from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureContract:
    """
    Defines the execution contract for an AQTIP feature.
    """

    output_column: str
    required_columns: tuple[str, ...]
    warmup_period: int