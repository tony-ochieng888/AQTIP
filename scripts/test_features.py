from src.data.downloader import MarketDataDownloader
from src.data.validator import MarketDataValidator

from src.features.feature_pipeline import FeaturePipeline
from src.features.schema import FeatureColumns


from src.storage.parquet_store import ParquetStore


print("=" * 60)
print("AQTIP Feature Pipeline Test")
print("=" * 60)

# Download
downloader = MarketDataDownloader()
candles = downloader.download()

# Validate
validator = MarketDataValidator()
validated = validator.validate(candles)

# Convert to DataFrame
store = ParquetStore()
df = store.save(validated)

# Generate Features
pipeline = FeaturePipeline()

print("\nRegistered Indicators:")
print(pipeline.registry.names())


df = pipeline.run(df)

# ------------------------------------------------------------
# Automated Feature Validation
# ------------------------------------------------------------

required_features = [
    FeatureColumns.RETURNS,
    FeatureColumns.LOG_RETURNS,
    FeatureColumns.ATR_14,
    FeatureColumns.KIJUN_26,
]

print("\nRunning automated feature validation...")

# 1. Required columns exist
missing_features = [
    feature
    for feature in required_features
    if feature not in df.columns
]

assert not missing_features, (
    f"Missing required features: {missing_features}"
)

# 2. Row count must remain unchanged
assert len(df) == len(validated), (
    f"Row count changed: expected {len(validated)}, got {len(df)}"
)

# 3. ATR warm-up validation
assert df[FeatureColumns.ATR_14].iloc[:13].isna().all(), (
    "ATR(14) should be NaN during its warm-up period."
)

assert df[FeatureColumns.ATR_14].iloc[13:].notna().all(), (
    "ATR(14) contains unexpected NaN values after warm-up."
)

# 4. ATR must never be negative
assert (df[FeatureColumns.ATR_14].dropna() >= 0).all(), (
    "ATR contains negative values."
)

# 5. Kijun warm-up validation
assert df[FeatureColumns.KIJUN_26].iloc[:25].isna().all(), (
    "Kijun(26) should be NaN during its warm-up period."
)

assert df[FeatureColumns.KIJUN_26].iloc[25:].notna().all(), (
    "Kijun(26) contains unexpected NaN values after warm-up."
)

print(" Required features present.")
print(" Row count preserved.")
print(" ATR(14) warm-up validated.")
print(" ATR values validated.")
print(" Kijun(26) warm-up validated.")
print(" Kijun(26) values validated.")
print(" Automated feature validation PASSED.")



print("\nGenerated Columns:\n")
print(df.columns.tolist())
print("\nPreview:\n")

print(
    df[
        [
            FeatureColumns.CLOSE,
            FeatureColumns.RETURNS,
            FeatureColumns.LOG_RETURNS,
            FeatureColumns.ATR_14,
            FeatureColumns.KIJUN_26,
        ]
    ].head(30)
)
