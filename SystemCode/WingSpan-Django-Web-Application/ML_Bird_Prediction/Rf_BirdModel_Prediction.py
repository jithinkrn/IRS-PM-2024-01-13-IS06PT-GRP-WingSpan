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
    hotspot_encoder = LabelEncoder()
    df['Species_encoded'] = species_encoder.fit_transform(df['Species'])
    df['Location_encoded'] = location_encoder.fit_transform(df['Location'])
    df['Hotspot_encoded'] = hotspot_encoder.fit_transform(df['Mapped_Station'])
    
    return df, species_encoder, location_encoder, hotspot_encoder

def predict_bird(specific_location, future_date, temperature, windspeed, winddir, visibility, cloudcover, specific_hotspot, rf_classifier, species_encoder, location_encoder, hotspot_encoder):
    """
    Predict the Bird based on the location on a future date.
    """
    specific_location_encoded = location_encoder.transform([specific_location])[0]
    future_day_of_year = future_date.timetuple().tm_yday
    future_month = future_date.month
    specific_hotspot_encoded = hotspot_encoder.transform([specific_hotspot])[0]
    future_day_of_week = future_date.weekday()  # Monday=0, Sunday=6
    
    features_future = [
        specific_location_encoded,
        future_day_of_year,
        future_month,
        temperature,
        windspeed, 
        winddir,
        visibility,
        specific_hotspot_encoded,
        cloudcover,
    ]
    
    predicted_bird_encoded = rf_classifier.predict([features_future])
    predicted_bird = species_encoder.inverse_transform(predicted_bird_encoded)
    return predicted_bird

def predict_bird_probability(specific_location, future_date, temperature, windspeed, winddir, visibility, cloudcover, specific_hotspot, rf_classifier, species_encoder, location_encoder, hotspot_encoder):
    """
    Predict the top 5 most probable birds for finding in a specific location on a future date,
    along with the associated probabilities.
    """
    specific_location_encoded = location_encoder.transform([specific_location])[0]
    future_day_of_year = future_date.timetuple().tm_yday
    future_month = future_date.month
    specific_hotspot_encoded = hotspot_encoder.transform([specific_hotspot])[0]
    future_day_of_week = future_date.weekday()  # Monday=0, Sunday=6
    
    features_future = np.array([
        specific_location_encoded,
        future_day_of_year,
        future_month,
        temperature,
        windspeed, 
        winddir,
        visibility,
        specific_hotspot_encoded,
        cloudcover,
    ]).reshape(1, -1)
    
    # Using predict_proba to get probabilities for all classes (birds)
    probabilities = rf_classifier.predict_proba(features_future)[0]
    
    # Mapping each probability back to the corresponding bird
    birds = species_encoder.inverse_transform(np.arange(len(probabilities)))
    probability_distribution = dict(zip(birds, probabilities))
    
    # Sorting probabilities from highest to lowest and selecting top 5
    sorted_probabilities = sorted(probability_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
    return sorted_probabilities
    
# Main code
current_directory_path = os.getcwd()
Bird_data_path = current_directory_path + "/ML_Bird_Prediction/Bird_Sighting_and_Weather.xlsx"
df, species_encoder, location_encoder, hotspot_encoder = load_and_preprocess_data(Bird_data_path)