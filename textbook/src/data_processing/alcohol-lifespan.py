import pandas as pd

# Load datasets
life_expectancy_df = pd.read_csv('textbook/data/life-expectancy-hmd-unwpp.csv')
alcohol_df = pd.read_csv('textbook/data/IHME-GBD_2021_DATA-446de514-1.csv')

# Filter and rename columns for life expectancy data
life_expectancy_df = life_expectancy_df.query('Year == 2021')
life_expectancy_df = life_expectancy_df.rename(columns={
    'Entity': 'country', 
    'Life expectancy - Type: period - Sex: both - Age: 0': 'average_life_expectancy', 
    'Code': 'code'
})
life_expectancy_df = life_expectancy_df.drop(columns=['Year'])

# Drop unnecessary columns in the alcohol data
alcohol_df = alcohol_df.drop(columns=['year', 'measure', 'sex', 'age', 'rei', 'upper', 'lower', 'metric', 'cause'])
alcohol_df = alcohol_df.rename(columns={'location': 'country', 'val': 'percentage_heavy_drinkers'})

# Create a dictionary to map country name replacements
country_name_replacements = {
    'Islamic Republic of ': '',
    'Republic of ': '',
    'Republic of the ': '',
    'Kingdom of ': '',
    'Kingdom of the ': '',
    'Union of ': '',
    'Union of the ': '',
    'State of ': '',
    'Federal ': '',
    'Principality of ': '',
    "^People's ": '',
    '^Independent ': '',
    '^the ': '',
    'United Tanzania': 'Tanzania',
    'United States of America': 'United States',
    'United Mexican States': 'Mexico',
    'United Great Britain and Northern Ireland': 'United Kingdom',
    'Togolese Republic': 'Togo',
    'Argentine Republic': 'Argentina',
    'Arab Egypt': 'Egypt',
    'Commonwealth of Dominica': 'Dominican Republic',
    'Commonwealth of the Bahamas': 'Bahamas',
    'Czech Republic': 'Czechia',
    'Democratic the Congo': 'Democratic Republic of Congo',
    'Democratic Socialist Sri Lanka': 'Sri Lanka',
    "Democratic People's Korea": 'North Korea',
    'Eastern Uruguay': 'Uruguay',
    'Taiwan (Province of China)': 'Taiwan',
    'Syrian Arab Republic': 'Syria',
    'Swiss Confederation': 'Switzerland',
    'Sultanate of Oman': 'Oman',
    'Socialist Viet Nam': 'Vietnam',
    'Slovak Republic': 'Slovakia',
    'Russian Federation': 'Russia',
    'Portuguese Republic': 'Portugal',
    'Plurinational Bolivia': 'Bolivia',
    "Democratic Algeria": 'Algeria',
    'Lebanese Republic': 'Lebanon',
    "Lao People's Democratic Republic": 'Laos',
    'Kyrgyz Republic': 'Kyrgyzstan',
    'Hellenic Republic': 'Greece',
    'Hashemite Jordan': 'Jordan',
    'Grand Duchy of Luxembourg': 'Luxembourg',
    'Gabonese Republic': 'Gabon',
    'French Republic': 'France',
    'Federative Brazil': 'Brazil',
    'Federated States of Micronesia': 'Micronesia (country)',
    'Democratic Sao Tome and Principe': 'Sao Tome and Principe',
    'Democratic Timor-Leste': 'Timor-Leste',
    'Democratic Nepal': 'Nepal',
    'Democratic Ethiopia': 'Ethiopia',
    'Brunei Darussalam': 'Brunei',
    'Bolivarian Venezuela': 'Venezuela',
    '^Korea': 'South Korea'
}

# Apply the replacements using the dictionary
for pattern, replacement in country_name_replacements.items():
    alcohol_df['country'] = alcohol_df['country'].str.replace(pattern, replacement, regex=True)

# Remove unwanted rows with 'income' or 'regions'
alcohol_df = alcohol_df[~alcohol_df['country'].str.contains('income')]
alcohol_df = alcohol_df[~alcohol_df['country'].str.contains('regions')]

# Merge life expectancy and alcohol consumption data
merged_df = pd.merge(life_expectancy_df, alcohol_df, on='country', how='inner')

# Load and clean continents data
continents_df = pd.read_csv('textbook/data/continents.csv')
continents_df = continents_df.drop(columns=['alpha-2', 'country-code', 'iso_3166-2', 'intermediate-region', 'region-code', 'sub-region-code', 'intermediate-region-code', 'name'])

# Merge with continents data
merged_df_with_continents = pd.merge(merged_df, continents_df, left_on='code', right_on='alpha-3', how='inner')
merged_df_with_continents = merged_df_with_continents.drop(columns=['alpha-3'])

# Multiply percentage_heavy_drinkers by 100
merged_df_with_continents['percentage_heavy_drinkers'] = merged_df_with_continents['percentage_heavy_drinkers'] * 100

# Limit both columns to two decimal places
merged_df_with_continents['average_life_expectancy'] = merged_df_with_continents['average_life_expectancy'].round(2)
merged_df_with_continents['percentage_heavy_drinkers'] = merged_df_with_continents['percentage_heavy_drinkers'].round(2)

# Export to CSV
merged_df_with_continents.to_csv('textbook/data/life_expectancy_alcohol.csv', index=False)