from src.features.indicator_factory import IndicatorFactory


print("=" * 60)
print("AQTIP Indicator Factory Test")
print("=" * 60)


# ============================================================
# Test 1: ATR factory creation
# ============================================================

atr_definition = IndicatorFactory.create(
    name="ATR(14)",
    period=14,
)

assert callable(atr_definition.function)

assert atr_definition.contract.output_column == "atr_14"

assert atr_definition.contract.required_columns == (
    "high",
    "low",
    "close",
)

assert atr_definition.contract.warmup_period == 14

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


# ============================================================
# Test 2: Kijun factory creation
# ============================================================

kijun_definition = IndicatorFactory.create(
    name="Kijun Sen(26)",
    period=26,
)

assert callable(kijun_definition.function)

assert kijun_definition.contract.output_column == "kijun_26"

assert kijun_definition.contract.required_columns == (
    "high",
    "low",
)

assert kijun_definition.contract.warmup_period == 26

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


# ============================================================
# Test 3: Dynamic period metadata
# ============================================================

atr_20_definition = IndicatorFactory.create(
    name="ATR(20)",
    period=20,
)

assert atr_20_definition.contract.output_column == "atr_20"

assert atr_20_definition.contract.warmup_period == 20

print("\nDynamic ATR period metadata PASSED.")
print(
    f"Output column: "
    f"{atr_20_definition.contract.output_column}"
)


kijun_50_definition = IndicatorFactory.create(
    name="Kijun Sen(50)",
    period=50,
)

assert kijun_50_definition.contract.output_column == "kijun_50"

assert kijun_50_definition.contract.warmup_period == 50

print("Dynamic Kijun period metadata PASSED.")
print(
    f"Output column: "
    f"{kijun_50_definition.contract.output_column}"
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
# Test 5: Unsupported indicator protection
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

print("\nIndicator Factory tests PASSED.")