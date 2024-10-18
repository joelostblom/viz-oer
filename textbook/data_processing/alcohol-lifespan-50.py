import pandas as pd

life_expectancy_df = pd.read_csv('textbook/data/life-expectancy-hmd-unwpp.csv')
alcohol_df = pd.read_csv('textbook/data/IHME-GBD_2021_DATA-446de514-1.csv')
life_span_50_df = pd.read_csv('textbook/data/IHME-GBD_2021_DATA-6b19deba-1.csv')

life_expectancy_df = life_expectancy_df.query('Year == 2021')
life_expectancy_df = life_expectancy_df.rename(columns={
    'Entity': 'country', 
    'Life expectancy - Type: period - Sex: both - Age: 0': 'average_life_expectancy', 
    'Code': 'code'
})
life_expectancy_df = life_expectancy_df.drop(columns=['Year'])

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

def process_dataset(df, value_column_name):
    df = df.drop(columns=['year', 'measure', 'sex', 'age', 'upper', 'lower', 'metric'])
    df = df.rename(columns={'location': 'country', 'val': value_column_name})
    
    for pattern, replacement in country_name_replacements.items():
        df['country'] = df['country'].str.replace(pattern, replacement, regex=True)
    
    df = df[~df['country'].str.contains('income')]
    df = df[~df['country'].str.contains('regions')]
    
    return df

alcohol_df = process_dataset(alcohol_df, 'percentage_heavy_drinkers')

life_span_50_df = process_dataset(life_span_50_df, 'life_expectancy_at_50')  # Adjust 'life_expectancy_at_50' to the appropriate column name

merged_df = life_expectancy_df.merge(alcohol_df, on='country', how='inner')
merged_df = merged_df.merge(life_span_50_df, on='country', how='inner')

continents_df = pd.read_csv('textbook/data/continents.csv')
continents_df = continents_df.drop(columns=['alpha-2', 'country-code', 'iso_3166-2', 'intermediate-region', 'region-code', 'sub-region-code', 'intermediate-region-code', 'name'])

merged_df_with_continents = merged_df.merge(continents_df, left_on='code', right_on='alpha-3', how='inner')
merged_df_with_continents = merged_df_with_continents.drop(columns=['alpha-3'])

merged_df_with_continents['percentage_heavy_drinkers'] *= 100

merged_df_with_continents['average_life_expectancy'] = merged_df_with_continents['average_life_expectancy'].round(2)
merged_df_with_continents['percentage_heavy_drinkers'] = merged_df_with_continents['percentage_heavy_drinkers'].round(2)
merged_df_with_continents['life_expectancy_at_50'] = merged_df_with_continents['life_expectancy_at_50'].round(2)

income_df = pd.read_excel('../data/world_bank_income.xlsx')
income_df = income_df.rename(columns={'Code': 'code', 'Income group': 'income_group'})
income_df = income_df[['code', 'income_group']]

merged_df_with_continents_income = pd.merge(income_df, merged_df_with_continents, on='code')

income_order = ['Low income', 'Lower middle income', 'Upper middle income', 'High income']
numbered_labels = {income: f"{i+1}. {income}" for i, income in enumerate(income_order)}

merged_df_with_continents_income['income_group'] = merged_df_with_continents_income['income_group'].map(numbered_labels)

merged_df.to_csv('../data/income_lifeexp_alcohol_1.csv', index=False)