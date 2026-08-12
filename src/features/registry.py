from dataclasses import dataclass
from typing import Callable

import pandas as pd


@dataclass(frozen=True)
class IndicatorDefinition:
    """
    Defines an indicator registered with AQTIP.
    """

    name: str
    role: str
    function: Callable[[pd.DataFrame], pd.DataFrame]


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
    ) -> None:
        """
        Register an indicator with AQTIP.
        """

        if any(
            indicator.name == name
            for indicator in self._indicators
        ):
            raise ValueError(
                f"Indicator '{name}' is already registered."
            )

        if not callable(function):
            raise TypeError(
                f"Function for '{name}' must be callable."
            )

        self._indicators.append(
            IndicatorDefinition(
                name=name,
                role=role,
                function=function,
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

    def definitions(self) -> list[IndicatorDefinition]:
        """
        Return all registered indicator definitions.
        """

        return list(self._indicators)