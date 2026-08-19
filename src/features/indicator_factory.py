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
    - The feature contract describing its output requirements.
    """

    function: Callable[[pd.DataFrame], pd.DataFrame]
    contract: FeatureContract


class IndicatorFactory:
    """
    Creates complete indicator definitions for AQTIP.

    The factory owns indicator-specific execution metadata,
    including:

    - Output column.
    - Required input columns.
    - Warm-up period.
    - Executable indicator function.
    """

    @staticmethod
    def create(
        name: str,
        period: int,
    ) -> IndicatorDefinition:
        """
        Create an indicator definition from its name and period.

        Parameters
        ----------
        name:
            Human-readable indicator name.

        period:
            Lookback period used by the indicator.

        Returns
        -------
        IndicatorDefinition
            Executable indicator function plus its feature contract.

        Raises
        ------
        ValueError
            If the indicator is not supported.
        """

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
                required_columns=("high", "low", "close"),
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
                required_columns=("high", "low"),
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