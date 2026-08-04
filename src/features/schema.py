from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureColumns:
    """
    Defines canonical feature names used
    throughout AQTIP.
    """

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"

    RETURNS = "returns"

    LOG_RETURNS = "log_returns"

    SMA_20 = "sma_20"

    EMA_20 = "ema_20"

    ATR_14 = "atr_14"