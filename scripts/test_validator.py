
from src.data.downloader import MarketDataDownloader
from src.data.validator import MarketDataValidator

print("=" * 50)
print("AQTIP Validation Test")
print("=" * 50)

downloader = MarketDataDownloader()

validator = MarketDataValidator()

candles = downloader.download()

validated = validator.validate(candles)

print(f"Validated {len(validated)} candles successfully.")