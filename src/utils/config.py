from pathlib import Path
import yaml


class Config:
    """
    Central configuration loader for AQTIP.
    """

    def __init__(self):
        config_path = (
            Path(__file__).resolve().parents[2]
            / "configs"
            / "config.yaml"
        )

        with open(config_path, "r", encoding="utf-8") as file:
            self._settings = yaml.safe_load(file)

    def get(self):
        return self._settings


config = Config().get()