import pandas as pd

data = pd.read_csv('data.csv')

# Grouping data by 'Replaced Location' and 'Week' and counting unique species
species_count = data.groupby(['Replaced Location', 'Week'])['Species'].nunique().reset_index()

# Saving the aggregated data to a new Excel file
species_count.to_excel('species_count.xlsx', index=False)
