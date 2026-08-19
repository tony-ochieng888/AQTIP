import pandas as pd

from src.features.feature_runtime import FeatureRuntime
from src.features.indicator_config import IndicatorConfig
from src.features.indicator_factory import IndicatorFactory
from src.features.registry import IndicatorRegistry
from src.features.transforms import FeatureTransforms
from src.utils.logger import logger


class FeaturePipeline:
    """
    AQTIP feature engineering pipeline.

    Architectural responsibility:

    1. Generate configured base transforms.
    2. Resolve configured indicators through IndicatorFactory.
    3. Register indicator definitions with IndicatorRegistry.
    4. Execute every feature through FeatureRuntime.

    The pipeline does not implement feature-specific contract logic.
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
        """Create and register every enabled indicator."""

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
        Execute the complete AQTIP feature pipeline.

        Base transforms execute first.

        Registered indicators execute afterwards.

        Every feature-producing operation passes through the same
        FeatureRuntime contract-enforcement boundary.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "FeaturePipeline.run() requires a pandas DataFrame."
            )

        logger.info(
            "Starting feature engineering pipeline..."
        )

        result = df.copy(deep=True)

        # ----------------------------------------------------------
        # Base feature transforms
        # ----------------------------------------------------------

        for transform in FeatureTransforms.definitions():
            logger.info(
                "Executing base feature '%s' through runtime "
                "contract enforcement...",
                transform.name,
            )

            result = FeatureRuntime.execute(
                df=result,
                function=transform.function,
                contract=transform.contract,
                name=transform.name,
            )

        # ----------------------------------------------------------
        # Registered indicators
        # ----------------------------------------------------------

        logger.info(
            "Executing registered indicators through runtime "
            "contracts..."
        )

        result = self.registry.apply(result)

        logger.info(
            "Feature pipeline completed."
        )

        return result