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
import joblib

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
    df['Hotspot_encoded'] = location_encoder.fit_transform(df['Mapped_Station'])
    
    return df, species_encoder, location_encoder, hotspot_encoder

def train_random_forest_classifier(X_train, y_train):
    """
    Train a Random Forest Classifier with the training data.
    """
    rf_classifier = RandomForestClassifier(n_estimators=300, random_state=42, max_depth=None, max_features='sqrt', min_samples_leaf=1, min_samples_split=10)
    # rf_classifier = RandomForestClassifier(n_estimators=300, random_state=42, max_depth=10, max_features='sqrt', min_samples_leaf=2, min_samples_split=5)
    rf_classifier.fit(X_train, y_train)
    return rf_classifier

def plot_species_distribution(df):
    """
    Plot the distribution of species in the dataset.
    """
    df['Species'].value_counts().plot(kind='bar')
    plt.title('Species Distribution')
    plt.xlabel('Species')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.show()

def plot_location_distribution(df):
    """
    Plot the distribution of locations in the dataset.
    """
    df['Location'].value_counts().plot(kind='bar')
    plt.title('Location Distribution')
    plt.xlabel('Location')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.show()

def plot_feature_importances(rf_classifier, features):
    """
    Plot the importance of features used by the Random Forest Classifier.
    """
    importances = rf_classifier.feature_importances_
    indices = np.argsort(importances)
    plt.title('Feature Importances in Bird Prediction')
    plt.barh(range(len(indices)), importances[indices], color='b', align='center')
    plt.yticks(range(len(indices)), [features[i] for i in indices])
    plt.xlabel('Relative Importance')
    plt.show()

def plot_sightings_per_month(df):
    """
    Plot the number of bird sightings per month.
    """
    df.groupby('Month')['Species'].count().plot(kind='bar')
    plt.title('Number of Sightings per Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Sightings')
    plt.show()

# Main code
current_directory_path = os.getcwd()
Bird_data_path = current_directory_path + "/Bird_Sighting_and_Weather.xlsx"
df, species_encoder, location_encoder, hotspot_encoder = load_and_preprocess_data(Bird_data_path)
X = df[['Location_encoded', 'Day_of_Year', 'Month', 'tempmax', 'windspeed', 'winddir', 'visibility', 'Hotspot_encoded', 'cloudcover']]
y = df['Species_encoded']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=40)

rf_classifier = train_random_forest_classifier(X_train, y_train)

current_directory_path = os.getcwd()
model_path = os.path.join(current_directory_path + "/Models/", 'rf_bird_classifier.joblib')
joblib.dump(rf_classifier, model_path)

# Uncomment to use
# plot_species_distribution(df)
# plot_location_distribution(df)
# plot_feature_importances(rf_classifier, X.columns)
# plot_sightings_per_month(df)

y_pred = rf_classifier.predict(X_test)
train_accuracy = accuracy_score(y_train, rf_classifier.predict(X_train))
test_accuracy = accuracy_score(y_test, y_pred)

# Calculate and print training and test accuracies
print(f"Training Accuracy: {train_accuracy:.2f}")
print(f"Test Accuracy: {test_accuracy:.2f}")

# Generate and print classification report
unique_classes = np.unique(np.concatenate((y_test, y_pred)))
target_names = [species_encoder.inverse_transform([cls])[0] for cls in unique_classes]
print(classification_report(y_test, y_pred, target_names=target_names, labels=unique_classes))