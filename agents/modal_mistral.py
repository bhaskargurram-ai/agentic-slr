"""Modal deployment of Mistral Small 24B Instruct 2501 for JSON extraction via vLLM."""
import modal
import time as _time

APP_NAME = "slr-mistral-extractor"
MODEL_DIR = "/models/mistral-small-24b"
GPU_CONFIG = "H100:1"
VOLUME_NAME = "slr-mistral-weights"
CACHE_BUST = str(int(_time.time()))

image = (
    modal.Image.debian_slim(python_version="3.11")
    .run_commands(f"echo mistral-build-{CACHE_BUST}")
    .pip_install(
        "vllm==0.6.4.post1",
        "transformers==4.46.3",
        "huggingface_hub[hf_transfer]==0.26.2",
        "pydantic==2.9.2",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "VLLM_WORKER_MULTIPROC_METHOD": "spawn"})
)

app = modal.App(APP_NAME, image=image)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


@app.function(volumes={MODEL_DIR: volume}, secrets=[modal.Secret.from_name("huggingface-secret")], timeout=3600)
def download_model():
    from huggingface_hub import snapshot_download
    import os
    snapshot_download(
        "mistralai/Mistral-Small-24B-Instruct-2501",
        local_dir=MODEL_DIR,
        ignore_patterns=["*.pt", "*.bin", "consolidated*"],
        token=os.environ.get("HF_TOKEN"),
    )
    volume.commit()


@app.cls(gpu=GPU_CONFIG, volumes={MODEL_DIR: volume}, timeout=1800, scaledown_window=300)
class MistralExtractor:
    @modal.enter()
    def load_model(self):
        from vllm import LLM, SamplingParams
        self.llm = LLM(
            model=MODEL_DIR,
            tensor_parallel_size=1,
            max_model_len=20000,
            gpu_memory_utilization=0.95,
            enforce_eager=True,
        )
        self.SamplingParams = SamplingParams

    @modal.method()
    def extract(self, system_prompt: str, user_prompt: str, json_schema: dict) -> dict:
        import time, json
        full_system = (
            system_prompt
            + "\n\nRESPOND ONLY WITH A VALID JSON OBJECT MATCHING THIS SCHEMA. "
            + "NO MARKDOWN, NO PROSE, NO CODE FENCES.\n\nSCHEMA:\n"
            + json.dumps(json_schema, indent=2)
        )
        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_prompt},
        ]
        prompt_text = self._format(messages)
        params = self.SamplingParams(temperature=0.0, max_tokens=2048)
        t0 = time.time()
        outputs = self.llm.generate([prompt_text], params)
        latency = time.time() - t0
        text = outputs[0].outputs[0].text.strip()
        parsed, parse_error = self._parse_json(text)
        return {
            "extraction": parsed,
            "raw_output": text if parse_error else None,
            "parse_error": parse_error,
            "latency_seconds": round(latency, 2),
            "input_tokens": len(outputs[0].prompt_token_ids),
            "output_tokens": len(outputs[0].outputs[0].token_ids),
            "error": parse_error,
        }

    @staticmethod
    def _parse_json(text):
        import json, re
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        start = text.find("{")
        if start < 0:
            return None, f"No JSON object found. First 200 chars: {text[:200]}"
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{": depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1]), None
                    except json.JSONDecodeError as e:
                        return None, f"JSON decode error: {e}"
        return None, "Unterminated JSON object"

    @staticmethod
    def _format(messages):
        parts = ["<s>"]
        system = ""
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            elif m["role"] == "user":
                content = (system + "\n\n" + m["content"]) if system else m["content"]
                parts.append(f"[INST] {content} [/INST]")
                system = ""
        return "".join(parts)
