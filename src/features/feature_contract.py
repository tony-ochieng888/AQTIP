from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureContract:
    """
    Immutable execution contract for an AQTIP feature.

    A FeatureContract declares the minimum guarantees required from
    an executable feature before the feature may participate in the
    AQTIP pipeline.

    Contract dimensions:

    - output_column:
        Column the feature must generate.

    - required_columns:
        Input columns the feature requires.

    - warmup_period:
        Number of observations required before the first valid
        feature value can exist.

    - causal:
        Whether the feature must be demonstrably causal and free
        from future-data dependence.
    """

    output_column: str
    required_columns: tuple[str, ...]
    warmup_period: int
    causal: bool = True

    def __post_init__(self) -> None:
        """
        Validate the contract immediately after construction.

        This prevents malformed contracts from entering the
        IndicatorFactory, FeatureRegistry, or FeaturePipeline.
        """

        if not isinstance(self.output_column, str):
            raise TypeError(
                "Feature contract output_column must be a string."
            )

        if not self.output_column.strip():
            raise ValueError(
                "Feature contract output_column cannot be empty."
            )

        if not isinstance(self.required_columns, tuple):
            raise TypeError(
                "Feature contract required_columns must be a tuple."
            )

        if not self.required_columns:
            raise ValueError(
                "Feature contract must declare at least one "
                "required input column."
            )

        if any(
            not isinstance(column, str)
            for column in self.required_columns
        ):
            raise TypeError(
                "All FeatureContract required_columns must be strings."
            )

        if any(
            not column.strip()
            for column in self.required_columns
        ):
            raise ValueError(
                "FeatureContract required_columns cannot contain "
                "empty column names."
            )

        if len(set(self.required_columns)) != len(
            self.required_columns
        ):
            raise ValueError(
                "FeatureContract required_columns cannot contain "
                "duplicates."
            )

        if not isinstance(self.warmup_period, int):
            raise TypeError(
                "Feature contract warmup_period must be an integer."
            )

        if isinstance(self.warmup_period, bool):
            raise TypeError(
                "Feature contract warmup_period must be an integer, "
                "not boolean."
            )

        if self.warmup_period <= 0:
            raise ValueError(
                "Feature contract warmup_period must be greater "
                "than zero."
            )

        if not isinstance(self.causal, bool):
            raise TypeError(
                "Feature contract causal must be a boolean."
            )