import numpy as np
import h5py
import os

def transform_2010_to_2024(weights_2010, file_path):
    """
    Transforms weights from 2010 constituencies to 2024 constituencies using the mapping matrix.

    Args:
        weights_2010 (numpy.ndarray): A 1D array of weights corresponding to 2010 constituencies.
        file_path (str): Path to the h5 file containing the mapping matrix.

    Returns:
        numpy.ndarray: A 1D array of weights corresponding to 2024 constituencies.
    """
    with h5py.File(file_path, 'r') as hf:
        mapping_matrix = hf['df'][:]  # Load the saved matrix

    if len(weights_2010) != mapping_matrix.shape[0]:
        raise ValueError(
            f"Input weights_2010 has length {len(weights_2010)}, "
            f"but mapping matrix expects {mapping_matrix.shape[0]} rows."
        )

    weights_2024 = np.dot(weights_2010, mapping_matrix)
    return weights_2024