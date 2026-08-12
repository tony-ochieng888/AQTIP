from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorConfig:
    """
    Configuration for an AQTIP technical indicator.
    """

    name: str
    role: str
    period: int
    enabled: bool = True