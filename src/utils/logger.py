import logging
from pathlib import Path

from src.utils.config import config

# Create the logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "aqtip.log"

logging.basicConfig(
    level=getattr(logging, config["logging"]["level"]),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AQTIP")