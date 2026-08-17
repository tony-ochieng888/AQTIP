import pandas as pd

from src.features.feature_contract import FeatureContract
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
    - Registering configured indicators.
    - Executing registered indicators.
    """

    def __init__(self):
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
        Register all enabled indicators with their feature contracts.
        """

        for config in self.indicator_configs:
            if not config.enabled:
                continue

            indicator_function = IndicatorFactory.create(
                name=config.name,
                period=config.period,
            )

            if config.name.startswith("ATR"):
                contract = FeatureContract(
                    output_column="atr_14",
                    required_columns=("high", "low", "close"),
                    warmup_period=config.period,
                )

            elif config.name.startswith("Kijun Sen"):
                contract = FeatureContract(
                    output_column="kijun_26",
                    required_columns=("high", "low"),
                    warmup_period=config.period,
                )

            else:
                raise ValueError(
                    f"No feature contract defined for indicator: "
                    f"{config.name}"
                )

            self.registry.register(
                name=config.name,
                role=config.role,
                function=indicator_function,
                contract=contract,
            )

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the complete feature engineering pipeline.
        """

        logger.info("Starting feature engineering pipeline...")

        logger.info("Generating returns feature...")
        df = FeatureTransforms.add_returns(df)

        logger.info("Generating log returns feature...")
        df = FeatureTransforms.add_log_returns(df)

        for definition in self.registry.definitions():
            logger.info(
                "Generating %s...",
                definition.name,
            )

            df = definition.function(df)

        logger.info("Feature pipeline completed.")

        return df