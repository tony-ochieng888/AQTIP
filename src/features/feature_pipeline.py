import pandas as pd

from src.features.indicator_config import IndicatorConfig
from src.features.indicator_factory import IndicatorFactory
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
        Register AQTIP indicators from configuration.
        """

        indicator_configs = [
            IndicatorConfig(
                name="ATR(14)",
                role="volatility",
                period=14,
            ),
            IndicatorConfig(
                name="Kijun Sen(26)",
                role="baseline",
                period=26,
            ),
        ]

        for config in indicator_configs:

            if not config.enabled:
                continue

            indicator_function = IndicatorFactory.create(
                name=config.name,
                period=config.period,
            )

            output_column = (
                "atr_14"
                if config.name.startswith("ATR")
                else "kijun_26"
                )

            self.registry.register(
                name=config.name,
                role=config.role,
                function=indicator_function,
                output_column=output_column,
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