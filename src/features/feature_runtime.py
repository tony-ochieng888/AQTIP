from typing import Callable

import pandas as pd

from src.features.feature_contract import FeatureContract


class FeatureRuntime:
    """
    AQTIP runtime contract-enforcement boundary.

    FeatureRuntime executes any feature-producing callable and
    verifies that its output satisfies the supplied FeatureContract.

    This runtime is deliberately independent of feature registration.

    It can therefore enforce contracts for:

    - Base mathematical transformations.
    - Technical indicators.
    - Future feature families.

    Architectural responsibilities:

    FeatureContract
        Defines what a feature promises.

    FeatureRuntime
        Verifies that the promise was actually kept.

    FeatureRegistry
        Owns registration and discovery.

    FeaturePipeline
        Orchestrates execution order.
    """

    @staticmethod
    def execute(
        df: pd.DataFrame,
        function: Callable[[pd.DataFrame], pd.DataFrame],
        contract: FeatureContract,
        name: str,
    ) -> pd.DataFrame:
        """
        Execute one feature through the runtime contract boundary.

        The runtime gives the feature a deep copy of the input
        DataFrame. This creates a defensive execution boundary and
        prevents direct mutation of the caller's DataFrame.

        The execution input is snapshotted before feature execution.
        After execution, the runtime verifies that the feature did not
        mutate that execution input.

        The returned DataFrame is then validated against the supplied
        FeatureContract.

        Causality validation deliberately occurs before warm-up
        validation so that accidental future-data dependence is
        reported as a causality violation rather than being masked by
        an unrelated warm-up violation.

        Parameters
        ----------
        df:
            Input DataFrame.

        function:
            Feature-producing callable.

        contract:
            FeatureContract governing execution.

        name:
            Human-readable feature name used in diagnostics.

        Returns
        -------
        pd.DataFrame
            Contract-validated feature output.

        Raises
        ------
        TypeError
            If inputs or outputs have invalid types.

        ValueError
            If any declared runtime contract is violated.
        """

        # ----------------------------------------------------------
        # Input validation
        # ----------------------------------------------------------

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"Feature '{name}' requires a pandas DataFrame."
            )

        if not callable(function):
            raise TypeError(
                f"Function for '{name}' must be callable."
            )

        if not isinstance(contract, FeatureContract):
            raise TypeError(
                f"Contract for '{name}' must be a FeatureContract."
            )

        FeatureRuntime._validate_required_columns(
            df,
            contract,
            name,
        )

        # ----------------------------------------------------------
        # Caller-input snapshot
        # ----------------------------------------------------------

        input_snapshot = df.copy(deep=True)
        input_row_count = len(df)

        # ----------------------------------------------------------
        # Defensive execution boundary
        # ----------------------------------------------------------

        execution_input = df.copy(deep=True)
        execution_snapshot = execution_input.copy(deep=True)

        try:
            generated = function(execution_input)
        except Exception as exc:
            raise RuntimeError(
                f"Feature '{name}' execution failed: {exc}"
            ) from exc

        # ----------------------------------------------------------
        # Execution-input immutability validation
        # ----------------------------------------------------------

        FeatureRuntime._validate_execution_input_immutability(
            execution_snapshot,
            execution_input,
            name,
        )

        # ----------------------------------------------------------
        # Output type validation
        # ----------------------------------------------------------

        if not isinstance(generated, pd.DataFrame):
            raise TypeError(
                f"Feature '{name}' must return a pandas DataFrame."
            )

        # ----------------------------------------------------------
        # Structural validation
        # ----------------------------------------------------------

        if len(generated) != input_row_count:
            raise ValueError(
                f"Feature '{name}' violated row-count preservation: "
                f"expected {input_row_count}, got {len(generated)}."
            )

        FeatureRuntime._validate_input_index(
            df,
            generated,
            name,
        )

        # ----------------------------------------------------------
        # Returned required-input immutability validation
        # ----------------------------------------------------------

        FeatureRuntime._validate_required_input_immutability(
            input_snapshot,
            generated,
            contract,
            name,
        )

        # ----------------------------------------------------------
        # Output-column validation
        # ----------------------------------------------------------

        output_column = contract.output_column

        if output_column not in generated.columns:
            raise ValueError(
                f"Feature '{name}' did not generate expected output "
                f"column '{output_column}'."
            )

        # ----------------------------------------------------------
        # Causality validation
        # ----------------------------------------------------------
        #
        # This deliberately occurs BEFORE warm-up validation.
        #
        # A future-looking feature must be rejected specifically for
        # violating causality rather than being rejected first because
        # its output contains NaN values during warm-up.
        # ----------------------------------------------------------

        if contract.causal:
            FeatureRuntime._validate_causality(
                df,
                generated,
                function,
                contract,
                name,
            )

        # ----------------------------------------------------------
        # Warm-up validation
        # ----------------------------------------------------------

        FeatureRuntime._validate_warmup(
            generated,
            contract,
            name,
        )

        return generated

    @staticmethod
    def _validate_required_columns(
        df: pd.DataFrame,
        contract: FeatureContract,
        name: str,
    ) -> None:
        """
        Ensure every declared input column exists.
        """

        missing = [
            column
            for column in contract.required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Feature '{name}' is missing required input "
                f"columns: {missing}"
            )

    @staticmethod
    def _validate_execution_input_immutability(
        before: pd.DataFrame,
        after: pd.DataFrame,
        name: str,
    ) -> None:
        """
        Ensure the feature did not mutate the DataFrame supplied to it.

        The runtime passes a defensive copy to the feature. That exact
        execution input is snapshotted before execution and compared
        immediately after execution.

        This catches direct in-place mutation of:

        - Original values.
        - Original columns.
        - Column ordering.
        - Index.
        - DataFrame structure.

        Output columns are not involved because this validation
        concerns the execution input itself.
        """

        if not before.equals(after):
            raise ValueError(
                f"Feature '{name}' mutated its execution input "
                "DataFrame."
            )

    @staticmethod
    def _validate_required_input_immutability(
        before: pd.DataFrame,
        generated: pd.DataFrame,
        contract: FeatureContract,
        name: str,
    ) -> None:
        """
        Ensure declared required input columns are preserved exactly.

        Feature contracts declare which input columns a feature depends
        upon. Those required inputs must not be modified, overwritten,
        removed, or structurally altered in the returned DataFrame.

        Features may add their declared output column and other derived
        columns, but their declared input dependencies remain immutable.

        This protection is distinct from execution-input immutability.

        Execution-input immutability protects the DataFrame passed into
        the feature.

        Required-input immutability protects the required market-data
        columns represented in the returned DataFrame.
        """

        required_columns = contract.required_columns

        missing_required_columns = [
            column
            for column in required_columns
            if column not in generated.columns
        ]

        if missing_required_columns:
            raise ValueError(
                f"Feature '{name}' removed required input columns: "
                f"{missing_required_columns}"
            )

        original_required = before.loc[:, required_columns]
        generated_required = generated.loc[:, required_columns]

        if not original_required.equals(generated_required):
            raise ValueError(
                f"Feature '{name}' mutated one or more required "
                "input columns."
            )

    @staticmethod
    def _validate_input_index(
        original: pd.DataFrame,
        generated: pd.DataFrame,
        name: str,
    ) -> None:
        """
        Ensure the feature preserves the input index exactly.
        """

        if not generated.index.equals(original.index):
            raise ValueError(
                f"Feature '{name}' changed the input DataFrame index."
            )

    @staticmethod
    def _validate_warmup(
        generated: pd.DataFrame,
        contract: FeatureContract,
        name: str,
    ) -> None:
        """
        Validate the declared warm-up boundary.

        For a warm-up period N:

        rows 0 through N-2 must be NaN.

        The first valid observation is therefore expected at
        position N-1.

        No NaN values may exist after that boundary.
        """

        output_column = contract.output_column
        warmup_period = contract.warmup_period

        series = generated[output_column]

        warmup_rows = min(
            warmup_period - 1,
            len(series),
        )

        if (
            warmup_rows > 0
            and series.iloc[:warmup_rows].notna().any()
        ):
            raise ValueError(
                f"Feature '{name}' violated warm-up behavior: "
                f"expected the first {warmup_rows} rows of "
                f"'{output_column}' to be NaN."
            )

        if len(series) >= warmup_period:
            if series.iloc[warmup_period - 1:].isna().any():
                raise ValueError(
                    f"Feature '{name}' violated warm-up behavior: "
                    f"'{output_column}' contains NaN values after "
                    "the warm-up boundary."
                )

    @staticmethod
    def _validate_causality(
        original: pd.DataFrame,
        generated: pd.DataFrame,
        function: Callable[[pd.DataFrame], pd.DataFrame],
        contract: FeatureContract,
        name: str,
    ) -> None:
        """
        Detect accidental future-data dependence.

        The feature is executed twice.

        The second execution mutates only the future portion of
        required numeric inputs.

        Values before the mutation point must remain unchanged.

        This is a runtime safeguard against accidental look-ahead
        behavior and future-data leakage.
        """

        if len(original) < 3:
            return

        mutation_point = len(original) // 2

        if mutation_point <= 0:
            return

        mutated = original.copy(deep=True)

        for column in contract.required_columns:
            if pd.api.types.is_numeric_dtype(
                mutated[column]
            ):
                future_index = mutated.index[mutation_point:]

                mutated.loc[
                    future_index,
                    column,
                ] = (
                    mutated.loc[
                        future_index,
                        column,
                    ]
                    + 1_000_000
                )

        try:
            mutated_generated = function(
                mutated.copy(deep=True)
            )
        except Exception as exc:
            raise RuntimeError(
                f"Feature '{name}' causality validation failed "
                f"during re-execution: {exc}"
            ) from exc

        if not isinstance(mutated_generated, pd.DataFrame):
            raise TypeError(
                f"Feature '{name}' must return a pandas DataFrame "
                "during causality validation."
            )

        if len(mutated_generated) != len(original):
            raise ValueError(
                f"Feature '{name}' violated row-count preservation "
                "during causality validation."
            )

        if not mutated_generated.index.equals(original.index):
            raise ValueError(
                f"Feature '{name}' changed the input DataFrame index "
                "during causality validation."
            )

        output_column = contract.output_column

        if output_column not in mutated_generated.columns:
            raise ValueError(
                f"Feature '{name}' did not generate expected output "
                f"column '{output_column}' during causality "
                "validation."
            )

        original_values = (
            generated[output_column]
            .iloc[:mutation_point]
        )

        mutated_values = (
            mutated_generated[output_column]
            .iloc[:mutation_point]
        )

        if not original_values.equals(mutated_values):
            raise ValueError(
                f"Feature '{name}' violated causal execution: "
                "feature values before the future mutation point "
                "changed."
            )