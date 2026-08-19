import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.registry import IndicatorRegistry


print("=" * 60)
print("AQTIP Indicator Registry Runtime Contract Test")
print("=" * 60)


# ------------------------------------------------------------------
# Test fixtures
# ------------------------------------------------------------------

def valid_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["test_indicator"] = (
        result["close"].rolling(window=2).mean()
    )
    return result


def missing_output_indicator(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


def row_changing_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["test_indicator"] = 1.0
    return result.iloc[:-1].copy()


def mutating_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df["close"] = 999.0
    df["test_indicator"] = 1.0
    return df


def invalid_warmup_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["test_indicator"] = 1.0
    return result


def future_looking_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["test_indicator"] = (
        result["close"]
        .rolling(window=2, min_periods=1)
        .mean()
        .shift(-1)
    )
    return result


def causal_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["test_indicator"] = (
        result["close"].rolling(window=2).mean()
    )
    return result


def base_contract(
    *,
    causal: bool = True,
    warmup_period: int = 2,
) -> FeatureContract:
    return FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=warmup_period,
        causal=causal,
    )


# ------------------------------------------------------------------
# Registry setup
# ------------------------------------------------------------------

registry = IndicatorRegistry()

registry.register(
    name="Test Indicator",
    role="test",
    function=valid_indicator,
    contract=base_contract(),
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
        contract=base_contract(),
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
        contract=base_contract(),
    )
    raise AssertionError(
        "Non-callable indicator was not blocked."
    )
except TypeError as exc:
    print("\nCallable validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Causal contract validation
# ------------------------------------------------------------------

try:
    registry.register(
        name="Invalid Causal Contract",
        role="test",
        function=valid_indicator,
        contract=FeatureContract(
            output_column="invalid_causal",
            required_columns=("close",),
            warmup_period=2,
            causal="yes",
        ),
    )
    raise AssertionError(
        "Non-boolean causal contract was not blocked."
    )
except TypeError as exc:
    print("\nCausal contract type validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Required input columns
# ------------------------------------------------------------------

try:
    registry.apply(
        pd.DataFrame({"open": [1.0, 2.0, 3.0]})
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

output_registry = IndicatorRegistry()
output_registry.register(
    name="Missing Output",
    role="test",
    function=missing_output_indicator,
    contract=base_contract(),
)

try:
    output_registry.apply(
        pd.DataFrame({"close": [10.0, 20.0, 30.0]})
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

row_registry = IndicatorRegistry()
row_registry.register(
    name="Row Changing",
    role="test",
    function=row_changing_indicator,
    contract=base_contract(),
)

try:
    row_registry.apply(
        pd.DataFrame({"close": [10.0, 20.0, 30.0]})
    )
    raise AssertionError(
        "Row-count violation was not blocked."
    )
except ValueError as exc:
    print("\nRow-count validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Input immutability
# ------------------------------------------------------------------

mutation_registry = IndicatorRegistry()
mutation_registry.register(
    name="Mutating Indicator",
    role="test",
    function=mutating_indicator,
    contract=FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=1,
        causal=False,
    ),
)

original = pd.DataFrame({"close": [10.0, 20.0, 30.0]})
original_snapshot = original.copy(deep=True)
mutation_registry.apply(original)

if not original.equals(original_snapshot):
    raise AssertionError(
        "Registry allowed an indicator to mutate the "
        "original input DataFrame."
    )

print("\nInput immutability protection PASSED.")


# ------------------------------------------------------------------
# Input index preservation
# ------------------------------------------------------------------

def index_changing_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["test_indicator"] = 1.0
    result.index = range(len(result))
    return result


index_registry = IndicatorRegistry()
index_registry.register(
    name="Index Changing",
    role="test",
    function=index_changing_indicator,
    contract=FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=1,
        causal=False,
    ),
)

indexed_input = pd.DataFrame(
    {"close": [10.0, 20.0, 30.0]},
    index=[10, 20, 30],
)

try:
    index_registry.apply(indexed_input)
    raise AssertionError(
        "Index mutation was not blocked."
    )
except ValueError as exc:
    print("\nIndex preservation validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Warm-up enforcement
# ------------------------------------------------------------------

warmup_registry = IndicatorRegistry()
warmup_registry.register(
    name="Invalid Warmup",
    role="test",
    function=invalid_warmup_indicator,
    contract=FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=3,
        causal=True,
    ),
)

try:
    warmup_registry.apply(
        pd.DataFrame({"close": [10.0, 20.0, 30.0, 40.0]})
    )
    raise AssertionError(
        "Warm-up violation was not blocked."
    )
except ValueError as exc:
    print("\nWarm-up validation PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Causality / look-ahead protection
# ------------------------------------------------------------------

causal_registry = IndicatorRegistry()
causal_registry.register(
    name="Future Looking Indicator",
    role="test",
    function=future_looking_indicator,
    contract=FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=1,
        causal=True,
    ),
)

try:
    causal_registry.apply(
        pd.DataFrame(
            {"close": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]}
        )
    )
    raise AssertionError(
        "Look-ahead violation was not blocked."
    )
except ValueError as exc:
    print("\nCausality / look-ahead protection PASSED.")
    print(exc)


# ------------------------------------------------------------------
# Valid causal execution
# ------------------------------------------------------------------

valid_input = pd.DataFrame(
    {"close": [10.0, 20.0, 30.0, 40.0]}
)
valid_input_snapshot = valid_input.copy(deep=True)

valid_registry = IndicatorRegistry()
valid_registry.register(
    name="Valid Causal Indicator",
    role="test",
    function=causal_indicator,
    contract=base_contract(),
)

valid_output = valid_registry.apply(valid_input)

assert len(valid_output) == len(valid_input), (
    "Valid indicator changed row count."
)

assert "test_indicator" in valid_output.columns, (
    "Valid indicator did not generate its expected output column."
)

assert pd.isna(valid_output["test_indicator"].iloc[0]), (
    "The first value should be NaN during the warm-up period."
)

assert valid_output["test_indicator"].iloc[1] == 15.0, (
    "The first valid rolling value should equal 15.0."
)

assert valid_input.equals(valid_input_snapshot), (
    "Valid indicator mutated the input DataFrame."
)

print("\nValid causal contract execution PASSED.")


# ------------------------------------------------------------------
# Registry definitions
# ------------------------------------------------------------------

print("\nIndicator definitions:")

for definition in valid_registry.definitions():
    print(
        f"- {definition.name} | "
        f"role={definition.role} | "
        f"output={definition.contract.output_column} | "
        f"warmup={definition.contract.warmup_period} | "
        f"causal={definition.contract.causal} | "
        f"required={definition.contract.required_columns}"
    )


print("\nRegistry runtime contract tests PASSED.")