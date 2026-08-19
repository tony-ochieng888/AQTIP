from dataclasses import dataclass
from typing import Callable

import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.indicators import IndicatorLibrary


@dataclass(frozen=True)
class IndicatorDefinition:
    """
    Complete executable definition of an AQTIP indicator.

    Combines:

    - The executable indicator function.
    - The immutable FeatureContract governing execution.
    """

    function: Callable[[pd.DataFrame], pd.DataFrame]
    contract: FeatureContract


class IndicatorFactory:
    """
    Creates complete, contract-bound indicator definitions.

    The factory is responsible for translating an indicator identity
    and period into:

        indicator function + complete FeatureContract

    Indicator-specific execution metadata belongs here rather than
    being duplicated by downstream components.
    """

    @staticmethod
    def create(
        name: str,
        period: int,
    ) -> IndicatorDefinition:
        """
        Create an executable indicator definition.

        Parameters
        ----------
        name:
            Human-readable indicator name.

        period:
            Positive integer lookback period.

        Returns
        -------
        IndicatorDefinition
            Executable function together with its complete contract.

        Raises
        ------
        TypeError
            If name or period has an invalid type.

        ValueError
            If the period is invalid or the indicator is unsupported.
        """

        if not isinstance(name, str):
            raise TypeError(
                "Indicator name must be a string."
            )

        if not name.strip():
            raise ValueError(
                "Indicator name cannot be empty."
            )

        if not isinstance(period, int):
            raise TypeError(
                "Indicator period must be an integer."
            )

        if isinstance(period, bool):
            raise TypeError(
                "Indicator period must be an integer, "
                "not boolean."
            )

        if period <= 0:
            raise ValueError(
                "Indicator period must be greater than zero."
            )

        if name.startswith("ATR"):
            function = lambda df: IndicatorLibrary.add_atr(
                df,
                period=period,
            )

            contract = FeatureContract(
                output_column=f"atr_{period}",
                required_columns=(
                    "high",
                    "low",
                    "close",
                ),
                warmup_period=period,
                causal=True,
            )

            return IndicatorDefinition(
                function=function,
                contract=contract,
            )

        if name.startswith("Kijun Sen"):
            function = lambda df: IndicatorLibrary.add_kijun_sen(
                df,
                period=period,
            )

            contract = FeatureContract(
                output_column=f"kijun_{period}",
                required_columns=(
                    "high",
                    "low",
                ),
                warmup_period=period,
                causal=True,
            )

            return IndicatorDefinition(
                function=function,
                contract=contract,
            )

        raise ValueError(
            f"Unsupported indicator: {name}"
        )