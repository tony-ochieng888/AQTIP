from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.logger import logger

logger.info("AQTIP logger initialized successfully.")
logger.warning("Sample warning message.")
logger.error("Sample error message.")