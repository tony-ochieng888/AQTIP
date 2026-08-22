from typing import Callable

import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.feature_definition import FeatureDefinition
from src.features.feature_runtime import FeatureRuntime


class FeatureRegistry:
    """
    Unified AQTIP feature registry.

    The registry owns feature definitions and registration policy.

    It intentionally treats transformations and indicators uniformly.

    Architectural responsibilities:

    FeatureRegistry
        Registration, discovery, duplicate protection,
        and feature execution.

    FeatureRuntime
        Runtime contract enforcement.

    FeaturePipeline
        Execution orchestration.
    """

    def __init__(self) -> None:
        self._features: list[FeatureDefinition] = []

    def register(
        self,
        name: str,
        role: str,
        function: Callable[[pd.DataFrame], pd.DataFrame],
        contract: FeatureContract,
    ) -> None:
        """
        Register a feature and its execution contract.
        """

        definition = FeatureDefinition(
            name=name,
            role=role,
            function=function,
            contract=contract,
        )

        if any(
            feature.name == definition.name
            for feature in self._features
        ):
            raise ValueError(
                f"Feature '{name}' is already registered."
            )

        if any(
            feature.contract.output_column
            == definition.contract.output_column
            for feature in self._features
        ):
            raise ValueError(
                f"Output column '{contract.output_column}' "
                "is already registered."
            )

        self._features.append(definition)

    def definitions(self) -> list[FeatureDefinition]:
        """
        Return a snapshot of registered feature definitions.
        """

        return list(self._features)

    def names(self) -> list[str]:
        """Return registered feature names."""

        return [
            feature.name
            for feature in self._features
        ]

    def roles(self) -> list[str]:
        """Return registered feature roles."""

        return [
            feature.role
            for feature in self._features
        ]

    def output_columns(self) -> list[str]:
        """Return registered feature output columns."""

        return [
            feature.contract.output_column
            for feature in self._features
        ]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute every registered feature through FeatureRuntime.
        """

        result = df.copy(deep=True)

        for feature in self._features:
            result = FeatureRuntime.execute(
                df=result,
                function=feature.function,
                contract=feature.contract,
                name=feature.name,
            )

        return result