import csv
import requests
import pandas as pd

# File path to the CSV file
csv_file_path = "C:\\IRS\\WingSpan\\Test\\Bird_Information_Testing Results.csv"

# # API endpoint remote
# api_endpoint = "https://wing-span-9a1a4eb79eb0.herokuapp.com/handlerequest/"
# API endpoint local
api_endpoint = "http://127.0.0.1:8000//handlerequest/"

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file_path, encoding="ISO-8859-1")

# List to store responses
responses = []

# Iterate over the rows in the DataFrame and send POST requests
for index, row in df.iterrows():
    query = row["Questions"]
    data = {"query": query}
    response = requests.post(api_endpoint, data=data)
    if response.ok:
        # Save the response content
        responses.append(response.text)
    else:
        # Indicate a failed request
        responses.append("Failed with status code {}".format(response.status_code))

# Save the responses into the 'Model Answers' column
df["Model Answers"] = responses

# Write the updated DataFrame back to a CSV file
df.to_csv(csv_file_path, index=False)

print("Updated CSV file with model answers.")
