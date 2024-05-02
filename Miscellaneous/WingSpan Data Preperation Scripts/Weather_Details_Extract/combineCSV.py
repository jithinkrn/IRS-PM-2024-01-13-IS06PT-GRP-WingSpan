import os
import pandas as pd

# Function to combine CSV files in a folder into one Excel sheet
def combine_csv_to_excel(folder_path, output_excel_file):
    # Get list of CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the folder.")
        return
    
    # Initialize an empty list to store DataFrames
    dataframes = []
    
    # Iterate through each CSV file
    for file in csv_files:
        # Read CSV file into a DataFrame
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        
        # Append DataFrame to dataframes list
        dataframes.append(df)
    
    # Concatenate all DataFrames into one
    combined_data = pd.concat(dataframes, ignore_index=True)
    
    # Write combined data to Excel file
    combined_data.to_excel(output_excel_file, index=False)
    print("Combined data has been written to", output_excel_file)

# Folder containing CSV files
folder_path = '/Users/ms/Desktop/WeatherCSVFIles'

# Output Excel file
output_excel_file = 'combined_data.xlsx'

# Call the function to combine CSV files into Excel
combine_csv_to_excel(folder_path, output_excel_file)


# Folder containing CSV files
#folder_path = '/Users/ms/Desktop/MTech Intelligent Systems/Intelligent Reasoning Systems/Project/WeatherCSVFIles'

# Output Excel file
#output_excel_file = 'combined_data.xlsx'

# Call the function to combine CSV files into Excel
#combine_csv_to_excel(folder_path, output_excel_file)
#