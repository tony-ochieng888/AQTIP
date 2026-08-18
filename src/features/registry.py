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
        """
        Register an indicator and its execution contract.
        """

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

        if any(
            indicator.name == name
            for indicator in self._indicators
        ):
            raise ValueError(
                f"Indicator '{name}' is already registered."
            )

        if any(
            indicator.contract.output_column
            == contract.output_column
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
        """
        Return a snapshot of registered indicator definitions.
        """
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
            result = self._apply_indicator(
                result,
                indicator,
            )

        return result

    def _apply_indicator(
        self,
        df: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> pd.DataFrame:
        """
        Execute one indicator and enforce its FeatureContract.
        """

        contract = indicator.contract

        self._validate_required_columns(
            df,
            indicator,
        )

        input_snapshot = df.copy(deep=True)
        input_row_count = len(df)

        try:
            generated = indicator.function(
                df.copy(deep=True)
            )
        except Exception as exc:
            raise RuntimeError(
                f"Indicator '{indicator.name}' execution failed: "
                f"{exc}"
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

        output_column = contract.output_column

        if output_column not in generated.columns:
            raise ValueError(
                f"Indicator '{indicator.name}' did not generate "
                f"expected output column '{output_column}'."
            )

        self._validate_warmup(
            generated,
            indicator,
        )

        return generated

    @staticmethod
    def _validate_required_columns(
        df: pd.DataFrame,
        indicator: IndicatorDefinition,
    ) -> None:
        """
        Ensure every input column declared by the contract exists.
        """

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
        """
        Ensure the input DataFrame supplied to the indicator was not
        mutated in-place.
        """

        if not before.equals(after):
            raise ValueError(
                f"Indicator '{indicator.name}' mutated its input "
                "DataFrame."
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

        warmup_rows = min(
            warmup_period - 1,
            len(series),
        )

        if warmup_rows > 0 and series.iloc[:warmup_rows].notna().any():
            raise ValueError(
                f"Indicator '{indicator.name}' violated warm-up "
                f"behavior: expected the first "
                f"{warmup_rows} rows of '{output_column}' to be NaN."
            )

        if len(series) >= warmup_period:
            if series.iloc[warmup_period - 1 :].isna().any():
                raise ValueError(
                    f"Indicator '{indicator.name}' violated warm-up "
                    f"behavior: '{output_column}' contains NaN values "
                    f"after the warm-up boundary."
                )