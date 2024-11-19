import os
import numpy as np
from transform_constituencies import transform_2010_to_2024
import h5py
import pandas as pd

# Example usage
print("Current working directory:", os.getcwd())

file_path = os.path.join(os.getcwd(), 'constituencies_mapping', 'constituency_mapping.h5')
print("Looking for file at:", file_path)

# Load the mapping matrix and its metadata
with h5py.File(file_path, 'r') as hf:
    mapping_matrix = hf['df'][:]  # Using 'df' as the dataset name
    
    code_2010_count = mapping_matrix.shape[0]
    code_2024_count = mapping_matrix.shape[1]
    
    # Try to get constituency codes if they were saved
    try:
        code_2010_indices = [i.decode('utf-8') for i in hf['row_indices'][:]]
        code_2024_indices = [i.decode('utf-8') for i in hf['col_indices'][:]]
    except KeyError:
        # If not saved, just use numbers
        code_2010_indices = list(range(code_2010_count))
        code_2024_indices = list(range(code_2024_count))

# Print information
print(f"\nNumber of 2010 constituencies: {code_2010_count}")
print(f"Number of 2024 constituencies: {code_2024_count}")

# Create and transform dummy weights
dummy_weights_2010 = np.ones(code_2010_count)
transformed_weights = transform_2010_to_2024(dummy_weights_2010, file_path)

# Create results DataFrame
results_df = pd.DataFrame({
    '2024_Constituency_Code': code_2024_indices,
    'Transformed_Weight': transformed_weights
})

print("\nTransformed Weights for each 2024 Constituency:")
print(results_df)