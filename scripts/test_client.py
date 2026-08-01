from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.client import BinanceClient

print("=" * 50)
print("AQTIP Binance Client Test")
print("=" * 50)

client = BinanceClient()

print(" Binance client object created successfully.")
print(type(client.get_client()))