import pandas as pd
import re

# data from here: https://www.scotlandscensus.gov.uk/search-the-census#/topics/location

def scale_age_data(excel_file_path, age_csv_path):
    """
    Scale age data based on population data from Excel file.
    
    Args:
        excel_file_path (str): Path to Excel file with population data
        age_csv_path (str): Path to CSV file with age distribution data
    
    Returns:
        pd.DataFrame: Scaled age distribution dataset
    """
    # Read input files
    excel_file = pd.ExcelFile(excel_file_path)
    age_initial = pd.read_csv(age_csv_path)
    
    # Get sheet names
    sheet_names = excel_file.sheet_names

    # Clean names and get populations
    clean_names = []
    populations = []

    # Iterate through sheets (excluding last two)
    for sheet_name in sheet_names[:-2]:
        clean_name = re.sub(r'^\d+\.\s*', '', sheet_name)
        clean_names.append(clean_name)
        
        sheet_data = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        population = sheet_data.iloc[12, 3]
        populations.append(population)

    # Create DataFrame with clean names and populations
    df = pd.DataFrame({
        'name': clean_names,
        'population': populations
    })

    # Check for matching names
    matches = age_initial['name'].isin(df['name']).sum()
    total_df = len(df)

    print("\nName Matching Check:")
    print(f"Total rows in population data: {total_df}")
    print(f"Matching rows with age data: {matches}")
    print(f"Missing matches: {total_df - matches}")

    # Show unmatched names
    missing_names = df[~df['name'].isin(age_initial['name'])]['name']
    if len(missing_names) > 0:
        print("\nNames in population data that don't match age data:")
        for name in missing_names:
            print(f"- {name}")

    # Define age columns
    age_columns = ['all', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                   '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', 
                   '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', 
                   '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', 
                   '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', 
                   '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', 
                   '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', 
                   '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', 
                   '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90+']

    # Create scaled DataFrame
    scaled_df = age_initial.copy()

    # Scale values only for matching names
    for idx, row in df.iterrows():
        mask = age_initial['name'] == row['name']
        if mask.any():
            ratio = row['population'] / age_initial.loc[mask, 'all'].values[0]
            scaled_df.loc[mask, age_columns] = age_initial.loc[mask, age_columns] * ratio

    # Verification of scaling
    print("\nScaling Verification (first few areas):")
    print("Area name | Original total | New population | Scaled total | Original age 0 | Scaled age 0")
    print("-" * 90)
    
    for idx, row in df.head().iterrows():
        mask = scaled_df['name'] == row['name']
        if mask.any():
            original_total = age_initial.loc[age_initial['name'] == row['name'], 'all'].values[0]
            original_age_0 = age_initial.loc[age_initial['name'] == row['name'], '0'].values[0]
            scaled_total = scaled_df.loc[mask, 'all'].values[0]
            scaled_age_0 = scaled_df.loc[mask, '0'].values[0]
            
            print(f"{row['name']:<25} | "
                  f"{original_total:>13,.2f} | "
                  f"{row['population']:>13,.2f} | "
                  f"{scaled_total:>12,.2f} | "
                  f"{original_age_0:>13,.2f} | "
                  f"{scaled_age_0:>12,.2f}")

    return scaled_df

scaled_age_data = scale_age_data("Scotland_population.xlsx", "age.csv")
scaled_age_data.to_csv("corrected_age.csv", index=False)