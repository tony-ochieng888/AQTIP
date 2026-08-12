from src.features.indicator_factory import IndicatorFactory


print("=" * 60)
print("AQTIP Indicator Factory Test")
print("=" * 60)


# Test 1: ATR factory creation

atr_function = IndicatorFactory.create(
    name="ATR(14)",
    period=14,
)

assert callable(atr_function)

print("\nATR factory creation PASSED.")


# Test 2: Kijun factory creation

kijun_function = IndicatorFactory.create(
    name="Kijun Sen(26)",
    period=26,
)

assert callable(kijun_function)

print("Kijun factory creation PASSED.")


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