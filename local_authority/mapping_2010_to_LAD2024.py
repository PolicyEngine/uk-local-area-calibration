import pandas as pd
import numpy as np
import os

def generate_lad_mapping(constituency_lad_path, mapping_2010_2024_path, output_path=None):
    """
    Generate a mapping matrix from 2010 constituencies to 2024 LADs.
    
    Parameters:
    -----------
    constituency_lad_path : str
        Path to the CSV file containing constituency to LAD mapping for 2024
    mapping_2010_2024_path : str
        Path to the CSV file containing mapping from 2010 to 2024 constituencies
    output_path : str, optional
        Path where the new mapping matrix should be saved. If None, matrix is only returned
        
    Returns:
    --------
    pandas.DataFrame
        The new mapping matrix from 2010 constituencies to 2024 LADs
    """
    
    # Load the constituency to LAD mapping
    constituency_lad = pd.read_csv(
        constituency_lad_path, 
        usecols=['PCON24CD', 'PCON24NM', 'LAD24CD', 'LAD24NM']
    )
    
    # Load and process the 2010 to 2024 constituency mapping
    mapping_2010_2024 = pd.read_csv(mapping_2010_2024_path)
    mapping_2010_2024 = mapping_2010_2024.set_index(mapping_2010_2024.columns[0])
    mapping_2010_2024 = mapping_2010_2024.div(mapping_2010_2024.sum(), axis=1)
    
    # Create constituency to LAD mapping matrix
    constituency_lad_grouped = constituency_lad.groupby(['PCON24CD', 'LAD24CD']).size().reset_index()
    constituency_lad_matrix = pd.crosstab(
        constituency_lad_grouped['PCON24CD'],
        constituency_lad_grouped['LAD24CD']
    ).div(1)
    
    # Create the direct mapping from 2010 constituencies to 2024 LADs
    new_mapping_matrix = mapping_2010_2024.dot(constituency_lad_matrix)
    
    # Normalize the weights
    new_mapping_matrix = new_mapping_matrix.div(new_mapping_matrix.sum(), axis=1)
    
    # Save if output path is provided
    if output_path:
        new_mapping_matrix.to_csv(output_path)
    
    return new_mapping_matrix

if __name__ == "__main__":
    # Get the project root directory (uk-local-area-calibration)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    constituency_lad_path = os.path.join(BASE_DIR, "local_authority", "Constituency_to_LAD(2024).csv")
    mapping_2010_2024_path = os.path.join(BASE_DIR, "mapping_2010_to_2024", "mapping_matrix.csv")
    output_path = os.path.join(BASE_DIR, "local_authority", "mapping_2010_to_LAD2024.csv")
    
    # Print paths for debugging
    print(f"Looking for files at:")
    print(f"Constituency LAD file: {constituency_lad_path}")
    print(f"Mapping matrix file: {mapping_2010_2024_path}")
    
    # Check if files exist
    if not os.path.exists(constituency_lad_path):
        print(f"ERROR: Constituency LAD file not found at {constituency_lad_path}")
    if not os.path.exists(mapping_2010_2024_path):
        print(f"ERROR: Mapping matrix file not found at {mapping_2010_2024_path}")
    
    try:
        new_mapping = generate_lad_mapping(
            constituency_lad_path,
            mapping_2010_2024_path,
            output_path
        )
        print("\nNew mapping matrix generated successfully!")
        print(f"Shape: {new_mapping.shape}")
        print(f"Saved to: {output_path}")
    except Exception as e:
        print(f"\nError generating mapping matrix: {str(e)}")