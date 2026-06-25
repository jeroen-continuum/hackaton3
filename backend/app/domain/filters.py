"""ICP filter configuration — the runtime-adjustable customer profile.

Defaults come from core/constants.py (the requirement values), but every field
can be overridden or disabled by the caller (CLI, API, frontend) so users can
widen, narrow, or switch off any filter.
"""
from dataclasses import dataclass, field
from typing import Optional

from app.core import constants


@dataclass(frozen=True)
class IcpFilter:
    """Adjustable Ideal Customer Profile applied at selection + filtering time."""

    regions: list[str] = field(default_factory=lambda: list(constants.REGIONS))
    # Leading NACE digits a company MUST match (empty = no include restriction).
    nace_include_prefixes: list[str] = field(
        default_factory=lambda: list(constants.FOCUS_NACE_PREFIXES)
    )
    # Leading NACE digits that disqualify a company.
    nace_exclude_prefixes: list[str] = field(
        default_factory=lambda: list(constants.EXCLUDED_NACE_PREFIXES)
    )
    min_employees: int = constants.MIN_EMPLOYEES
    max_employees: int = constants.MAX_EMPLOYEES
    project_value_min: float = constants.PROJECT_VALUE_MIN
    max_project_to_ebitda_ratio: float = constants.MAX_PROJECT_TO_EBITDA_RATIO
    # Toggles — disable the financial-data-dependent filters entirely.
    apply_size: bool = True
    apply_financial: bool = True
    # Area filter — keep only companies within `radius_km` of (center_lat, center_lon).
    # All None (the default) = no geographic restriction.
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    radius_km: Optional[float] = None

    @property
    def has_area(self) -> bool:
        """True when a usable center + positive radius are set."""
        return (
            self.center_lat is not None
            and self.center_lon is not None
            and self.radius_km is not None
            and self.radius_km > 0
        )

    @classmethod
    def default(cls) -> "IcpFilter":
        """The requirement ICP — all filters on, values from constants."""
        return cls()
