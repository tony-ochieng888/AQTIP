import pandas as pd

from src.features.feature_pipeline_integrity import (
    FeaturePipelineIntegrity,
)
from src.features.feature_runtime import FeatureRuntime
from src.features.indicator_config import IndicatorConfig
from src.features.indicator_factory import IndicatorFactory
from src.features.feature_registry import FeatureRegistry
from src.features.transforms import FeatureTransforms
from src.utils.logger import logger


class FeaturePipeline:
    """
    AQTIP feature engineering pipeline.

    Architectural responsibility:

    1. Capture the original input schema.
    2. Generate configured base transforms.
    3. Resolve configured indicators through IndicatorFactory.
    4. Register feature definitions with FeatureRegistry.
    5. Execute every feature through FeatureRuntime.
    6. Validate complete pipeline-level integrity.

    The pipeline remains the orchestration layer.

    FeatureRuntime owns individual feature contract enforcement.

    FeaturePipelineIntegrity owns complete pipeline integrity
    enforcement.
    """

    def __init__(self) -> None:
        self.registry = FeatureRegistry()

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
        Create and register every enabled indicator.
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

    def run(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Execute the complete AQTIP feature pipeline.

        Pipeline execution order:

        1. Capture original input schema.
        2. Capture original input values.
        3. Determine expected feature-output declarations.
        4. Execute base feature transforms through FeatureRuntime.
        5. Execute registered indicators through FeatureRuntime.
        6. Validate complete pipeline-level integrity.
        7. Return the feature-enriched DataFrame.

        FeaturePipeline remains an orchestration layer.

        FeatureRuntime is responsible for individual feature
        execution contracts.

        FeaturePipelineIntegrity is responsible for complete
        pipeline integrity.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "FeaturePipeline.run() requires a pandas DataFrame."
            )

        logger.info(
            "Starting feature engineering pipeline..."
        )

        # ----------------------------------------------------------
        # Capture original pipeline input
        # ----------------------------------------------------------

        original_input = df.copy(deep=True)

        input_schema = (
            FeaturePipelineIntegrity.capture_input(df)
        )

        # ----------------------------------------------------------
        # Determine expected feature outputs
        # ----------------------------------------------------------

        transform_outputs = tuple(
            transform.contract.output_column
            for transform in FeatureTransforms.definitions()
        )

        indicator_outputs = tuple(
            self.registry.output_columns()
        )

        expected_outputs = (
            transform_outputs
            + indicator_outputs
        )

        # ----------------------------------------------------------
        # Execute features
        # ----------------------------------------------------------

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
        # Registered features
        # ----------------------------------------------------------

        logger.info(
            "Executing registered features through runtime "
            "contracts..."
        )

        result = self.registry.apply(result)

        # ----------------------------------------------------------
        # Pipeline-level integrity validation
        # ----------------------------------------------------------

        logger.info(
            "Validating complete feature pipeline integrity..."
        )

        FeaturePipelineIntegrity.validate_feature_outputs(
            input_schema=input_schema,
            output_df=result,
            expected_outputs=expected_outputs,
        )

        FeaturePipelineIntegrity.validate_input_integrity(
            original_df=original_input,
            output_df=result,
        )

        logger.info(
            "Feature pipeline integrity validation PASSED."
        )

        logger.info(
            "Feature pipeline completed."
        )

        return result
