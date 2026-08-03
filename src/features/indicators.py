import pandas as pd

from src.features.schema import FeatureColumns
from src.utils.logger import logger


class IndicatorLibrary:
    """
    Technical analysis indicators used by AQTIP.
    """

    @staticmethod
    def add_sma_20(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds the 20-period Simple Moving Average.
        """

        logger.info("Generating SMA(20)...")

        df = df.copy()

        df[FeatureColumns.SMA_20] = (
            df[FeatureColumns.CLOSE]
            .rolling(window=20)
            .mean()
        )

        return df