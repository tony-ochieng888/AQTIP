import pandas as pd

from src.features.indicator_config import IndicatorConfig
from src.features.indicator_factory import IndicatorFactory
from src.features.registry import IndicatorRegistry
from src.features.transforms import FeatureTransforms
from src.utils.logger import logger


class FeaturePipeline:
    """
    AQTIP feature engineering pipeline.

    Responsible for:
    - Generating base return features.
    - Creating configured indicator definitions.
    - Registering indicator definitions.
    - Executing registered indicators through the
      IndicatorRegistry runtime contract gate.
    """

    def __init__(self) -> None:
        self.registry = IndicatorRegistry()

        self.indicator_configs = [
            IndicatorConfig(
                name="ATR(14)",
                role="volatility",
                period=14,
                enabled=True,
            ),
            IndicatorConfig(
                name="Kijun Sen(26)",
                role="baseline",
                period=26,
                enabled=True,
            ),
        ]

        self._register_indicators()

    def _register_indicators(self) -> None:
        """
        Create and register all enabled indicators.

        Indicator-specific execution contracts are supplied by
        IndicatorFactory rather than being defined here.
        """

        for config in self.indicator_configs:
            if not config.enabled:
                continue

            definition = IndicatorFactory.create(
                name=config.name,
                period=config.period,
            )

            self.registry.register(
                name=config.name,
                role=config.role,
                function=definition.function,
                contract=definition.contract,
            )

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the complete feature engineering pipeline.

        Base features are generated first. All registered indicators
        are then executed through IndicatorRegistry.apply(), which
        serves as the runtime contract enforcement gate.
        """

        logger.info("Starting feature engineering pipeline...")

        logger.info("Generating returns feature...")
        df = FeatureTransforms.add_returns(df)

        logger.info("Generating log returns feature...")
        df = FeatureTransforms.add_log_returns(df)

        logger.info(
            "Executing registered indicators through runtime contracts..."
        )
        df = self.registry.apply(df)

        logger.info("Feature pipeline completed.")

        return df