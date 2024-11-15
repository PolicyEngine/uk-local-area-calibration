import numpy as np
import h5py
from pathlib import Path
from typing import Union
import pandas as pd

def transform_2010_to_2024(weights_2010: np.ndarray, file_path: Union[str, Path] = Path(__file__).parent / "constituencies_mapping_2010_2024.h5") -> np.ndarray:
    """
    Transforms weights from 2010 constituencies to 2024 constituencies using the mapping matrix.

    Args:
        weights_2010 (np.ndarray): A 1D array of weights corresponding to 2010 constituencies.
        file_path (Union[str, Path]): Path to the h5 file containing the mapping matrix.
                                     Can be provided as string or Path object.

    Returns:
        np.ndarray: A 1D array of weights corresponding to 2024 constituencies.

    Raises:
        ValueError: If the input weights array length doesn't match the mapping matrix dimensions.
    """
    # Convert file_path to Path object if it isn't already
    file_path = Path(file_path)

    with h5py.File(file_path, 'r') as hf:
        mapping_matrix = hf['df'][:]  # Load the saved matrix

    if len(weights_2010) != mapping_matrix.shape[0]:
        raise ValueError(
            f"Input weights_2010 has length {len(weights_2010)}, "
            f"but mapping matrix expects {mapping_matrix.shape[0]} rows."
        )

    return np.dot(weights_2010, mapping_matrix)
