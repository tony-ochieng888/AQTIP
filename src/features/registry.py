from dataclasses import dataclass
from typing import Callable

import pandas as pd
from src.features.feature_contract import FeatureContract


@dataclass(frozen=True)
class IndicatorDefinition:
    """
    Defines an indicator registered with AQTIP.
    """

    name: str
    role: str
    function: Callable[[pd.DataFrame], pd.DataFrame]
    contract: FeatureContract


class IndicatorRegistry:
    """
    Central registry for AQTIP technical indicators.
    """

    def __init__(self):
        self._indicators: list[IndicatorDefinition] = []

    def register(
        self,
        name: str,
        role: str,
        function: Callable[[pd.DataFrame], pd.DataFrame],
        contract: FeatureContract,
    ) -> None:
        """
        Register an indicator.
        """

        # Validate metadata
        if not name.strip():
            raise ValueError(
                "Indicator name cannot be empty."
            )

        if not role.strip():
            raise ValueError(
                "Indicator role cannot be empty."
            )

        if not contract.output_column.strip():
            raise ValueError(
                "Indicator output column cannot be empty."
                )

        # Validate callable
        if not callable(function):
            raise TypeError(
                f"Function for '{name}' must be callable."
            )

        # Prevent duplicate indicator names
        if any(
            indicator.name == name
            for indicator in self._indicators
        ):
            raise ValueError(
                f"Indicator '{name}' is already registered."
            )

        # Prevent duplicate output columns
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
                contract = contract,
            )
        )

    def apply(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Apply all registered indicators in registration order.
        """

        for indicator in self._indicators:
            df = indicator.function(df)

        return df

    def names(self) -> list[str]:
        """
        Return names of all registered indicators.
        """

        return [
            indicator.name
            for indicator in self._indicators
        ]

    def roles(self) -> list[str]:
        """
        Return roles of all registered indicators.
        """

        return [
            indicator.role
            for indicator in self._indicators
        ]

    def output_columns(self) -> list[str]:
        """
        Return output columns of all registered indicators.
        """

        return [
            indicator.contract.output_column
            for indicator in self._indicators
            ]

    def definitions(self) -> list[IndicatorDefinition]:
        """
        Return all registered indicator definitions.
        """

        return list(self._indicators)