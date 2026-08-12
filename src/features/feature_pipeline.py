import pandas as pd

from src.features.indicator_config import IndicatorConfig
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

            if config.name.startswith("ATR"):
                self.registry.register(
                    name=config.name,
                    role=config.role,
                    function=lambda df, period=config.period:
                        IndicatorLibrary.add_atr(
                            df,
                            period=period,
                        ),
                )

            elif config.name.startswith("Kijun Sen"):
                self.registry.register(
                    name=config.name,
                    role=config.role,
                    function=lambda df, period=config.period:
                        IndicatorLibrary.add_kijun_sen(
                            df,
                            period=period,
                        ),
                )

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute all feature transformations and indicators.
        """

        logger.info("Starting feature engineering pipeline...")

        for transform in self.transforms:
            df = transform(df)

        df = self.registry.apply(df)

        logger.info("Feature pipeline completed.")

        return df