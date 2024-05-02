import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np


def preprocess_Data():

    # Get the current working directory
    current_directory_path = os.getcwd()
    print(f"Current directory: {current_directory_path}")

    # Construct the full path to the CSV file
    data_path = os.path.join(
        current_directory_path, "Data", "Park_Recommendation_Data.csv"
    )
    print(f"Data path: {data_path}")

    # Read the CSV file into a DataFrame

    sighting_data = pd.read_csv(data_path, encoding="latin1")
    sighting_data.columns = ["bird", "datetime", "location"]

    # Count the number of sightings per bird per park
    grouped_data = (
        sighting_data.groupby(["bird", "location"]).size().reset_index(name="count")
    )

    # Initialize the MinMaxScaler to scale the counts to a 1-5 range
    scaler = MinMaxScaler(feature_range=(1, 10))

    # Scale the 'count' column
    grouped_data["count"] = scaler.fit_transform(grouped_data[["count"]])

    # Round up to the nearest integer using numpy's ceil function
    grouped_data["count"] = np.ceil(grouped_data["count"])

    # Create the 'bird_count_df' DataFrame with the specified columns
    bird_count_df = grouped_data.copy()
    bird_count_df.columns = ["bird", "park", "count"]

    # Merge the datetime information back into the 'bird_count_df' DataFrame
    bird_count_df = bird_count_df.merge(
        sighting_data[["bird", "location", "datetime"]],
        left_on=["bird", "park"],
        right_on=["bird", "location"],
        how="left",
    )

    # Drop the extra 'location' column
    bird_count_df.drop("location", axis=1, inplace=True)

    # Rename 'datetime' to 'count_datetime' to clarify that it's the datetime for the count
    bird_count_df.rename(columns={"datetime": "count_datetime"}, inplace=True)

    # Print the first few rows of the final DataFrame
    print(bird_count_df.head())

    # Specify the name of the file you want to save it as
    output_file_name = "bird_count_dataframe.csv"

    # Use the current working directory or specify a path where you want to save the CSV
    output_file_path = os.path.join(current_directory_path, output_file_name)

    # Save the DataFrame as a CSV file
    bird_count_df.to_csv(output_file_path, index=False, encoding="utf-8")

    print(f"DataFrame saved as '{output_file_name}' at {output_file_path}")

    # Drop the 'count_datetime' column
    bird_count_df.drop("count_datetime", axis=1, inplace=True)

    # Remove duplicate rows based on 'bird' and 'park'
    bird_count_df.drop_duplicates(subset=["bird", "park"], keep="first", inplace=True)

    # Specify the name of the new file you want to save it as
    final_output_file_name = "final_count_dataframe.csv"

    # Use the current working directory or specify a path where you want to save the CSV
    final_output_file_path = os.path.join(
        current_directory_path, "Data", final_output_file_name
    )

    # Save the DataFrame as a CSV file
    bird_count_df.to_csv(final_output_file_path, index=False, encoding="utf-8")

    print(
        f"Final DataFrame saved as '{final_output_file_name}' at {final_output_file_path}"
    )


# main code
preprocess_Data()
