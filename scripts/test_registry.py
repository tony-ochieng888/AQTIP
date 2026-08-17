from src.features.registry import IndicatorRegistry


def dummy_indicator(df):
    return df


registry = IndicatorRegistry()

print("=" * 60)
print("AQTIP Indicator Registry Test")
print("=" * 60)


# ---------------------------------------------------------
# Test 1: Registration
# ---------------------------------------------------------

registry.register(
    name="Test Indicator",
    role="test",
    function=dummy_indicator,
    output_column="test_indicator",
)

print("\nRegistered indicators:")
print(registry.names())

print("\nRegistered roles:")
print(registry.roles())

print("\nRegistered output columns:")
print(registry.output_columns())


# ---------------------------------------------------------
# Test 2: Duplicate protection
# ---------------------------------------------------------

try:
    registry.register(
        name="Test Indicator",
        role="test",
        function=dummy_indicator,
        output_column="test_indicator",
    )

    raise AssertionError(
        "Duplicate registration was not blocked."
    )

except ValueError as error:
    print("\nDuplicate protection PASSED.")
    print(error)


# ---------------------------------------------------------
# Test 3: Invalid function protection
# ---------------------------------------------------------

try:
    registry.register(
        name="Invalid Indicator",
        role="test",
        function="not_a_function",
        output_column="invalid_indicator",
    )

    raise AssertionError(
        "Invalid function was not blocked."
    )

except TypeError as error:
    print("\nCallable validation PASSED.")
    print(error)


# ---------------------------------------------------------
# Test 4: Definitions
# ---------------------------------------------------------

print("\nIndicator definitions:")

for definition in registry.definitions():
    print(
        f"- {definition.name} "
        f"| role={definition.role} "
        f"| output={definition.output_column}"
    )


print("\nRegistry tests PASSED.")