import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# Obtain the current working directory to construct file paths dynamically
current_directory_path = os.getcwd()
print(f"Current directory: {current_directory_path}")

# Construct the full path to the CSV file storing park and bird data
data_path = os.path.join(current_directory_path, "Data", "final_count_dataframe.csv")
print(f"Data path: {data_path}")

# Load and preprocess the data from CSV
data = pd.read_csv(data_path, encoding="latin1", dtype=str)
data['bird'] = data['bird'].str.strip()  # Remove any leading/trailing whitespace
data.drop_duplicates(subset=['bird', 'park'], inplace=True)  # Remove duplicate entries

# Function to process data into a suitable format for similarity calculations
'''
def process_data(df):
    # Group data by 'Location' and aggregate 'Species' into sets
    grouped = df.groupby('Location')['Species'].apply(set).reset_index()
    mlb = MultiLabelBinarizer()  # Initialize the binarizer
    matrix = mlb.fit_transform(grouped['Species'])  # Transform species sets into binary matrix format
    return grouped['Location'], matrix, mlb, mlb.classes_
'''
def process_data(df):
    # Group data by 'Location' and aggregate 'Species' into sets
    grouped = df.groupby('park')['bird'].apply(set).reset_index()
    mlb = MultiLabelBinarizer()  # Initialize the binarizer
    matrix = mlb.fit_transform(grouped['bird'])  # Transform species sets into binary matrix format
    boolean_matrix = matrix.astype(bool)  # Convert to boolean explicitly to avoid warnings
    return grouped['park'], boolean_matrix, mlb, mlb.classes_


# Split data into training and testing sets to validate the model
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
train_locations, train_matrix, mlb, species_classes = process_data(train_data)
# Function to recommend parks based on a specific bird using Jaccard similarity
def recommend_parks_for_bird(bird_name, mlb, train_matrix, train_locations):
    bird_index = list(mlb.classes_).index(bird_name)
    bird_vector = np.zeros((1, len(mlb.classes_)))
    bird_vector[0, bird_index] = 1  # Set the bird presence to 1
    similarity_matrix = 1 - pairwise_distances(bird_vector, train_matrix, metric='jaccard')  # Using Jaccard similarity
    recommendation_indices = np.argsort(-similarity_matrix, axis=1)[:, :3]  # Top 3 recommendations
    return [train_locations[i] for i in recommendation_indices[0]]

# Example usage for a specific bird
bird_name = "Amur Stonechat"  # Change this to the bird you're interested in
recommended_parks = recommend_parks_for_bird(bird_name, mlb, train_matrix, train_locations)
print(f"Top 3 recommended parks for {bird_name}:", recommended_parks)

# Evaluate recommendations for a specific bird
def evaluate_specific_bird_recommendations(recommended_parks, bird_name, train_data):
    true_parks = set(train_data[train_data['bird'].str.contains(bird_name, na=False)]['park'].unique())
    predicted_parks = set(recommended_parks)
    true_positive = predicted_parks.intersection(true_parks)
    precision = len(true_positive) / len(predicted_parks) if predicted_parks else 0
    recall = len(true_positive) / len(true_parks) if true_parks else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0
    return precision, recall, f1

# Calculate metrics for the specific bird recommendations
precision, recall, f1 = evaluate_specific_bird_recommendations(recommended_parks, bird_name, train_data)
print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}")
