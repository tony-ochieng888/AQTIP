import numpy as np
import pandas as pd

from src.features.schema import FeatureColumns
from src.utils.logger import logger


class FeatureTransforms:
    """
    General mathematical transformations
    applied to market datasets.
    """

    @staticmethod
    def add_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds percentage returns.
        """

        logger.info("Generating returns feature...")

        df = df.copy()

        df[FeatureColumns.RETURNS] = (
            df[FeatureColumns.CLOSE]
            .pct_change()
        )

        return df

    @staticmethod
    def add_log_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds logarithmic returns.
        """
        logger.info("Generating log returns feature...")
        df = df.copy()
        df[FeatureColumns.LOG_RETURNS] = np.log(
            df[FeatureColumns.CLOSE] /
            df[FeatureColumns.CLOSE].shift(1)
            )
        return df