import pandas as pd

from src.features.schema import FeatureColumns
from src.utils.logger import logger


class IndicatorLibrary:
    """
    Technical analysis indicators used by AQTIP.
    """
    @staticmethod
    def add_sma(df, period=20):
        """
        Adds a Simple Moving Average (SMA)
        for the specified period.
        """
        logger.info(f"Generating SMA({period})...")
        df = df.copy()
        column_name = f"sma_{period}"
        df[column_name] = (
            df[FeatureColumns.CLOSE]
            .rolling(window=period)
            .mean()
            )
        return df

    
    @staticmethod
    def add_ema(df, period=20):
        """
        Adds an Exponential Moving Average (EMA)
        for the specified period.
        """
        logger.info(f"Generating EMA({period})...")
        df = df.copy()
        column_name = f"ema_{period}"
        df[column_name] = (
            df[FeatureColumns.CLOSE]
            .ewm(span=period, adjust=False)
            .mean()
            )
        return df
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
    @staticmethod
    def add_kijun_sen(df, period=26):
        """
        Adds the Ichimoku Kijun Sen (Base Line).

        Kijun Sen is calculated as the midpoint
        between the highest high and lowest low
        over the specified period.
        """
        logger.info(f"Generating Kijun Sen({period})...")

        df = df.copy()

        highest_high = (
            df[FeatureColumns.HIGH]
            .rolling(window=period)
            .max()
        )

        lowest_low = (
            df[FeatureColumns.LOW]
            .rolling(window=period)
            .min()
        )

        df[FeatureColumns.KIJUN_26] = (
            highest_high + lowest_low
        ) / 2

        return df
    