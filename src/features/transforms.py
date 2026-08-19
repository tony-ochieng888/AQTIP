from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from src.features.feature_contract import FeatureContract
from src.features.schema import FeatureColumns
from src.utils.logger import logger


@dataclass(frozen=True)
class FeatureTransformDefinition:
    """
    Immutable executable definition of a base feature transform.

    Combines:

    - Human-readable feature identity.
    - Executable transformation function.
    - Immutable FeatureContract.

    Runtime enforcement belongs to FeatureRuntime.

    Pipeline orchestration belongs to FeaturePipeline.
    """

    name: str
    function: Callable[[pd.DataFrame], pd.DataFrame]
    contract: FeatureContract

    def __post_init__(self) -> None:
        """Validate the transform definition immediately."""

        if not isinstance(self.name, str):
            raise TypeError(
                "Feature transform name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Feature transform name cannot be empty."
            )

        if not callable(self.function):
            raise TypeError(
                f"Function for feature transform '{self.name}' "
                "must be callable."
            )

        if not isinstance(self.contract, FeatureContract):
            raise TypeError(
                f"Contract for feature transform '{self.name}' "
                "must be a FeatureContract."
            )


class FeatureTransforms:
    """
    General mathematical transformations applied to market datasets.

    Architectural responsibility:

    - Define deterministic base feature transformations.
    - Declare the execution contract for each transformation.
    - Keep mathematical transformation logic separate from
      runtime contract enforcement.

    FeatureRuntime is responsible for verifying these contracts.

    FeaturePipeline is responsible only for orchestration.
    """

    @staticmethod
    def add_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add simple percentage returns.

        Mathematical dependency:

            return[t] = close[t] / close[t-1] - 1

        Therefore two observations are required before the first
        valid return can exist.
        """

        logger.info("Generating returns feature...")

        result = df.copy()

        result[FeatureColumns.RETURNS] = (
            result[FeatureColumns.CLOSE]
            .pct_change()
        )

        return result

    @staticmethod
    def add_log_returns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add logarithmic returns.

        Mathematical dependency:

            log_return[t] =
                log(close[t] / close[t-1])

        Therefore two observations are required before the first
        valid log return can exist.
        """

        logger.info("Generating log returns feature...")

        result = df.copy()

        result[FeatureColumns.LOG_RETURNS] = np.log(
            result[FeatureColumns.CLOSE]
            / result[FeatureColumns.CLOSE].shift(1)
        )

        return result

    @staticmethod
    def definitions() -> tuple[FeatureTransformDefinition, ...]:
        """
        Return immutable definitions for all base transforms.

        Each definition contains:

        - Human-readable feature name.
        - Executable transformation function.
        - Immutable FeatureContract.

        Metadata remains co-located with the implementation while
        enforcement remains centralized in FeatureRuntime.
        """

        return (
            FeatureTransformDefinition(
                name="Returns",
                function=FeatureTransforms.add_returns,
                contract=FeatureContract(
                    output_column=FeatureColumns.RETURNS,
                    required_columns=(
                        FeatureColumns.CLOSE,
                    ),
                    warmup_period=2,
                    causal=True,
                ),
            ),
            FeatureTransformDefinition(
                name="Log Returns",
                function=FeatureTransforms.add_log_returns,
                contract=FeatureContract(
                    output_column=FeatureColumns.LOG_RETURNS,
                    required_columns=(
                        FeatureColumns.CLOSE,
                    ),
                    warmup_period=2,
                    causal=True,
                ),
            ),
        )