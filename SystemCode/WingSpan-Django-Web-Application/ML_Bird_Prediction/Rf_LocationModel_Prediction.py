import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
import os

def load_and_preprocess_data(Bird_data_path):
    """
    Load data from an Excel file and preprocess it by converting dates
    and encoding categorical variables.
    """
    df = pd.read_excel(Bird_data_path)
    df['Observation_Date'] = pd.to_datetime(df['Observation_Date'])
    df['Day_of_Year'] = df['Observation_Date'].dt.dayofyear
    df['Month'] = df['Observation_Date'].dt.month
    df['Day_of_Week'] = df['Observation_Date'].dt.dayofweek  # Monday=0, Sunday=6

    species_encoder = LabelEncoder()
    location_encoder = LabelEncoder()
    df['Species_encoded'] = species_encoder.fit_transform(df['Species'])
    df['Location_encoded'] = location_encoder.fit_transform(df['Location'])
    
    return df, species_encoder, location_encoder

def predict_future_location(specific_species, future_date, temparature, rf_classifier, species_encoder, location_encoder):
    """
    Predict the location of a specific species on a future date.
    """
    specific_species_encoded = species_encoder.transform([specific_species])[0]
    future_day_of_year = future_date.timetuple().tm_yday
    future_month = future_date.month
    future_day_of_week = future_date.weekday()  # Monday=0, Sunday=6
    
    features_future = [
        specific_species_encoded,
        future_day_of_year,
        future_month,
        future_day_of_week,
        temparature,
    ]
    
    predicted_location_encoded = rf_classifier.predict([features_future])
    predicted_location = location_encoder.inverse_transform(predicted_location_encoded)
    return predicted_location

def predict_location_probability(specific_species, future_date, temparature, rf_classifier, species_encoder, location_encoder):
    """
    Predict the top 5 most probable locations for finding a specific species on a future date,
    along with the associated probabilities.
    """
    specific_species_encoded = species_encoder.transform([specific_species])[0]
    future_day_of_year = future_date.timetuple().tm_yday
    future_month = future_date.month
    future_day_of_week = future_date.weekday()  # Monday=0, Sunday=6
    
    features_future = np.array([
        specific_species_encoded,
        future_day_of_year,
        future_month,
        future_day_of_week,
        temparature,
    ]).reshape(1, -1)
    
    # Using predict_proba to get probabilities for all classes (locations)
    probabilities = rf_classifier.predict_proba(features_future)[0]
    
    # Mapping each probability back to the corresponding location
    locations = location_encoder.inverse_transform(np.arange(len(probabilities)))
    probability_distribution = dict(zip(locations, probabilities))
    
    # Sorting probabilities from highest to lowest and selecting top 5
    sorted_probabilities = sorted(probability_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_probabilities

# Main code
current_directory_path = os.getcwd()
Bird_data_path = current_directory_path + "/ML_Bird_Prediction/Bird_Sighting_and_Weather.xlsx"
df, species_encoder, location_encoder = load_and_preprocess_data(Bird_data_path)