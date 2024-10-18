import pandas as pd

file_path = 'textbook/data/MSW_2023_Data_Tables.xlsx'
sheet_name = 'Age'  

df = pd.read_excel(file_path, sheet_name=sheet_name, header=3, usecols='A:H', nrows=72)
continents_df = pd.read_csv('textbook/data/continents.csv')

# pivot columns 2 to 7 as age groups

df = df.rename(columns={'Country/Region': 'country'})

df = df.melt(id_vars=['country'], var_name='age_group', value_name='MHQ_score')

continents_df = continents_df.drop(columns=['alpha-2', 'country-code', 'iso_3166-2', 'intermediate-region', 'region-code', 'sub-region-code', 'intermediate-region-code', 'alpha-3', 'sub-region'])

merged_df = df.merge(continents_df, left_on='country', right_on='name', how='inner')

merged_df = merged_df.drop(columns=['name'])

output_path = 'textbook/data/MH_data_processed_3.csv'
merged_df.to_csv(output_path, index=False)

print(f"Data has been saved to {output_path}.")