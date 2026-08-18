import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.registry import IndicatorRegistry


print("=" * 60)
print("AQTIP Indicator Registry Test")
print("=" * 60)


def valid_indicator(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()

    result["test_indicator"] = (
        result["close"].rolling(window=2).mean()
    )

    return result


contract = FeatureContract(
    output_column="test_indicator",
    required_columns=("close",),
    warmup_period=2,
)

registry = IndicatorRegistry()

registry.register(
    name="Test Indicator",
    role="test",
    function=valid_indicator,
    contract=contract,
)

print("\nRegistered indicators:")
print(registry.names())

print("\nRegistered roles:")
print(registry.roles())

print("\nRegistered output columns:")
print(registry.output_columns())


# ------------------------------------------------------------------
# Duplicate registration protection
# ------------------------------------------------------------------

try:
    registry.register(
        name="Test Indicator",
        role="test",
        function=valid_indicator,
        contract=contract,
    )

    raise AssertionError(
        "Duplicate registration was not blocked."
    )

except ValueError as exc:
    print("\nDuplicate protection PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Callable validation
# ------------------------------------------------------------------

try:
    registry.register(
        name="Invalid Indicator",
        role="test",
        function="not_callable",
        contract=FeatureContract(
            output_column="invalid",
            required_columns=("close",),
            warmup_period=1,
        ),
    )

    raise AssertionError(
        "Non-callable indicator was not blocked."
    )

except TypeError as exc:
    print("\nCallable validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Required input columns
# ------------------------------------------------------------------

try:
    registry.apply(
        pd.DataFrame(
            {
                "open": [1.0, 2.0, 3.0],
            }
        )
    )

    raise AssertionError(
        "Missing required columns were not blocked."
    )

except ValueError as exc:
    print("\nRequired-column validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Expected output column
# ------------------------------------------------------------------

def missing_output_indicator(
    df: pd.DataFrame,
) -> pd.DataFrame:
    return df.copy()


output_registry = IndicatorRegistry()

output_registry.register(
    name="Missing Output",
    role="test",
    function=missing_output_indicator,
    contract=contract,
)

try:
    output_registry.apply(
        pd.DataFrame(
            {
                "close": [10.0, 20.0, 30.0],
            }
        )
    )

    raise AssertionError(
        "Missing output column was not blocked."
    )

except ValueError as exc:
    print("\nOutput-column validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Row-count preservation
# ------------------------------------------------------------------

def row_changing_indicator(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()

    result["test_indicator"] = 1.0

    return result.iloc[:-1].copy()


row_registry = IndicatorRegistry()

row_registry.register(
    name="Row Changing",
    role="test",
    function=row_changing_indicator,
    contract=contract,
)

try:
    row_registry.apply(
        pd.DataFrame(
            {
                "close": [10.0, 20.0, 30.0],
            }
        )
    )

    raise AssertionError(
        "Row-count violation was not blocked."
    )

except ValueError as exc:
    print("\nRow-count validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Input immutability
#
# The registry intentionally passes a deep copy of the input to
# every indicator. Therefore an indicator may mutate its private
# working DataFrame without mutating the pipeline's original data.
# ------------------------------------------------------------------

def mutating_indicator(
    df: pd.DataFrame,
) -> pd.DataFrame:
    df["close"] = 999.0
    df["test_indicator"] = 1.0

    return df


mutation_registry = IndicatorRegistry()

mutation_registry.register(
    name="Mutating Indicator",
    role="test",
    function=mutating_indicator,
    contract=FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=1,
    ),
)

original = pd.DataFrame(
    {
        "close": [10.0, 20.0, 30.0],
    }
)

original_snapshot = original.copy(
    deep=True
)

mutation_registry.apply(original)

if not original.equals(original_snapshot):
    raise AssertionError(
        "Registry allowed an indicator to mutate the "
        "original input DataFrame."
    )

print("\nInput immutability protection PASSED.")


# ------------------------------------------------------------------
# Warm-up enforcement
# ------------------------------------------------------------------

def invalid_warmup_indicator(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()

    result["test_indicator"] = 1.0

    return result


warmup_registry = IndicatorRegistry()

warmup_registry.register(
    name="Invalid Warmup",
    role="test",
    function=invalid_warmup_indicator,
    contract=FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=3,
    ),
)

try:
    warmup_registry.apply(
        pd.DataFrame(
            {
                "close": [10.0, 20.0, 30.0, 40.0],
            }
        )
    )

    raise AssertionError(
        "Warm-up violation was not blocked."
    )

except ValueError as exc:
    print("\nWarm-up validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Valid execution
# ------------------------------------------------------------------

valid_input = pd.DataFrame(
    {
        "close": [
            10.0,
            20.0,
            30.0,
            40.0,
        ],
    }
)

valid_input_snapshot = valid_input.copy(
    deep=True
)

valid_output = registry.apply(
    valid_input
)

assert len(valid_output) == len(valid_input), (
    "Valid indicator changed row count."
)

assert "test_indicator" in valid_output.columns, (
    "Valid indicator did not generate its expected output column."
)

assert pd.isna(
    valid_output["test_indicator"].iloc[0]
), (
    "The first value should be NaN during the warm-up period."
)

assert valid_output["test_indicator"].iloc[1] == 15.0, (
    "The first valid rolling value should equal 15.0."
)

assert valid_input.equals(
    valid_input_snapshot
), (
    "Valid indicator mutated the input DataFrame."
)

print("\nValid contract execution PASSED.")


# ------------------------------------------------------------------
# Registry definitions
# ------------------------------------------------------------------

print("\nIndicator definitions:")

for definition in registry.definitions():
    print(
        f"- {definition.name} | "
        f"role={definition.role} | "
        f"output={definition.contract.output_column} | "
        f"warmup={definition.contract.warmup_period} | "
        f"required={definition.contract.required_columns}"
    )


print("\nRegistry runtime contract tests PASSED.")