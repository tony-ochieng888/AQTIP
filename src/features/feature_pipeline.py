import pandas as pd

from src.features.indicators import IndicatorLibrary
from src.features.volatility import VolatilityIndicators

from src.features.transforms import FeatureTransforms
from src.utils.logger import logger


class FeaturePipeline:
    """
    Coordinates all feature generation.
    """

    def __init__(self):
        """
        Register all feature transformations
        in execution order.
        """

        self.transforms = [
            FeatureTransforms.add_returns,
            FeatureTransforms.add_log_returns,
            lambda df: VolatilityIndicators.add_atr(df, period=14),
            lambda df: IndicatorLibrary.add_kijun_sen(df, period=26),
        ]

    def run(self, df: pd.DataFrame) -> pd.DataFrame:

        logger.info("Starting feature engineering pipeline...")

        for transform in self.transforms:
            df = transform(df)

        logger.info("Feature pipeline completed.")

        return df