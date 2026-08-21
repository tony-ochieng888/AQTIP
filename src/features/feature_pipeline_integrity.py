from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PipelineSchema:
    """
    Immutable snapshot of the input schema presented to the
    AQTIP feature pipeline.
    """

    input_columns: tuple[str, ...]
    input_row_count: int
    input_index: pd.Index


class FeaturePipelineIntegrity:
    """
    Pipeline-level integrity enforcement for AQTIP.

    FeatureRuntime validates individual feature contracts.

    FeaturePipelineIntegrity validates the complete pipeline.

    Responsibilities:

    - Preserve original market-data columns.
    - Preserve original row count.
    - Preserve original index.
    - Ensure every declared feature output exists.
    - Prevent feature-output collisions with input columns.
    - Prevent duplicate feature output declarations.
    - Provide deterministic schema accounting.
    """

    @staticmethod
    def capture_input(df: pd.DataFrame) -> PipelineSchema:
        """
        Capture the immutable structural properties of pipeline input.
        """

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Feature pipeline input must be a pandas DataFrame."
            )

        return PipelineSchema(
            input_columns=tuple(df.columns),
            input_row_count=len(df),
            input_index=df.index.copy(),
        )

    @staticmethod
    def validate_feature_outputs(
        input_schema: PipelineSchema,
        output_df: pd.DataFrame,
        expected_outputs: tuple[str, ...],
    ) -> None:
        """
        Validate the structural integrity of the completed pipeline.
        """

        if not isinstance(output_df, pd.DataFrame):
            raise TypeError(
                "Feature pipeline output must be a pandas DataFrame."
            )

        # ----------------------------------------------------------
        # Row-count preservation
        # ----------------------------------------------------------

        if len(output_df) != input_schema.input_row_count:
            raise ValueError(
                "Feature pipeline violated row-count preservation: "
                f"expected {input_schema.input_row_count}, "
                f"got {len(output_df)}."
            )

        # ----------------------------------------------------------
        # Index preservation
        # ----------------------------------------------------------

        if not output_df.index.equals(input_schema.input_index):
            raise ValueError(
                "Feature pipeline changed the input DataFrame index."
            )

        # ----------------------------------------------------------
        # Original market-data columns
        # ----------------------------------------------------------

        missing_input_columns = [
            column
            for column in input_schema.input_columns
            if column not in output_df.columns
        ]

        if missing_input_columns:
            raise ValueError(
                "Feature pipeline removed original input columns: "
                f"{missing_input_columns}"
            )

        # ----------------------------------------------------------
        # Duplicate feature declarations
        # ----------------------------------------------------------

        if len(expected_outputs) != len(set(expected_outputs)):
            raise ValueError(
                "Feature pipeline contains duplicate feature output "
                "declarations."
            )

        # ----------------------------------------------------------
        # Feature/input collision
        # ----------------------------------------------------------

        collisions = [
            output
            for output in expected_outputs
            if output in input_schema.input_columns
        ]

        if collisions:
            raise ValueError(
                "Feature output columns collide with original input "
                f"columns: {collisions}"
            )

        # ----------------------------------------------------------
        # Missing feature outputs
        # ----------------------------------------------------------

        missing_outputs = [
            output
            for output in expected_outputs
            if output not in output_df.columns
        ]

        if missing_outputs:
            raise ValueError(
                "Feature pipeline did not generate expected feature "
                f"outputs: {missing_outputs}"
            )

    @staticmethod
    def validate_input_integrity(
        original_df: pd.DataFrame,
        output_df: pd.DataFrame,
    ) -> None:
        """
        Verify that original market-data values remain unchanged.

        Feature columns may be appended, but the original input columns
        must retain their original values.
        """

        if not isinstance(original_df, pd.DataFrame):
            raise TypeError(
                "Original pipeline input must be a pandas DataFrame."
            )

        if not isinstance(output_df, pd.DataFrame):
            raise TypeError(
                "Feature pipeline output must be a pandas DataFrame."
            )

        missing_columns = [
            column
            for column in original_df.columns
            if column not in output_df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Feature pipeline removed original input columns: "
                f"{missing_columns}"
            )

        original_values = original_df.loc[
            :,
            list(original_df.columns),
        ]

        output_values = output_df.loc[
            :,
            list(original_df.columns),
        ]

        if not original_values.equals(output_values):
            raise ValueError(
                "Feature pipeline mutated one or more original "
                "market-data columns."
            )