import pandas as pd

def scale_age_data(scotland_pop, age_initial):
    """
    Scale age data based on population data from Scotland_pop.
    
    Args:
        scotland_pop (pd.DataFrame): Population data with code and population
        age_initial (pd.DataFrame): Age distribution DataFrame
    
    Returns:
        pd.DataFrame: Scaled age distribution dataset
    """
    # Define age columns
    age_columns = ['all'] + [str(i) for i in range(90)] + ['90+']

    # Create scaled DataFrame
    scaled_df = age_initial.copy()

    # Scale values using matched codes
    scottish_mask = age_initial['code'].isin(scotland_pop['code'])
    
    # Get scaling data by merging
    scaling_data = age_initial[scottish_mask].merge(scotland_pop[['code', 'population']], on='code')
    
    # Scale each row using population ratios
    for idx, row in scaling_data.iterrows():
        mask = scaled_df['code'] == row['code']
        ratio = row['population'] / row['all']
        scaled_df.loc[mask, age_columns] = age_initial.loc[mask, age_columns] * ratio

    # Verification of scaling (5 areas with lowest population)
    print("\nScaling Verification (5 areas with lowest population):")
    print("Code | Original total | New population | Scaled total | Original age 0 | Scaled age 0")
    print("-" * 90)
    
    for idx, row in scaling_data.sort_values('population').head().iterrows():
        mask = scaled_df['code'] == row['code']
        original_total = age_initial.loc[age_initial['code'] == row['code'], 'all'].values[0]
        original_age_0 = age_initial.loc[age_initial['code'] == row['code'], '0'].values[0]
        scaled_total = scaled_df.loc[mask, 'all'].values[0]
        scaled_age_0 = scaled_df.loc[mask, '0'].values[0]
        
        print(f"{row['code']:<10} | "
              f"{original_total:>13,.2f} | "
              f"{row['population']:>13,.2f} | "
              f"{scaled_total:>12,.2f} | "
              f"{original_age_0:>13,.2f} | "
              f"{scaled_age_0:>12,.2f}")

    return scaled_df

# Run the scaling
age_old = pd.read_csv("age_old.csv")
Scotland_pop = pd.read_csv("Scotland_population.csv")

# Run the scaling
scaled_age_data = scale_age_data(Scotland_pop, age_old)

# Save the results
scaled_age_data.to_csv("age.csv", index=False)