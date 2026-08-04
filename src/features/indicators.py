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
    