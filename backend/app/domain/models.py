"""Pure domain value objects — no I/O, no framework imports."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class CompanyProfile:
    """Minimal company identity from the KBO pond."""
    enterprise_number: str
    name: str
    region: str = "BE"
    nace_code: Optional[str] = None
    sector: Optional[str] = None
    website: Optional[str] = None
    municipality: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass(frozen=True)
class Financials:
    """Financial metrics from NBB."""
    employees: Optional[int] = None
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    fiscal_year: Optional[int] = None


@dataclass(frozen=True)
class Signals:
    """Normalised scoring inputs, all in [0.0, 1.0]."""
    buyer_intent: float = 0.0
    impact_potential: float = 0.0
    financial_fit: float = 0.0
    sector_fit: float = 0.0
    warm_connection: float = 0.0

    def __post_init__(self):
        for field_name in ("buyer_intent", "impact_potential",
                           "financial_fit", "sector_fit", "warm_connection"):
            v = getattr(self, field_name)
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{field_name} must be in [0, 1], got {v}")


@dataclass(frozen=True)
class ScoreResult:
    """Output from a ScoringStrategy."""
    total: float
    breakdown: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    """Output from a FilterPolicy."""
    passes: bool
    reason: Optional[str] = None
