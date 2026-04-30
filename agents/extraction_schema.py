"""
Shared extraction schema used by all three extraction agents
(OpenAI, Llama on Modal, Qwen on Modal). Defines the structured output format
and the prompts, so comparisons are apples-to-apples.
"""
from pydantic import BaseModel, Field
from typing import Literal


class RiskOfBias(BaseModel):
    random_sequence_generation: Literal["low", "unclear", "high", "not_reported"]
    allocation_concealment: Literal["low", "unclear", "high", "not_reported"]
    performance_bias: Literal["low", "unclear", "high", "not_reported"]
    detection_bias: Literal["low", "unclear", "high", "not_reported"]
    attrition_bias: Literal["low", "unclear", "high", "not_reported"]
    reporting_bias: Literal["low", "unclear", "high", "not_reported"]


class StudyExtraction(BaseModel):
    first_author: str = Field(description="Last name of first author, e.g., 'Devinsky'")
    year: int = Field(description="Publication year")
    phase: str = Field(description="Trial phase, e.g., 'II', 'III', or 'N/A'")
    design: str = Field(description="Study design description")
    blinding: str = Field(description="Blinding approach, e.g., 'Double-blind'")
    duration_weeks: int | None = Field(default=None, description="Total study duration in weeks including baseline and treatment")
    maintenance_weeks_ge_12: bool = Field(description="True if maintenance phase is 12 weeks or longer")
    country_region: str = Field(description="Country or region of trial sites")
    n_total: int = Field(description="Total number of randomized participants")
    n_active: int = Field(description="Number randomized to active treatment arms (sum across all active arms if multiple)")
    n_placebo: int = Field(description="Number randomized to placebo")
    age_range_years: str = Field(description="Age eligibility range as a string, e.g., '2-18'")
    intervention: str = Field(description="Active intervention drug name")
    dose: str = Field(description="Dose(s) tested, e.g., '10, 20 mg/kg/day'")
    primary_efficacy_outcome: str = Field(description="Primary efficacy outcome as defined in the paper")
    outcomes_reported: list[str] = Field(description="List of outcome categories reported: seizure_response_50, seizure_freedom_100, adverse_events, treatment_discontinuation, cgic, pharmacokinetics, safety")
    risk_of_bias: RiskOfBias


# PROMPT VERSION: v3 (LOCKED 2026-04-28)
# This prompt was developed during r01 (Lattanzi/Dravet) and revised once
# after r02 (Ali/SGLT2-HF) to clarify two fields (age_range_years,
# maintenance_weeks_ge_12). It is FROZEN for r03/r04/r05, which serve
# as held-out validation.
# DO NOT MODIFY THIS PROMPT. If a new failure mode is identified on r03/r04/r05,
# document it as a finding in the paper rather than patching the prompt.
SYSTEM_PROMPT = """You are a data extraction specialist for systematic reviews of clinical trials.

Given the full text of a randomized controlled trial, extract structured study characteristics following PRISMA / Cochrane data extraction standards.

Rules:
1. Extract only information explicitly stated in the paper. Do not infer.
2. If a field cannot be determined from the text, use 'not_reported' for risk of bias fields and empty/zero/null for others as appropriate.
3. For 'n_active', sum the sample sizes of ALL active treatment arms if the trial has multiple doses or multiple active drugs.
4. For 'intervention', give only the generic drug name (e.g., 'Cannabidiol', 'Fenfluramine hydrochloride', 'Stiripentol', 'Soticlestat').
5. For age_range_years:
   - If the paper reports an explicit range (e.g., "ages 2 to 18 years"), output as "2-18" or "2 to 18".
   - If the paper reports only a lower bound (e.g., "adults aged 18 years or older", "patients ≥18 years", "men and women aged 40 or above"), output as ">=18" or ">=40" — preserve the lower-bound number with ">=" prefix.
   - If the paper reports only an upper bound (e.g., "children up to 12 years"), output as "<=12".
   - If the paper reports both lower and upper bounds, output as "X-Y".
   - If no age eligibility criterion is stated, output "not_reported".
6. For maintenance_weeks_ge_12 (boolean):
   - This field asks whether the trial's TREATMENT DURATION (or active follow-up duration) is at least 12 weeks total.
   - The paper does not need to use the word "maintenance" for this to be True. Look for any of: total trial duration, treatment duration, follow-up period, study duration, observation period, or median follow-up.
   - True = treatment or follow-up duration is at least 12 weeks (i.e., ≥84 days, ≥3 months).
   - False = treatment or follow-up duration is less than 12 weeks (e.g., 4-week studies, single-dose studies, hospitalization-only studies of <3 months).
   - If no duration information is stated, output False with a note in your reasoning.
7. For risk of bias, apply the Cochrane Risk of Bias tool criteria:
   - 'low' if the paper describes adequate methods (e.g., computer-generated randomization, matching placebo)
   - 'unclear' if the paper describes the domain but with insufficient detail to judge
   - 'high' if an actual bias source is evident
   - 'not_reported' only if the paper omits the domain entirely

Return the extraction as JSON matching the specified schema."""


USER_PROMPT_TEMPLATE = """Extract study characteristics from this randomized controlled trial.

TITLE: {title}
JOURNAL: {journal} ({year})
PMID: {pmid}

FULL TEXT:
{fulltext}
"""
