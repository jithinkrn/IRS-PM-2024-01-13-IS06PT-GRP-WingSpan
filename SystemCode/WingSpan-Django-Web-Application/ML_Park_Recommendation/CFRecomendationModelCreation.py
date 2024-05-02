import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from surprise import KNNBasic
from surprise import Dataset
from surprise import accuracy
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise.model_selection import cross_validate
import pickle

from collections import defaultdict


def get_top_n(predictions, n=10):
    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))
    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, bird_count in top_n.items():
        bird_count.sort(key=lambda x: x[1], reverse=True)  # sort on predicted count
        top_n[uid] = bird_count[:n]
    return top_n


# Get the current working directory
current_directory_path = os.getcwd()
print(f"Current directory: {current_directory_path}")

# Construct the full path to the CSV file
data_path = os.path.join(current_directory_path, "Data", "final_count_dataframe.csv")
print(f"Data path: {data_path}")

# Read the CSV file into a DataFrame
bird_count_df = pd.read_csv(data_path, encoding="latin1", dtype=str)

print(bird_count_df)

# convert into Surprise data format
reader = Reader(rating_scale=(1, 10))
data = Dataset.load_from_df(bird_count_df, reader)

trainset, testset = train_test_split(data, test_size=0.1)  # select 10%
print("testset size=", len(testset))
print("trainset type=", type(trainset), "testsettype=", type(testset))
print("birds,parks in trainset=", trainset.n_users, trainset.n_items)

# note that testset is stored as a list, we temporarily convert to dataframe to more easily count users and items
testdf = pd.DataFrame(testset)
print(
    "birds,parks in testset= ",
    len(testdf.iloc[:, 0].unique()),
    len(testdf.iloc[:, 1].unique()),
)
del testdf
# w view a sample of the testset
print("testset sample=", testset[0:3])

# Apply basic user-based CF and then compute MAE on the testset

algo = KNNBasic(
    k=40, sim_options={"name": "cosine", "user_based": True}
)  # User-based CF
algo.fit(trainset)
preds = algo.test(testset)
accuracy.rmse(preds)
accuracy.mae(preds)

# 5-fold cross-validation.
res = cross_validate(algo, data, measures=["RMSE", "MAE"], cv=5, verbose=True)

# now pick a target user (any user is OK)
birdname = "Barred Eagle-Owl"

# Fetch all unique park IDs from the dataset
parks = bird_count_df["park"].unique()


# Function to predict count for a given bird across all parks
def predict_parks_for_bird(bird_name):
    predictions = []
    for park in parks:
        # Predict the bird count for each park
        pred = algo.predict(uid=bird_name, iid=park)
        predictions.append((park, pred.est))

    # Sort predictions by estimated count in descending order
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions


# Use the function to get predictions
predicted_bird_count = predict_parks_for_bird("Lesser Frigatebird")

# Display the top 10 recommended parks for 'Barred Eagle-Owl'
top_10_parks = predicted_bird_count[:10]
print(top_10_parks)

# Your trained model 'algo' is ready to be saved
filename = "ParkRecommendation_CF_model.sav"
with open(filename, "wb") as file:
    pickle.dump(algo, file)
