from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureContract:
    """
    Defines the execution contract for an AQTIP feature.

    The contract describes:
    - The expected output column.
    - The input columns required by the feature.
    - The number of rows required for warm-up.
    - Whether the feature must be causal.
    """

    output_column: str
    required_columns: tuple[str, ...]
    warmup_period: int
    causal: bool = True