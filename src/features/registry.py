from dataclasses import dataclass
from enum import Enum
from typing import Callable

import pandas as pd

class IndicatorRole(Enum):
    """
    Defines the strategic role of an indicator in AQTIP.
    """

    BASELINE = "baseline"
    CONFIRMATION_1 = "confirmation_1"
    CONFIRMATION_2 = "confirmation_2"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    EXIT = "exit"


@dataclass(frozen=True)
class IndicatorDefinition:
    """
    Defines an indicator registered with AQTIP.
    """

    name: str
    role: IndicatorRole
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
        role: IndicatorRole,
        function: Callable[[pd.DataFrame], pd.DataFrame],
    ) -> None:
        """
        Register an indicator.
        """
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
    