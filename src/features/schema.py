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

    ATR_14 = "atr_14"

    KIJUN_26 = "kijun_26"