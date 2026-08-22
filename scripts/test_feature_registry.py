import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.feature_definition import FeatureDefinition
from src.features.feature_registry import FeatureRegistry


def test_feature(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)

    result["test_feature"] = result["close"].rolling(
        window=2,
        min_periods=2,
    ).mean()

    return result


def test_feature_two(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)

    result["test_feature_two"] = result["close"].rolling(
        window=2,
        min_periods=2,
    ).mean()

    return result


def main() -> None:
    print("=" * 60)
    print("AQTIP Feature Registry Runtime Contract Test")
    print("=" * 60)

    # ----------------------------------------------------------
    # Test fixture
    # ----------------------------------------------------------

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

    contract = FeatureContract(
        output_column="test_feature",
        required_columns=("close",),
        warmup_period=2,
        causal=True,
    )

    # ----------------------------------------------------------
    # FeatureDefinition validation
    # ----------------------------------------------------------

    definition = FeatureDefinition(
        name="Test Feature",
        role="test",
        function=test_feature,
        contract=contract,
    )

    assert definition.name == "Test Feature"
    assert definition.role == "test"
    assert definition.function is test_feature
    assert definition.contract == contract

    print("\nFeatureDefinition validation PASSED.")

    # ----------------------------------------------------------
    # FeatureDefinition invalid name
    # ----------------------------------------------------------

    try:
        FeatureDefinition(
            name="",
            role="test",
            function=test_feature,
            contract=contract,
        )

        raise AssertionError(
            "Empty feature name was not rejected."
        )

    except ValueError as exc:
        assert "Feature name cannot be empty" in str(exc)

        print("FeatureDefinition name validation PASSED.")

    # ----------------------------------------------------------
    # Registry construction
    # ----------------------------------------------------------

    registry = FeatureRegistry()

    registry.register(
        name="Test Feature",
        role="test",
        function=test_feature,
        contract=contract,
    )

    # ----------------------------------------------------------
    # Registration discovery
    # ----------------------------------------------------------

    assert registry.names() == ["Test Feature"]

    print("\nRegistered features:")
    print(registry.names())

    assert registry.roles() == ["test"]

    print("\nRegistered roles:")
    print(registry.roles())

    assert registry.output_columns() == ["test_feature"]

    print("\nRegistered output columns:")
    print(registry.output_columns())

    # ----------------------------------------------------------
    # Duplicate feature-name protection
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Test Feature",
            role="test",
            function=test_feature_two,
            contract=FeatureContract(
                output_column="test_feature_two",
                required_columns=("close",),
                warmup_period=2,
                causal=True,
            ),
        )

        raise AssertionError(
            "Duplicate feature name was not rejected."
        )

    except ValueError as exc:
        assert "already registered" in str(exc)

        print("\nDuplicate protection PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Non-callable validation
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Invalid Feature",
            role="test",
            function="not callable",  # type: ignore[arg-type]
            contract=FeatureContract(
                output_column="invalid_feature",
                required_columns=("close",),
                warmup_period=2,
                causal=True,
            ),
        )

        raise AssertionError(
            "Non-callable feature function was not rejected."
        )

    except TypeError as exc:
        assert "must be callable" in str(exc)

        print("\nCallable validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Contract validation
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Invalid Contract Feature",
            role="test",
            function=test_feature_two,
            contract="not a FeatureContract",  # type: ignore[arg-type]
        )

        raise AssertionError(
            "Invalid contract type was not rejected."
        )

    except TypeError as exc:
        assert "must be a FeatureContract" in str(exc)

        print("\nContract type validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Duplicate output-column protection
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Duplicate Output Feature",
            role="test",
            function=test_feature_two,
            contract=FeatureContract(
                output_column="test_feature",
                required_columns=("close",),
                warmup_period=2,
                causal=True,
            ),
        )

        raise AssertionError(
            "Duplicate output column was not rejected."
        )

    except ValueError as exc:
        assert "already registered" in str(exc)

        print("\nOutput-column duplicate protection PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Second valid registration
    # ----------------------------------------------------------

    second_contract = FeatureContract(
        output_column="test_feature_two",
        required_columns=("close",),
        warmup_period=2,
        causal=True,
    )

    registry.register(
        name="Second Test Feature",
        role="test",
        function=test_feature_two,
        contract=second_contract,
    )

    assert registry.names() == [
        "Test Feature",
        "Second Test Feature",
    ]

    assert registry.roles() == [
        "test",
        "test",
    ]

    assert registry.output_columns() == [
        "test_feature",
        "test_feature_two",
    ]

    print("\nMultiple registration PASSED.")

    # ----------------------------------------------------------
    # Definition snapshot protection
    # ----------------------------------------------------------

    definitions = registry.definitions()

    assert len(definitions) == 2
    assert definitions[0].name == "Test Feature"
    assert definitions[1].name == "Second Test Feature"

    definitions.clear()

    assert len(registry.definitions()) == 2

    print("Definition snapshot protection PASSED.")

    # ----------------------------------------------------------
    # Runtime application
    # ----------------------------------------------------------

    original = df.copy(deep=True)

    result = registry.apply(df)

    assert isinstance(result, pd.DataFrame)

    assert "test_feature" in result.columns
    assert "test_feature_two" in result.columns

    assert len(result) == len(df)

    assert result.index.equals(df.index)

    assert df.equals(original)

    print("Runtime application PASSED.")

    # ----------------------------------------------------------
    # Final report
    # ----------------------------------------------------------

    print("\nRegistered definitions:")

    for definition in registry.definitions():
        print(
            f"- {definition.name} | "
            f"role={definition.role} | "
            f"output={definition.contract.output_column} | "
            f"warmup={definition.contract.warmup_period} | "
            f"causal={definition.contract.causal} | "
            f"required={definition.contract.required_columns}"
        )

    print("\nFeature Registry contract tests PASSED.")


if __name__ == "__main__":
    main()