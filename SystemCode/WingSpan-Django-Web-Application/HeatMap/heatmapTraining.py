import pandas as pd
from sklearn.model_selection import train_test_split
#from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression

from sklearn.ensemble import RandomForestClassifier
# import joblib
from sklearn.metrics import accuracy_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

# Read the data
data = pd.read_csv('./PreprocessData/species_count.csv')  

# Calculate Euclidean distance
data['Distance'] = ((data['Latitude'] - data['Longitude'])**2)**0.5

# Define features and target
X = data[['Distance', 'Week']]  # Features
y = data['Count']  # Target


# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Initialize a dictionary to store models
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest Regressor": RandomForestRegressor(),
    "Gradient Boosting Regressor": GradientBoostingRegressor(),
    "SVR": SVR(),
    "K-Nearest Neighbors Regressor": KNeighborsRegressor(n_neighbors=5, weights='distance')
}

# Train and evaluate each model
results = {}
for name, model in models.items():
    # Fit the model with training data
    model.fit(X_train, y_train)
    # Predictions
    y_pred = model.predict(X_test)
    # Calculate mean squared error
    mse = mean_squared_error(y_test, y_pred)
    r_squared = model.score(X_test, y_test)
    # Store MSE in results dictionary
    results[name] = mse
    

# Print results
print("Mean Squared Errors:")

for name, mse in results.items():
    print(f"{name}: {mse}")

# Train and evaluate each model
results = {}
for name, model in models.items():
    # Fit the model with training data
    model.fit(X_train, y_train)
    # Predictions
    y_pred = model.predict(X_test)
    # Calculate R-squared
    r_squared = model.score(X_test, y_test)
    # Store R-squared in results dictionary
    results[name] = r_squared

# Print results
print("R-squared:")
for name, r_squared in results.items():
    print(f"{name}: {r_squared}")


# Train and evaluate each model
results = {}
for name, model in models.items():
    # Fit the model with training data
    model.fit(X_train, y_train)
    # Predictions
    y_pred = model.predict(X_test)
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    # Store accuracy in results dictionary
    results[name] = accuracy

# Print results
print("Accuracy:")
for name, accuracy in results.items():
    print(f"{name}: {accuracy}")



# model_gb = GradientBoostingRegressor(random_state=42)
# model_gb.fit(X_train, y_train)

# # Save the trained model to a file
# joblib.dump(model_gb, 'gradient_boosting_regressor_model.pkl')