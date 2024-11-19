import os
import numpy as np
import h5py
import pandas as pd
from pathlib import Path
from typing import Union

def transform_2010_to_2024(weights_2010: np.ndarray, file_path: Union[str, Path]) -> np.ndarray:
    """
    Transforms weights from 2010 constituencies to 2024 constituencies using the mapping matrix.
    """
    file_path = Path(file_path)
    
    with h5py.File(file_path, 'r') as hf:
        mapping_matrix = hf['df'][:]  # Now matches the dataset name we saved
        
    if len(weights_2010) != mapping_matrix.shape[0]:
        raise ValueError(
            f"Input weights_2010 has length {len(weights_2010)}, "
            f"but mapping matrix expects {mapping_matrix.shape[0]} rows."
        )
        
    weights_2024: np.ndarray = np.dot(weights_2010, mapping_matrix)
    return weights_2024