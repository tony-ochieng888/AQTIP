from pathlib import Path

import pandas as pd

from src.utils.config import config
from src.utils.logger import logger


class ParquetStore:
    """
    Stores validated market data as
    Parquet files for efficient analysis.
    """

    COLUMNS = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]

    def save(self, candles, filename=None):

        logger.info("Converting candles to DataFrame...")

        df = pd.DataFrame(candles, columns=self.COLUMNS)

        # Convert timestamps
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

        # Convert numeric columns
        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_asset_volume",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column])

        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)

        if filename is None:
            filename = (
                f"{config['market']['symbol']}_"
                f"{config['market']['interval']}.parquet"
            )

        path = output_dir / filename

        df.to_parquet(path, index=False)

        logger.info(f"Saved dataset to {path}")

        return df