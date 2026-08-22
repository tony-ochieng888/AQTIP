from dataclasses import dataclass
from typing import Callable

import pandas as pd

from src.features.feature_contract import FeatureContract


@dataclass(frozen=True)
class FeatureDefinition:
    """
    Complete registered definition of an AQTIP feature.

    A feature may represent:

    - A base mathematical transformation.
    - A technical indicator.
    - A future feature family.

    The registry deliberately does not distinguish between these
    implementation categories.

    Feature identity and execution guarantees are defined by:

    - name
    - role
    - function
    - contract
    """

    name: str
    role: str
    function: Callable[[pd.DataFrame], pd.DataFrame]
    contract: FeatureContract

    def __post_init__(self) -> None:
        """Validate the feature definition immediately."""

        if not isinstance(self.name, str):
            raise TypeError(
                "Feature name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Feature name cannot be empty."
            )

        if not isinstance(self.role, str):
            raise TypeError(
                f"Role for feature '{self.name}' must be a string."
            )

        if not self.role.strip():
            raise ValueError(
                f"Role for feature '{self.name}' cannot be empty."
            )

        if not callable(self.function):
            raise TypeError(
                f"Function for feature '{self.name}' must be callable."
            )

        if not isinstance(self.contract, FeatureContract):
            raise TypeError(
                f"Contract for feature '{self.name}' "
                "must be a FeatureContract."
            )