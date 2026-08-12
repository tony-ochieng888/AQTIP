from typing import Callable

import pandas as pd

from src.features.indicators import IndicatorLibrary


class IndicatorFactory:
    """
    Creates indicator functions for AQTIP.
    """

    @staticmethod
    def create(
        name: str,
        period: int,
    ) -> Callable[[pd.DataFrame], pd.DataFrame]:
        """
        Create an indicator function from its name and period.
        """

        if name.startswith("ATR"):
            return lambda df: IndicatorLibrary.add_atr(
                df,
                period=period,
            )

        if name.startswith("Kijun Sen"):
            return lambda df: IndicatorLibrary.add_kijun_sen(
                df,
                period=period,
            )

        raise ValueError(
            f"Unsupported indicator: {name}"
        )