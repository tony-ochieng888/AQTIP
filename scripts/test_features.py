import numpy as np
import pandas as pd

from src.data.downloader import MarketDataDownloader
from src.data.validator import MarketDataValidator
from src.features.feature_contract import FeatureContract
from src.features.feature_pipeline import FeaturePipeline
from src.features.schema import FeatureColumns
from src.features.transforms import (
    FeatureTransformDefinition,
    FeatureTransforms,
)
from src.storage.parquet_store import ParquetStore


print("=" * 60)
print("AQTIP Feature Pipeline Test")
print("=" * 60)


# ============================================================
# Feature transform definition validation
# ============================================================

print("\nValidating feature transform definitions...")

definitions = FeatureTransforms.definitions()

assert len(definitions) == 2

for definition in definitions:
    assert isinstance(
        definition,
        FeatureTransformDefinition,
    )

    assert isinstance(
        definition.name,
        str,
    )

    assert definition.name.strip()

    assert callable(definition.function)

    assert isinstance(
        definition.contract,
        FeatureContract,
    )

print(" Feature transform definitions validated.")
print(" Feature transform contracts validated.")


# Verify FeatureTransformDefinition immutability.

try:
    definitions[0].name = "Mutated Name"

    raise AssertionError(
        "FeatureTransformDefinition allowed mutation."
    )

except AttributeError:
    print(" Feature transform immutability PASSED.")


# ============================================================
# Download market data
# ============================================================

downloader = MarketDataDownloader()

candles = downloader.download()


# ============================================================
# Validate market data
# ============================================================

validator = MarketDataValidator()

validated_candles = validator.validate(candles)


# ============================================================
# Store market data
#
# ParquetStore.save() is the established AQTIP boundary that
# converts validated Binance candles into a pandas DataFrame.
# FeaturePipeline.run() consumes that DataFrame.
# ============================================================

store = ParquetStore()

validated_df = store.save(
    validated_candles,
    "BTCUSDT_1h.parquet",
)

assert isinstance(
    validated_df,
    pd.DataFrame,
)

print(" Market data storage PASSED.")


# Preserve the exact input received by the feature pipeline.
# This snapshot is used to verify that feature execution does
# not mutate the caller's DataFrame.
original_df = validated_df.copy(deep=True)


# ============================================================
# Create feature pipeline
# ============================================================

pipeline = FeaturePipeline()


print("\nRegistered Indicators:")
print(
    pipeline.registry.names()
)


# ============================================================
# Execute feature pipeline
# ============================================================

result = pipeline.run(validated_df)

assert isinstance(
    result,
    pd.DataFrame,
)


# ============================================================
# Automated feature validation
# ============================================================

print("\nRunning automated feature validation...")


# ------------------------------------------------------------
# Required features
# ------------------------------------------------------------

required_features = [
    FeatureColumns.RETURNS,
    FeatureColumns.LOG_RETURNS,
    "atr_14",
    "kijun_26",
]

for feature in required_features:
    assert feature in result.columns

print(" Required features present.")


# ------------------------------------------------------------
# Row count preservation
# ------------------------------------------------------------

assert len(result) == len(validated_df)

print(" Row count preserved.")


# ------------------------------------------------------------
# Index preservation
# ------------------------------------------------------------

assert result.index.equals(
    validated_df.index
)

print(" Input index preserved.")


# ------------------------------------------------------------
# Original market-data columns preserved
# ------------------------------------------------------------

for column in validated_df.columns:
    assert column in result.columns

print(" Original market-data columns preserved.")


# ------------------------------------------------------------
# Input immutability
# ------------------------------------------------------------

pd.testing.assert_frame_equal(
    validated_df,
    original_df,
)

print(" Input market-data integrity preserved.")


# ------------------------------------------------------------
# Returns validation
# ------------------------------------------------------------

returns = result[
    FeatureColumns.RETURNS
]

assert pd.isna(
    returns.iloc[0]
)

assert returns.iloc[1:].notna().all()

expected_returns = (
    validated_df[
        FeatureColumns.CLOSE
    ].pct_change()
)

pd.testing.assert_series_equal(
    returns,
    expected_returns,
    check_names=False,
)

print(" Returns warm-up validated.")
print(" Returns values validated.")


# ------------------------------------------------------------
# Log returns validation
# ------------------------------------------------------------

log_returns = result[
    FeatureColumns.LOG_RETURNS
]

assert pd.isna(
    log_returns.iloc[0]
)

assert log_returns.iloc[1:].notna().all()

expected_log_returns = (
    validated_df[
        FeatureColumns.CLOSE
    ]
    / validated_df[
        FeatureColumns.CLOSE
    ].shift(1)
).apply(np.log)

pd.testing.assert_series_equal(
    log_returns,
    expected_log_returns,
    check_names=False,
)

print(" Log returns warm-up validated.")
print(" Log returns values validated.")


# ------------------------------------------------------------
# ATR validation
# ------------------------------------------------------------

atr = result["atr_14"]

assert atr.iloc[:13].isna().all()
assert atr.iloc[13:].notna().all()

print(" ATR(14) warm-up validated.")


# ------------------------------------------------------------
# Kijun validation
# ------------------------------------------------------------

kijun = result["kijun_26"]

assert kijun.iloc[:25].isna().all()
assert kijun.iloc[25:].notna().all()

print(" Kijun(26) warm-up validated.")


# ============================================================
# Final result
# ============================================================

print(" Automated feature validation PASSED.")

print("\nGenerated Columns:")
print()

print(
    result.columns.tolist()
)


print("\nPreview:")
print()

print(
    result[
        [
            FeatureColumns.CLOSE,
            FeatureColumns.RETURNS,
            FeatureColumns.LOG_RETURNS,
            "atr_14",
            "kijun_26",
        ]
    ].head(30)
)


print("\nAQTIP Feature Pipeline Test PASSED.")
