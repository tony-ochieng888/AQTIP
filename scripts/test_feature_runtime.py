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


# ============================================================
# Valid feature
# ============================================================

def valid_feature(dataframe: pd.DataFrame) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"]
        .pct_change()
    )

    return result


# pct_change() requires two observations before the first
# valid value exists.
#
# Therefore:
#
# row 0 -> NaN
# row 1 -> first valid value
#
# warmup_period = 2
valid_contract = FeatureContract(
    output_column="test_feature",
    required_columns=("close",),
    warmup_period=2,
    causal=True,
)


result = FeatureRuntime.execute(
    df=df,
    function=valid_feature,
    contract=valid_contract,
    name="Valid Feature",
)

assert "test_feature" in result.columns

assert result["test_feature"].iloc[0] != (
    result["test_feature"].iloc[0]
)

assert result["test_feature"].iloc[1:].notna().all()

print("\nValid feature execution PASSED.")


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
    print("\nRequired-column protection PASSED.")
    print(error)


# ============================================================
# Row-count protection
# ============================================================

def row_changing_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"]
        .pct_change()
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
    print("\nRow-count protection PASSED.")
    print(error)


# ============================================================
# Input immutability protection
# ============================================================

def mutating_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    dataframe["close"] = 999.0

    dataframe["test_feature"] = (
        dataframe["close"]
        .pct_change()
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
        "Input mutation was not rejected."
    )

except ValueError as error:
    print("\nInput immutability protection PASSED.")
    print(error)


# ============================================================
# Index protection
# ============================================================

def index_changing_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"]
        .pct_change()
    )

    result.index = range(len(result))

    return result


indexed_df = df.copy(deep=True)
indexed_df.index = [10, 20, 30, 40, 50, 60]

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
    print("\nOutput-column protection PASSED.")
    print(error)


# ============================================================
# Warm-up protection
# ============================================================

def invalid_warmup_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"]
        .pct_change()
        .fillna(0.0)
    )

    return result


try:
    FeatureRuntime.execute(
        df=df,
        function=invalid_warmup_feature,
        contract=valid_contract,
        name="Invalid Warmup Feature",
    )

    raise AssertionError(
        "Invalid warm-up behavior was not rejected."
    )

except ValueError as error:
    print("\nWarm-up protection PASSED.")
    print(error)


# ============================================================
# Causality protection
# ============================================================

def future_looking_feature(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy(deep=True)

    result["test_feature"] = (
        result["close"]
        .shift(-1)
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
    print("\nCausality protection PASSED.")
    print(error)


# ============================================================
# Final result
# ============================================================

print("\nFeature Runtime contract tests PASSED.")