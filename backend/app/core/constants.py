"""ICP thresholds, exclusions, and scoring weights.

Single source of truth so sales can tune "why these 10" and re-score fast,
without hunting through pipeline code.
"""

# --- Ideal Customer Profile (hard filters) ---
REGIONS = ["BE", "NL"]
MIN_EMPLOYEES = 100
MAX_EMPLOYEES = 500

# Project value sits between these; EBITDA must comfortably cover it.
PROJECT_VALUE_MIN = 150_000
PROJECT_VALUE_MAX = 500_000
# Project value must be < this fraction of annual EBITDA.
MAX_PROJECT_TO_EBITDA_RATIO = 0.10

# Focus sectors by leading NACE digits (Finance, Insurance, Prof. services, Industry).
FOCUS_NACE_PREFIXES = ["64", "65", "66", "69", "70", "78"]

# --- Exclusions (hard) ---
# Healthcare (86), and a flag for too-mature/enterprise handled in filter.py.
EXCLUDED_NACE_PREFIXES = ["86", "51"]  # 86 = health, 51 = air transport (aviation)

# --- Scoring weights (sum need not be 1; score is normalised) ---
SCORE_WEIGHTS = {
    "buyer_intent": 0.30,      # open IT vacancies, growth signals
    "impact_potential": 0.25,  # small IT team + legacy tech = high AI impact
    "financial_fit": 0.20,     # EBITDA headroom vs project value
    "sector_fit": 0.10,        # in a focus sector with strong reference cases
    "warm_connection": 0.15,   # 2nd/3rd-degree tie to the sales team
}
