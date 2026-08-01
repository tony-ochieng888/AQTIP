from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.downloader import MarketDataDownloader

print("=" * 50)
print("AQTIP Downloader Test")
print("=" * 50)

downloader = MarketDataDownloader()

candles = downloader.download()

print(f"Downloaded {len(candles)} candles.")

print("\nFirst candle:\n")

print(candles[0])