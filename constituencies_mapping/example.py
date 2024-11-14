import os
import numpy as np
from transform_constituencies import transform_2010_to_2024
import h5py

print("Current working directory:", os.getcwd())

# Use the full path to the file
file_path = os.path.join(os.getcwd(), 'constituencies_mapping', 'constituencies_mapping_2010_2024.h5')
print("Looking for file at:", file_path)

# Load the mapping matrix and its metadata to check dimensions
with h5py.File(file_path, 'r') as hf:
    mapping_matrix = hf['df'][:]
    code_2010_count = mapping_matrix.shape[0]
    code_2024_count = mapping_matrix.shape[1]
    
    # Extract the metadata for row and column indices
    code_2010_indices = hf.attrs['rows'] if 'rows' in hf.attrs else None
    code_2024_indices = hf.attrs['columns'] if 'columns' in hf.attrs else None

# Print the dimensions
print(f"Number of 2010 constituencies: {code_2010_count}")
print(f"Number of 2024 constituencies: {code_2024_count}")

# Example of using the transform function
# Create some dummy weights for demonstration
dummy_weights_2010 = np.ones(code_2010_count)  # Create array of ones with correct size
transformed_weights = transform_2010_to_2024(dummy_weights_2010, file_path)

print("\nExample transformation results:")
print(f"Input weights shape: {dummy_weights_2010.shape}")
print(f"Output weights shape: {transformed_weights.shape}")