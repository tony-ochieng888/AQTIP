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
df = pipeline.run(df)

print("\nGenerated Columns:\n")
print(df.columns.tolist())
print("\nPreview:\n")

print(
    df[
        [
            FeatureColumns.CLOSE,
            FeatureColumns.RETURNS,
            FeatureColumns.LOG_RETURNS,
            FeatureColumns.SMA_20,
            FeatureColumns.EMA_20,
        ]
    ].head(30)
)