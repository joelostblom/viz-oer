import pandas as pd

def main():
    faostat_data = pd.read_csv('data/FAOSTAT_data_en_8-2-2024.csv')
    food_production_data = pd.read_csv('data/Food_Production.csv')

    mapping_dict = {
        'Wheat and products': 'Wheat & Rye (Bread)',
        'Maize and products': 'Maize (Meal)',
        'Barley and products': 'Barley (Beer)',
        'Oats': 'Oatmeal',
        'Rice (Milled Equivalent)': 'Rice',
        'Potatoes and products': 'Potatoes',
        'Cassava and products': 'Cassava',
        'Sugar (Raw Equivalent)': 'Cane Sugar',
        'Sweeteners, Other': 'Beet Sugar',
        'Pulses, Other and products': 'Other Pulses',
        'Peas': 'Peas',
        'Nuts and products': 'Nuts',
        'Groundnuts (Shelled Eq)': 'Groundnuts',
        'Soyabean Oil': 'Soybean Oil',
        'Palm Oil': 'Palm Oil',
        'Sunflowerseed Oil': 'Sunflower Oil',
        'Rape and Mustard Oil': 'Rapeseed Oil',
        'Olive Oil': 'Olive Oil',
        'Tomatoes and products': 'Tomatoes',
        'Onions': 'Onions & Leeks',
        'Roots, Other': 'Root Vegetables',
        'Vegetables, other': 'Other Vegetables',
        'Bananas': 'Bananas',
        'Apples and products': 'Apples',
        'Grapes and products (excl wine)': 'Berries & Grapes',
        'Wine': 'Wine',
        'Fruits, other': 'Other Fruit',
        'Coffee and products': 'Coffee',
        'Cocoa Beans and products': 'Dark Chocolate',
        'Bovine Meat': 'Beef (beef herd)',
        'Mutton & Goat Meat': 'Lamb & Mutton',
        'Pigmeat': 'Pig Meat',
        'Poultry Meat': 'Poultry Meat',
        'Milk - Excluding Butter': 'Milk',
        'Cheese': 'Cheese',
        'Eggs': 'Eggs',
        'Freshwater Fish': 'Fish (farmed)',
        'Crustaceans': 'Shrimps (farmed)'
    }

    unique_mappings = {k: v for k, v in mapping_dict.items() if list(mapping_dict.values()).count(v) == 1}

    faostat_data['Mapped_Item'] = faostat_data['Item'].map(unique_mappings)
    faostat_data.dropna(subset=['Mapped_Item'], inplace=True)

    merged_data = pd.merge(faostat_data, food_production_data, left_on='Mapped_Item', right_on='Food product', how='inner')

    columns_to_keep = ['Mapped_Item', 'Value', 'Total_emissions']
    merged_data = merged_data[columns_to_keep]

    merged_data.columns = ['Food Item', 'Total Food Supply (kg/capita/yr)', 'Emissions (Kg CO2 / kg product)']

    aggregated_data = merged_data.groupby('Food Item').agg({
        'Total Food Supply (kg/capita/yr)': 'sum',
        'Emissions (Kg CO2 / kg product)': 'sum'
    }).reset_index()

    aggregated_data.to_csv('data/aggregated_food_data.csv', index=False)

if __name__ == "__main__":
    main()