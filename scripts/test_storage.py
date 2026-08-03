from src.data.downloader import MarketDataDownloader
from src.data.validator import MarketDataValidator
from src.storage.parquet_store import ParquetStore

print("=" * 60)
print("AQTIP Storage Pipeline Test")
print("=" * 60)

# Step 1: Download
downloader = MarketDataDownloader()
candles = downloader.download()

# Step 2: Validate
validator = MarketDataValidator()
validated = validator.validate(candles)

# Step 3: Store
store = ParquetStore()

df = store.save(validated)

print("\nPipeline completed successfully.\n")

print(df.head())