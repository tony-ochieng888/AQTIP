from src.features.feature_contract import FeatureContract
from src.features.registry import IndicatorRegistry


def dummy_indicator(df):
    return df


registry = IndicatorRegistry()

print("=" * 60)
print("AQTIP Indicator Registry Test")
print("=" * 60)

test_contract = FeatureContract(
    output_column="test_indicator",
    required_columns=("close",),
    warmup_period=1,
)

# Test 1: Registration

registry.register(
    name="Test Indicator",
    role="test",
    function=dummy_indicator,
    contract=test_contract,
)

print("\nRegistered indicators:")
print(registry.names())

print("\nRegistered roles:")
print(registry.roles())

print("\nRegistered output columns:")
print(registry.output_columns())

# Test 2: Duplicate protection

try:
    registry.register(
        name="Test Indicator",
        role="test",
        function=dummy_indicator,
        contract=test_contract,
    )

    raise AssertionError(
        "Duplicate registration was not blocked."
    )

except ValueError as error:
    print("\nDuplicate protection PASSED.")
    print(error)

# Test 3: Invalid function protection

try:
    registry.register(
        name="Invalid Indicator",
        role="test",
        function="not_a_function",
        contract=FeatureContract(
            output_column="invalid_indicator",
            required_columns=("close",),
            warmup_period=1,
        ),
    )

    raise AssertionError(
        "Invalid function was not blocked."
    )

except TypeError as error:
    print("\nCallable validation PASSED.")
    print(error)

# Test 4: Definitions

print("\nIndicator definitions:")

for definition in registry.definitions():
    print(
        f"- {definition.name} "
        f"| role={definition.role} "
        f"| output={definition.contract.output_column} "
        f"| warmup={definition.contract.warmup_period} "
        f"| required={definition.contract.required_columns}"
    )

print("\nRegistry tests PASSED.")