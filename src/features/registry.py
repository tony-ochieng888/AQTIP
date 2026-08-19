from dataclasses import dataclass
from typing import Callable

import pandas as pd

from src.features.feature_contract import FeatureContract


@dataclass(frozen=True)
class IndicatorDefinition:
    """
    Complete registered definition of an AQTIP indicator.
    """

    name: str
    role: str
    function: Callable[[pd.DataFrame], pd.DataFrame]
    contract: FeatureContract


class IndicatorRegistry:
    """
    AQTIP indicator registry and runtime execution gate.

    The registry owns indicator definitions and ensures that every
    registered feature satisfies its FeatureContract before the
    resulting DataFrame is accepted by the pipeline.

    Runtime guarantees include:

    - Required input columns.
    - Expected output column.
    - Row-count preservation.
    - Input immutability.
    - Input index preservation.
    - Warm-up behavior.
    - Causal / no-look-ahead behavior.
    """

    def __init__(self) -> None:
        self._indicators: list[IndicatorDefinition] = []

    def register(
        self,
        name: str,
        role: str,
        function: Callable[[pd.DataFrame], pd.DataFrame],
        contract: FeatureContract,
    ) -> None:
        """Register an indicator and its execution contract."""

        if not name.strip():
            raise ValueError("Indicator name cannot be empty.")

        if not role.strip():
            raise ValueError("Indicator role cannot be empty.")

        if not callable(function):
            raise TypeError(
                f"Function for '{name}' must be callable."
            )

        if not isinstance(contract, FeatureContract):
            raise TypeError(
                f"Contract for '{name}' must be a FeatureContract."
            )

        if not contract.output_column.strip():
            raise ValueError(
                "Indicator output column cannot be empty."
            )

        if contract.warmup_period <= 0:
            raise ValueError(
                "Indicator warm-up period must be greater than zero."
            )

        if not isinstance(contract.causal, bool):
            raise TypeError(
                f"Causal contract for '{name}' must be a boolean."
            )

        if any(
            indicator.name == name
            for indicator in self._indicators
        ):
            raise ValueError(
                f"Indicator '{name}' is already registered."
            )

        if any(
            indicator.contract.output_column == contract.output_column
            for indicator in self._indicators
        ):
            raise ValueError(
                f"Output column '{contract.output_column}' "
                "is already registered."
            )

        self._indicators.append(
            IndicatorDefinition(
                name=name,
                role=role,
                function=function,
                contract=contract,
            )
        )

    def definitions(self) -> list[IndicatorDefinition]:
        """Return a snapshot of registered indicator definitions."""

        return list(self._indicators)

    def names(self) -> list[str]:
        """Return registered indicator names."""

        return [indicator.name for indicator in self._indicators]

    def roles(self) -> list[str]:
        """Return registered indicator roles."""

        return [indicator.role for indicator in self._indicators]

    def output_columns(self) -> list[str]:
        """Return registered feature output columns."""

        return [
            indicator.contract.output_column
            for indicator in self._indicators
        ]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute every registered indicator through the runtime
        contract enforcement gate.
        """

        result = df.copy(deep=True)

        for indicator in self._indicators:
            result = self._apply_indicator(result, indicator)

        return result

    def _apply_indicator(
        self,
        df: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> pd.DataFrame:
        """Execute one indicator and enforce its FeatureContract."""

        contract = indicator.contract

        self._validate_required_columns(df, indicator)

        input_snapshot = df.copy(deep=True)
        input_row_count = len(df)

        try:
            generated = indicator.function(df.copy(deep=True))
        except Exception as exc:
            raise RuntimeError(
                f"Indicator '{indicator.name}' execution failed: {exc}"
            ) from exc

        if not isinstance(generated, pd.DataFrame):
            raise TypeError(
                f"Indicator '{indicator.name}' must return a "
                "pandas DataFrame."
            )

        if len(generated) != input_row_count:
            raise ValueError(
                f"Indicator '{indicator.name}' violated row-count "
                f"preservation: expected {input_row_count}, "
                f"got {len(generated)}."
            )

        self._validate_input_immutability(
            input_snapshot,
            df,
            indicator,
        )
        self._validate_input_index(df, generated, indicator)

        output_column = contract.output_column

        if output_column not in generated.columns:
            raise ValueError(
                f"Indicator '{indicator.name}' did not generate "
                f"expected output column '{output_column}'."
            )

        self._validate_warmup(generated, indicator)

        if contract.causal:
            self._validate_causality(df, generated, indicator)

        return generated

    @staticmethod
    def _validate_required_columns(
        df: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> None:
        """Ensure every input column declared by the contract exists."""

        missing = [
            column
            for column in indicator.contract.required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Indicator '{indicator.name}' is missing required "
                f"input columns: {missing}"
            )

    @staticmethod
    def _validate_input_immutability(
        before: pd.DataFrame,
        after: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> None:
        """Ensure the supplied DataFrame was not mutated in-place."""

        if not before.equals(after):
            raise ValueError(
                f"Indicator '{indicator.name}' mutated its input "
                "DataFrame."
            )

    @staticmethod
    def _validate_input_index(
        original: pd.DataFrame,
        generated: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> None:
        """Ensure the indicator preserves the input index exactly."""

        if not generated.index.equals(original.index):
            raise ValueError(
                f"Indicator '{indicator.name}' changed the input "
                "DataFrame index."
            )

    @staticmethod
    def _validate_warmup(
        generated: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> None:
        """
        Validate the declared warm-up boundary.

        For a warm-up period N, rows 0 through N-2 must be NaN.
        The first valid observation is therefore expected at index N-1.
        Values must also exist from that boundary onward.
        """

        output_column = indicator.contract.output_column
        warmup_period = indicator.contract.warmup_period
        series = generated[output_column]

        warmup_rows = min(warmup_period - 1, len(series))

        if (
            warmup_rows > 0
            and series.iloc[:warmup_rows].notna().any()
        ):
            raise ValueError(
                f"Indicator '{indicator.name}' violated warm-up "
                f"behavior: expected the first {warmup_rows} rows "
                f"of '{output_column}' to be NaN."
            )

        if len(series) >= warmup_period:
            if series.iloc[warmup_period - 1:].isna().any():
                raise ValueError(
                    f"Indicator '{indicator.name}' violated warm-up "
                    f"behavior: '{output_column}' contains NaN values "
                    "after the warm-up boundary."
                )

    @staticmethod
    def _validate_causality(
        original: pd.DataFrame,
        generated: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> None:
        """
        Detect accidental future-data dependence.

        The indicator is executed twice. The second execution mutates
        only the future portion of required numeric inputs. Values before
        that mutation point must remain identical.
        """

        output_column = indicator.contract.output_column

        if len(original) < 3:
            return

        mutation_point = len(original) // 2

        if mutation_point <= 0:
            return

        mutated = original.copy(deep=True)

        for column in indicator.contract.required_columns:
            if pd.api.types.is_numeric_dtype(mutated[column]):
                future_index = mutated.index[mutation_point:]

                mutated.loc[future_index, column] = (
                    mutated.loc[future_index, column] + 1_000_000
                )

        try:
            mutated_generated = indicator.function(
                mutated.copy(deep=True)
            )
        except Exception as exc:
            raise RuntimeError(
                f"Indicator '{indicator.name}' causality validation "
                f"failed during re-execution: {exc}"
            ) from exc

        if not isinstance(mutated_generated, pd.DataFrame):
            raise TypeError(
                f"Indicator '{indicator.name}' must return a "
                "pandas DataFrame during causality validation."
            )

        if len(mutated_generated) != len(original):
            raise ValueError(
                f"Indicator '{indicator.name}' violated row-count "
                "preservation during causality validation."
            )

        if not mutated_generated.index.equals(original.index):
            raise ValueError(
                f"Indicator '{indicator.name}' changed the input "
                "DataFrame index during causality validation."
            )

        original_values = generated[output_column].iloc[:mutation_point]
        mutated_values = mutated_generated[
            output_column
        ].iloc[:mutation_point]

        if not original_values.equals(mutated_values):
            raise ValueError(
                f"Indicator '{indicator.name}' violated causal "
                "execution: feature values before the future "
                "mutation point changed."
            )