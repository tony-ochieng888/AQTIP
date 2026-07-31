from pathlib import Path
import sys

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import config

print("=" * 50)
print("AQTIP Configuration Test")
print("=" * 50)

print(f"Application : {config['application']['name']}")
print(f"Environment : {config['application']['environment']}")
print(f"Exchange    : {config['market']['exchange']}")
print(f"Symbol      : {config['market']['symbol']}")
print(f"Interval    : {config['market']['interval']}")