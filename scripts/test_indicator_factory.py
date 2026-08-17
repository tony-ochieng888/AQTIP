from src.features.feature_contract import FeatureContract
from src.features.indicator_factory import IndicatorFactory


print("=" * 60)
print("AQTIP Indicator Factory Test")
print("=" * 60)


# Test 1: ATR factory creation

atr_definition = IndicatorFactory.create(
    name="ATR(14)",
    period=14,
)

assert callable(atr_definition.function)
assert isinstance(atr_definition.contract, FeatureContract)

assert atr_definition.contract.output_column == "atr_14"
assert atr_definition.contract.required_columns == (
    "high",
    "low",
    "close",
)
assert atr_definition.contract.warmup_period == 14

print("\nATR factory creation PASSED.")
print(f"Output column: {atr_definition.contract.output_column}")
print(f"Required columns: {atr_definition.contract.required_columns}")
print(f"Warm-up period: {atr_definition.contract.warmup_period}")


# Test 2: Kijun factory creation

kijun_definition = IndicatorFactory.create(
    name="Kijun Sen(26)",
    period=26,
)

assert callable(kijun_definition.function)
assert isinstance(kijun_definition.contract, FeatureContract)

assert kijun_definition.contract.output_column == "kijun_26"
assert kijun_definition.contract.required_columns == (
    "high",
    "low",
)
assert kijun_definition.contract.warmup_period == 26

print("\nKijun factory creation PASSED.")
print(f"Output column: {kijun_definition.contract.output_column}")
print(f"Required columns: {kijun_definition.contract.required_columns}")
print(f"Warm-up period: {kijun_definition.contract.warmup_period}")


# Test 3: Unsupported indicator protection

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


print("\nIndicator Factory tests PASSED.")