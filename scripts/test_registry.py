from typing import Any

import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.registry import IndicatorRegistry


def test_indicator(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)

    result["test_indicator"] = result["close"].rolling(
        window=2,
        min_periods=2,
    ).mean()

    return result


def test_indicator_two(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)

    result["test_indicator_two"] = result["close"].rolling(
        window=2,
        min_periods=2,
    ).mean()

    return result


def test_indicator_three(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy(deep=True)

    result["test_indicator_three"] = result["close"].rolling(
        window=2,
        min_periods=2,
    ).mean()

    return result


def main() -> None:
    print("=" * 60)
    print("AQTIP Indicator Registry Runtime Contract Test")
    print("=" * 60)

    registry = IndicatorRegistry()

    valid_contract = FeatureContract(
        output_column="test_indicator",
        required_columns=("close",),
        warmup_period=2,
        causal=True,
    )

    registry.register(
        name="Test Indicator",
        role="test",
        function=test_indicator,
        contract=valid_contract,
    )

    # ----------------------------------------------------------
    # Registration discovery
    # ----------------------------------------------------------

    assert registry.names() == ["Test Indicator"]

    print("\nRegistered indicators:")
    print(registry.names())

    assert registry.roles() == ["test"]

    print("\nRegistered roles:")
    print(registry.roles())

    assert registry.output_columns() == ["test_indicator"]

    print("\nRegistered output columns:")
    print(registry.output_columns())

    # ----------------------------------------------------------
    # Duplicate indicator-name protection
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Test Indicator",
            role="test",
            function=test_indicator_two,
            contract=FeatureContract(
                output_column="test_indicator_two",
                required_columns=("close",),
                warmup_period=2,
                causal=True,
            ),
        )

        raise AssertionError(
            "Duplicate indicator name was not rejected."
        )

    except ValueError as exc:
        assert "already registered" in str(exc)

        print("\nDuplicate protection PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Callable validation
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Invalid Indicator",
            role="test",
            function="not callable",  # type: ignore[arg-type]
            contract=FeatureContract(
                output_column="invalid_indicator",
                required_columns=("close",),
                warmup_period=2,
                causal=True,
            ),
        )

        raise AssertionError(
            "Non-callable indicator function was not rejected."
        )

    except TypeError as exc:
        assert "must be callable" in str(exc)

        print("\nCallable validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Contract type validation
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Invalid Contract Indicator",
            role="test",
            function=test_indicator_two,
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
    # Invalid causal contract
    #
    # IMPORTANT:
    # FeatureContract now owns its own validation.
    #
    # Therefore an invalid causal value must fail during
    # FeatureContract construction, before registry.register()
    # is reached.
    # ----------------------------------------------------------

    try:
        FeatureContract(
            output_column="invalid_causal_indicator",
            required_columns=("close",),
            warmup_period=2,
            causal="yes",  # type: ignore[arg-type]
        )

        raise AssertionError(
            "Invalid causal contract type was not rejected."
        )

    except TypeError as exc:
        assert "causal must be a boolean" in str(exc)

        print("\nCausal contract validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Invalid warm-up contract
    # ----------------------------------------------------------

    try:
        FeatureContract(
            output_column="invalid_warmup_indicator",
            required_columns=("close",),
            warmup_period=0,
            causal=True,
        )

        raise AssertionError(
            "Invalid warm-up period was not rejected."
        )

    except ValueError as exc:
        assert "warmup_period must be greater than zero" in str(exc)

        print("\nWarm-up contract validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Empty output-column contract
    # ----------------------------------------------------------

    try:
        FeatureContract(
            output_column="",
            required_columns=("close",),
            warmup_period=2,
            causal=True,
        )

        raise AssertionError(
            "Empty output column was not rejected."
        )

    except ValueError as exc:
        assert "output_column cannot be empty" in str(exc)

        print("\nOutput-column contract validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Required-column contract validation
    # ----------------------------------------------------------

    try:
        FeatureContract(
            output_column="invalid_required_columns",
            required_columns=(),  # type: ignore[arg-type]
            warmup_period=2,
            causal=True,
        )

        raise AssertionError(
            "Empty required_columns was not rejected."
        )

    except ValueError as exc:
        assert "at least one required input column" in str(exc)

        print("\nRequired-column contract validation PASSED.")
        print(exc)

    # ----------------------------------------------------------
    # Duplicate output-column protection
    # ----------------------------------------------------------

    try:
        registry.register(
            name="Duplicate Output Indicator",
            role="test",
            function=test_indicator_two,
            contract=FeatureContract(
                output_column="test_indicator",
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
        output_column="test_indicator_two",
        required_columns=("close",),
        warmup_period=2,
        causal=True,
    )

    registry.register(
        name="Second Test Indicator",
        role="test",
        function=test_indicator_two,
        contract=second_contract,
    )

    assert registry.names() == [
        "Test Indicator",
        "Second Test Indicator",
    ]

    assert registry.roles() == [
        "test",
        "test",
    ]

    assert registry.output_columns() == [
        "test_indicator",
        "test_indicator_two",
    ]

    print("\nMultiple registration PASSED.")

    # ----------------------------------------------------------
    # Definition snapshot protection
    # ----------------------------------------------------------

    definitions = registry.definitions()

    assert len(definitions) == 2
    assert definitions[0].name == "Test Indicator"
    assert definitions[1].name == "Second Test Indicator"

    definitions.clear()

    assert len(registry.definitions()) == 2

    print("Definition snapshot protection PASSED.")

    # ----------------------------------------------------------
    # Runtime application
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

    result = registry.apply(df)

    assert isinstance(result, pd.DataFrame)

    assert "test_indicator" in result.columns
    assert "test_indicator_two" in result.columns

    assert len(result) == len(df)

    assert result.index.equals(df.index)

    assert df.equals(
        pd.DataFrame(
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
    )

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

    print("\nIndicator Registry contract tests PASSED.")


if __name__ == "__main__":
    main()