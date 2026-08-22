import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.feature_runtime import FeatureRuntime


print("=" * 60)
print("AQTIP Feature Runtime Contract Test")
print("=" * 60)


# ============================================================
# Test data
# ============================================================

df = pd.DataFrame(
    {
        "close": [
            100.0,
            101.0,
            102.0,
            103.0,
            104.0,
            105.0,
        ]
    }
)

indexed_df = df.copy(deep=True)
indexed_df.index = [10, 20, 30, 40, 50, 60]


# ============================================================
# Shared valid contract
# ============================================================

valid_contract = FeatureContract(
    output_column="test_feature",
    required_columns=("close",),
    warmup_period=2,
    causal=True,
)


# ============================================================
# Shared valid feature
# ============================================================

def valid_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].pct_change()
    )

    return result


# ============================================================
# Valid execution
# ============================================================

original_df = df.copy(deep=True)

result = FeatureRuntime.execute(
    df=df,
    function=valid_feature,
    contract=valid_contract,
    name="Valid Feature",
)

assert isinstance(result, pd.DataFrame)

assert "test_feature" in result.columns

assert pd.isna(
    result["test_feature"].iloc[0]
)

assert result["test_feature"].iloc[1:].notna().all()

assert len(result) == len(df)

assert result.index.equals(df.index)

pd.testing.assert_frame_equal(
    df,
    original_df,
)

print("\nValid feature execution PASSED.")
print("Caller input preservation PASSED.")


# ============================================================
# Input type validation
# ============================================================

try:
    FeatureRuntime.execute(
        df="not a dataframe",  # type: ignore[arg-type]
        function=valid_feature,
        contract=valid_contract,
        name="Invalid Input Feature",
    )

    raise AssertionError(
        "Non-DataFrame input was not rejected."
    )

except TypeError as error:
    assert "requires a pandas DataFrame" in str(error)

    print("\nInput type validation PASSED.")
    print(error)


# ============================================================
# Callable validation
# ============================================================

try:
    FeatureRuntime.execute(
        df=df,
        function="not callable",  # type: ignore[arg-type]
        contract=valid_contract,
        name="Non Callable Feature",
    )

    raise AssertionError(
        "Non-callable feature was not rejected."
    )

except TypeError as error:
    assert "must be callable" in str(error)

    print("\nCallable validation PASSED.")
    print(error)


# ============================================================
# Contract type validation
# ============================================================

try:
    FeatureRuntime.execute(
        df=df,
        function=valid_feature,
        contract="not a contract",  # type: ignore[arg-type]
        name="Invalid Contract Feature",
    )

    raise AssertionError(
        "Invalid contract type was not rejected."
    )

except TypeError as error:
    assert "must be a FeatureContract" in str(error)

    print("\nContract type validation PASSED.")
    print(error)


# ============================================================
# Required-column protection
# ============================================================

missing_column_contract = FeatureContract(
    output_column="test_feature",
    required_columns=("missing",),
    warmup_period=2,
    causal=True,
)

try:
    FeatureRuntime.execute(
        df=df,
        function=valid_feature,
        contract=missing_column_contract,
        name="Missing Column Feature",
    )

    raise AssertionError(
        "Missing required column was not rejected."
    )

except ValueError as error:
    assert "missing required input columns" in str(error)

    print("\nRequired-column protection PASSED.")
    print(error)


# ============================================================
# Non-DataFrame output protection
# ============================================================

def non_dataframe_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    return dataframe["close"]  # type: ignore[return-value]


try:
    FeatureRuntime.execute(
        df=df,
        function=non_dataframe_feature,
        contract=valid_contract,
        name="Non DataFrame Output Feature",
    )

    raise AssertionError(
        "Non-DataFrame output was not rejected."
    )

except TypeError as error:
    assert "must return a pandas DataFrame" in str(error)

    print("\nOutput type protection PASSED.")
    print(error)


# ============================================================
# Row-count protection
# ============================================================

def row_changing_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].pct_change()
    )

    return result.iloc[:-1]


try:
    FeatureRuntime.execute(
        df=df,
        function=row_changing_feature,
        contract=valid_contract,
        name="Row Changing Feature",
    )

    raise AssertionError(
        "Row-count violation was not rejected."
    )

except ValueError as error:
    assert "row-count preservation" in str(error)

    print("\nRow-count protection PASSED.")
    print(error)


# ============================================================
# Execution-input immutability protection
# ============================================================

def mutating_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    dataframe["close"] = 999.0

    dataframe["test_feature"] = (
        dataframe["close"].pct_change()
    )

    return dataframe


try:
    FeatureRuntime.execute(
        df=df,
        function=mutating_feature,
        contract=valid_contract,
        name="Mutating Feature",
    )

    raise AssertionError(
        "Execution-input mutation was not rejected."
    )

except ValueError as error:
    assert "mutated its execution input" in str(error)

    print("\nExecution-input immutability protection PASSED.")
    print(error)


# ============================================================
# Returned required-input mutation protection
# ============================================================

def returned_input_mutating_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["close"] = (
        result["close"] + 1000.0
    )

    result["test_feature"] = (
        result["close"].pct_change()
    )

    return result


try:
    FeatureRuntime.execute(
        df=df,
        function=returned_input_mutating_feature,
        contract=valid_contract,
        name="Returned Input Mutating Feature",
    )

    raise AssertionError(
        "Returned required-input mutation was not rejected."
    )

except ValueError as error:
    assert "mutated one or more required input columns" in str(
        error
    )

    print("\nReturned-input immutability protection PASSED.")
    print(error)


