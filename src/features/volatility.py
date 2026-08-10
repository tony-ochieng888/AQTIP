import pandas as pd

from src.features.schema import FeatureColumns
from src.utils.logger import logger


class VolatilityIndicators:
    """
    Volatility-related indicators used by AQTIP.
    """

    @staticmethod
    def add_atr(df, period=14):
        """
        Adds the Average True Range (ATR)
        for the specified period.
        """

        logger.info(f"Generating ATR({period})...")

        df = df.copy()

        previous_close = df[FeatureColumns.CLOSE].shift(1)

        high_low = df["high"] - df["low"]

        high_prev_close = (
            df["high"] - previous_close
        ).abs()

        low_prev_close = (
            df["low"] - previous_close
        ).abs()

        true_range = pd.concat(
            [
                high_low,
                high_prev_close,
                low_prev_close,
            ],
            axis=1,
        ).max(axis=1)

        column_name = f"atr_{period}"

        df[column_name] = (
            true_range
            .rolling(window=period)
            .mean()
        )

        return df