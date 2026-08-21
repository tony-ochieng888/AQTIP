import pandas as pd

from src.features.feature_pipeline_integrity import (
    FeaturePipelineIntegrity,
)


print("=" * 60)
print("AQTIP Feature Pipeline Integrity Test")
print("=" * 60)


# ============================================================
# Test data
# ============================================================

df = pd.DataFrame(
    {
        "open": [100.0, 101.0, 102.0, 103.0],
        "high": [102.0, 103.0, 104.0, 105.0],
        "low": [99.0, 100.0, 101.0, 102.0],
        "close": [101.0, 102.0, 103.0, 104.0],
    }
)


# ============================================================
# Input schema capture
# ============================================================

schema = FeaturePipelineIntegrity.capture_input(df)

assert schema.input_columns == (
    "open",
    "high",
    "low",
    "close",
)

assert schema.input_row_count == 4

assert schema.input_index.equals(df.index)

print("\nInput schema capture PASSED.")


# ============================================================
# Valid pipeline output
# ============================================================

valid_output = df.copy(deep=True)

valid_output["returns"] = (
    valid_output["close"].pct_change()
)

valid_output["atr_14"] = [
    None,
    None,
    None,
    1.5,
]

FeaturePipelineIntegrity.validate_feature_outputs(
    input_schema=schema,
    output_df=valid_output,
    expected_outputs=(
        "returns",
        "atr_14",
    ),
)

FeaturePipelineIntegrity.validate_input_integrity(
    original_df=df,
    output_df=valid_output,
)

print("Valid pipeline integrity PASSED.")


# ============================================================
# Row-count protection
# ============================================================

invalid_row_count = valid_output.iloc[:-1].copy()

try:
    FeaturePipelineIntegrity.validate_feature_outputs(
        input_schema=schema,
        output_df=invalid_row_count,
        expected_outputs=(
            "returns",
            "atr_14",
        ),
    )

    raise AssertionError(
        "Pipeline row-count violation was not rejected."
    )

except ValueError as error:
    assert "row-count preservation" in str(error)

    print("\nRow-count protection PASSED.")
    print(error)


# ============================================================
# Index protection
# ============================================================

invalid_index = valid_output.copy()

invalid_index.index = [10, 20, 30, 40]

try:
    FeaturePipelineIntegrity.validate_feature_outputs(
        input_schema=schema,
        output_df=invalid_index,
        expected_outputs=(
            "returns",
            "atr_14",
        ),
    )

    raise AssertionError(
        "Pipeline index violation was not rejected."
    )

except ValueError as error:
    assert "changed the input DataFrame index" in str(error)

    print("\nIndex protection PASSED.")
    print(error)


# ============================================================
# Missing original input column
# ============================================================

missing_input = valid_output.drop(
    columns=["close"]
)

try:
    FeaturePipelineIntegrity.validate_feature_outputs(
        input_schema=schema,
        output_df=missing_input,
        expected_outputs=(
            "returns",
            "atr_14",
        ),
    )

    raise AssertionError(
        "Removed input column was not rejected."
    )

except ValueError as error:
    assert "removed original input columns" in str(error)

    print("\nOriginal-column protection PASSED.")
    print(error)


# ============================================================
# Missing feature output
# ============================================================

missing_feature = df.copy(deep=True)

missing_feature["returns"] = (
    missing_feature["close"].pct_change()
)

try:
    FeaturePipelineIntegrity.validate_feature_outputs(
        input_schema=schema,
        output_df=missing_feature,
        expected_outputs=(
            "returns",
            "atr_14",
        ),
    )

    raise AssertionError(
        "Missing feature output was not rejected."
    )

except ValueError as error:
    assert "expected feature outputs" in str(error)

    print("\nMissing-output protection PASSED.")
    print(error)


# ============================================================
# Duplicate output declaration
# ============================================================

try:
    FeaturePipelineIntegrity.validate_feature_outputs(
        input_schema=schema,
        output_df=valid_output,
        expected_outputs=(
            "returns",
            "returns",
        ),
    )

    raise AssertionError(
        "Duplicate feature output declaration was not rejected."
    )

except ValueError as error:
    assert "duplicate feature output" in str(error)

    print("\nDuplicate-output protection PASSED.")
    print(error)


# ============================================================
# Input/output collision
# ============================================================

try:
    FeaturePipelineIntegrity.validate_feature_outputs(
        input_schema=schema,
        output_df=valid_output,
        expected_outputs=(
            "close",
        ),
    )

    raise AssertionError(
        "Feature/input column collision was not rejected."
    )

except ValueError as error:
    assert "collide with original input" in str(error)

    print("\nInput/output collision protection PASSED.")
    print(error)


# ============================================================
# Market-data mutation protection
# ============================================================

mutated_output = valid_output.copy(deep=True)

mutated_output.loc[0, "close"] = 999999.0

try:
    FeaturePipelineIntegrity.validate_input_integrity(
        original_df=df,
        output_df=mutated_output,
    )

    raise AssertionError(
        "Market-data mutation was not rejected."
    )

except ValueError as error:
    assert "mutated one or more original" in str(error)

    print("\nMarket-data mutation protection PASSED.")
    print(error)


# ============================================================
# Final result
# ============================================================

print(
    "\nFeature Pipeline Integrity tests PASSED."
)
