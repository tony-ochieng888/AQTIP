from src.features.feature_contract import FeatureContract
from src.features.indicator_factory import IndicatorFactory


print("=" * 60)
print("AQTIP Indicator Factory Contract Test")
print("=" * 60)


# ============================================================
# Test 1: ATR factory creation
# ============================================================

atr_definition = IndicatorFactory.create(
    name="ATR(14)",
    period=14,
)

assert callable(atr_definition.function)

assert isinstance(
    atr_definition.contract,
    FeatureContract,
)

assert atr_definition.contract.output_column == "atr_14"

assert atr_definition.contract.required_columns == (
    "high",
    "low",
    "close",
)

assert atr_definition.contract.warmup_period == 14

assert atr_definition.contract.causal is True

print("\nATR factory creation PASSED.")
print(
    f"Output column: "
    f"{atr_definition.contract.output_column}"
)
print(
    f"Required columns: "
    f"{atr_definition.contract.required_columns}"
)
print(
    f"Warm-up period: "
    f"{atr_definition.contract.warmup_period}"
)
print(
    f"Causal: "
    f"{atr_definition.contract.causal}"
)


# ============================================================
# Test 2: Kijun factory creation
# ============================================================

kijun_definition = IndicatorFactory.create(
    name="Kijun Sen(26)",
    period=26,
)

assert callable(kijun_definition.function)

assert isinstance(
    kijun_definition.contract,
    FeatureContract,
)

assert kijun_definition.contract.output_column == "kijun_26"

assert kijun_definition.contract.required_columns == (
    "high",
    "low",
)

assert kijun_definition.contract.warmup_period == 26

assert kijun_definition.contract.causal is True

print("\nKijun factory creation PASSED.")
print(
    f"Output column: "
    f"{kijun_definition.contract.output_column}"
)
print(
    f"Required columns: "
    f"{kijun_definition.contract.required_columns}"
)
print(
    f"Warm-up period: "
    f"{kijun_definition.contract.warmup_period}"
)
print(
    f"Causal: "
    f"{kijun_definition.contract.causal}"
)


# ============================================================
# Test 3: Dynamic period metadata
# ============================================================

atr_20_definition = IndicatorFactory.create(
    name="ATR(20)",
    period=20,
)

assert atr_20_definition.contract.output_column == "atr_20"

assert atr_20_definition.contract.required_columns == (
    "high",
    "low",
    "close",
)

assert atr_20_definition.contract.warmup_period == 20

assert atr_20_definition.contract.causal is True

print("\nDynamic ATR period metadata PASSED.")
print(
    f"Output column: "
    f"{atr_20_definition.contract.output_column}"
)
print(
    f"Warm-up period: "
    f"{atr_20_definition.contract.warmup_period}"
)


kijun_50_definition = IndicatorFactory.create(
    name="Kijun Sen(50)",
    period=50,
)

assert kijun_50_definition.contract.output_column == "kijun_50"

assert kijun_50_definition.contract.required_columns == (
    "high",
    "low",
)

assert kijun_50_definition.contract.warmup_period == 50

assert kijun_50_definition.contract.causal is True

print("Dynamic Kijun period metadata PASSED.")
print(
    f"Output column: "
    f"{kijun_50_definition.contract.output_column}"
)
print(
    f"Warm-up period: "
    f"{kijun_50_definition.contract.warmup_period}"
)


# ============================================================
# Test 4: Invalid period protection
# ============================================================

try:
    IndicatorFactory.create(
        name="ATR(0)",
        period=0,
    )

    raise AssertionError(
        "Invalid period was not rejected."
    )

except ValueError as error:
    print("\nInvalid period protection PASSED.")
    print(error)


# ============================================================
# Test 5: Invalid period type protection
# ============================================================

try:
    IndicatorFactory.create(
        name="ATR(14)",
        period="14",
    )

    raise AssertionError(
        "Non-integer period was not rejected."
    )

except TypeError as error:
    print("\nInvalid period type protection PASSED.")
    print(error)


# ============================================================
# Test 6: Boolean period protection
# ============================================================

try:
    IndicatorFactory.create(
        name="ATR(14)",
        period=True,
    )

    raise AssertionError(
        "Boolean period was not rejected."
    )

except TypeError as error:
    print("\nBoolean period protection PASSED.")
    print(error)


# ============================================================
# Test 7: Invalid indicator name protection
# ============================================================

try:
    IndicatorFactory.create(
        name="",
        period=14,
    )

    raise AssertionError(
        "Empty indicator name was not rejected."
    )

except ValueError as error:
    print("\nInvalid indicator name protection PASSED.")
    print(error)


# ============================================================
# Test 8: Invalid indicator name type protection
# ============================================================

try:
    IndicatorFactory.create(
        name=None,
        period=14,
    )

    raise AssertionError(
        "Non-string indicator name was not rejected."
    )

except TypeError as error:
    print("\nIndicator name type validation PASSED.")
    print(error)


# ============================================================
# Test 9: Unsupported indicator protection
# ============================================================

try:
    IndicatorFactory.create(
        name="Unsupported Indicator",
        period=14,
    )

    raise AssertionError(
        "Unsupported indicator was not rejected."
    )

except ValueError as error:
    print("\nUnsupported indicator protection PASSED.")
    print(error)


# ============================================================
# Final result
# ============================================================

print("\nIndicator Factory definitions:")

print(
    f"- ATR(14) | "
    f"output={atr_definition.contract.output_column} | "
    f"warmup={atr_definition.contract.warmup_period} | "
    f"causal={atr_definition.contract.causal} | "
    f"required={atr_definition.contract.required_columns}"
)

print(
    f"- Kijun Sen(26) | "
    f"output={kijun_definition.contract.output_column} | "
    f"warmup={kijun_definition.contract.warmup_period} | "
    f"causal={kijun_definition.contract.causal} | "
    f"required={kijun_definition.contract.required_columns}"
)

print("\nIndicator Factory contract tests PASSED.")