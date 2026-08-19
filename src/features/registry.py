from dataclasses import dataclass
from typing import Callable

import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.feature_runtime import FeatureRuntime


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
    AQTIP indicator registry.

    The registry owns indicator definitions and registration policy.

    Runtime contract enforcement is delegated to FeatureRuntime.

    Architectural responsibilities:

    IndicatorRegistry
        Registration, discovery, duplicate protection.

    FeatureRuntime
        Runtime contract enforcement.

    FeaturePipeline
        Execution orchestration.
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
            raise ValueError(
                "Indicator name cannot be empty."
            )

        if not role.strip():
            raise ValueError(
                "Indicator role cannot be empty."
            )

        if not callable(function):
            raise TypeError(
                f"Function for '{name}' must be callable."
            )

        if not isinstance(contract, FeatureContract):
            raise TypeError(
                f"Contract for '{name}' must be a FeatureContract."
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
        """Return a snapshot of registered indicator definitions."""

        return list(self._indicators)

    def names(self) -> list[str]:
        """Return registered indicator names."""

        return [
            indicator.name
            for indicator in self._indicators
        ]

    def roles(self) -> list[str]:
        """Return registered indicator roles."""

        return [
            indicator.role
            for indicator in self._indicators
        ]

    def output_columns(self) -> list[str]:
        """Return registered feature output columns."""

        return [
            indicator.contract.output_column
            for indicator in self._indicators
        ]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute every registered indicator through FeatureRuntime.
        """

        result = df.copy(deep=True)

        for indicator in self._indicators:
            result = FeatureRuntime.execute(
                df=result,
                function=indicator.function,
                contract=indicator.contract,
                name=indicator.name,
            )

        return result