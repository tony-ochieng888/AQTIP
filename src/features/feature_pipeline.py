import pandas as pd

from src.features.indicators import IndicatorLibrary
from src.features.registry import IndicatorRegistry
from src.features.transforms import FeatureTransforms
from src.utils.logger import logger


class FeaturePipeline:
    """
    Coordinates all feature generation for AQTIP.
    """

    def __init__(self):
        """
        Build the feature pipeline and register
        all indicators used by AQTIP.
        """

        self.registry = IndicatorRegistry()

        self.transforms = [
            FeatureTransforms.add_returns,
            FeatureTransforms.add_log_returns,
        ]

        self._register_indicators()

    def _register_indicators(self):
        """
        Register AQTIP indicators with the central registry.
        """

        self.registry.register(
            name="ATR(14)",
            function=lambda df: IndicatorLibrary.add_atr(
                df,
                period=14,
            ),
        )

        self.registry.register(
            name="Kijun Sen(26)",
            function=lambda df: IndicatorLibrary.add_kijun_sen(
                df,
                period=26,
            ),
        )

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute all feature transformations and indicators.
        """

        logger.info("Starting feature engineering pipeline...")

        # Apply basic feature transformations
        for transform in self.transforms:
            df = transform(df)

        # Apply registered indicators
        df = self.registry.apply(df)

        logger.info("Feature pipeline completed.")

        return df