# ============================================================
# Required-column removal protection
# ============================================================

def removing_required_column_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].pct_change()
    )

    return result.drop(columns=["close"])


try:
    FeatureRuntime.execute(
        df=df,
        function=removing_required_column_feature,
        contract=valid_contract,
        name="Removing Required Column Feature",
    )

    raise AssertionError(
        "Required-column removal was not rejected."
    )

except ValueError as error:
    assert "removed required input columns" in str(error)

    print("\nRequired-column removal protection PASSED.")
    print(error)


# ============================================================
# Index protection
# ============================================================

def index_changing_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].pct_change()
    )

    result.index = range(len(result))

    return result


try:
    FeatureRuntime.execute(
        df=indexed_df,
        function=index_changing_feature,
        contract=valid_contract,
        name="Index Changing Feature",
    )

    raise AssertionError(
        "Index mutation was not rejected."
    )

except ValueError as error:
    assert "changed the input DataFrame index" in str(error)

    print("\nIndex protection PASSED.")
    print(error)


# ============================================================
# Output-column protection
# ============================================================

def missing_output_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    return dataframe.copy(deep=True)


try:
    FeatureRuntime.execute(
        df=df,
        function=missing_output_feature,
        contract=valid_contract,
        name="Missing Output Feature",
    )

    raise AssertionError(
        "Missing output column was not rejected."
    )

except ValueError as error:
    assert "did not generate expected output column" in str(
        error
    )

    print("\nOutput-column protection PASSED.")
    print(error)


# ============================================================
# Warm-up protection: valid boundary
# ============================================================

def valid_warmup_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].rolling(
            window=3,
            min_periods=3,
        ).mean()
    )

    return result


warmup_contract = FeatureContract(
    output_column="test_feature",
    required_columns=("close",),
    warmup_period=3,
    causal=True,
)

warmup_result = FeatureRuntime.execute(
    df=df,
    function=valid_warmup_feature,
    contract=warmup_contract,
    name="Valid Warmup Feature",
)

assert warmup_result["test_feature"].iloc[:2].isna().all()

assert warmup_result["test_feature"].iloc[2:].notna().all()

print("\nValid warm-up behavior PASSED.")


# ============================================================
# Warm-up protection: first valid value too early
# ============================================================

def early_warmup_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].pct_change()
    )

    return result


invalid_warmup_contract = FeatureContract(
    output_column="test_feature",
    required_columns=("close",),
    warmup_period=3,
    causal=True,
)

try:
    FeatureRuntime.execute(
        df=df,
        function=early_warmup_feature,
        contract=invalid_warmup_contract,
        name="Early Warmup Feature",
    )

    raise AssertionError(
        "Early warm-up violation was not rejected."
    )

except ValueError as error:
    assert "violated warm-up behavior" in str(error)

    print("\nEarly warm-up protection PASSED.")
    print(error)


# ============================================================
# Warm-up protection: NaN after boundary
# ============================================================

def late_nan_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].pct_change()
    )

    result.loc[3, "test_feature"] = float("nan")

    return result


try:
    FeatureRuntime.execute(
        df=df,
        function=late_nan_feature,
        contract=valid_contract,
        name="Late NaN Feature",
    )

    raise AssertionError(
        "NaN after warm-up boundary was not rejected."
    )

except ValueError as error:
    assert "contains NaN values after" in str(error)

    print("\nPost-warm-up NaN protection PASSED.")
    print(error)


# ============================================================
# Causality protection
# ============================================================

def future_looking_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"].shift(-1)
    )

    return result


try:
    FeatureRuntime.execute(
        df=df,
        function=future_looking_feature,
        contract=valid_contract,
        name="Future Looking Feature",
    )

    raise AssertionError(
        "Future-data dependence was not rejected."
    )

except ValueError as error:
    assert "violated causal execution" in str(error)

    print("\nCausality protection PASSED.")
    print(error)


# ============================================================
# Valid causal feature
# ============================================================

def causal_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"]
        .rolling(
            window=2,
            min_periods=2,
        )
        .mean()
    )

    return result


causal_result = FeatureRuntime.execute(
    df=df,
    function=causal_feature,
    contract=valid_contract,
    name="Valid Causal Feature",
)

assert causal_result["test_feature"].iloc[0] != (
    causal_result["test_feature"].iloc[0]
)

assert causal_result["test_feature"].iloc[1:].notna().all()

print("\nValid causality execution PASSED.")


# ============================================================
# Small-input causality behavior
# ============================================================

small_df = pd.DataFrame(
    {
        "close": [100.0, 101.0],
    }
)

small_contract = FeatureContract(
    output_column="test_feature",
    required_columns=("close",),
    warmup_period=2,
    causal=True,
)

small_result = FeatureRuntime.execute(
    df=small_df,
    function=valid_feature,
    contract=small_contract,
    name="Small Input Feature",
)

assert small_result["test_feature"].iloc[0] != (
    small_result["test_feature"].iloc[0]
)

assert small_result["test_feature"].iloc[1] == (
    101.0 / 100.0 - 1.0
)

print("\nSmall-input causal execution PASSED.")


# ============================================================
# Caller input remains unchanged after all valid execution
# ============================================================

pd.testing.assert_frame_equal(
    df,
    original_df,
)

print("\nFinal caller-input immutability PASSED.")


# ============================================================
# Final result
# ============================================================

print("\n" + "=" * 60)
print("Feature Runtime contract tests PASSED.")
print("=" * 60)
