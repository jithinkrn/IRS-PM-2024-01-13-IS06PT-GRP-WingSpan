import time
from openai import OpenAI
import pickle
from django.conf import settings
import os
import pandas as pd

GPT_MODEL = "gpt-4"


# Function to load the trained model
def load_model():

    park_recommendation_model_path = os.path.join(
        settings.MODELS_ROOT_RECOM, "ParkRecommendation_CF_model.sav"
    )

    with open(park_recommendation_model_path, "rb") as file:
        loaded_model = pickle.load(file)
    return loaded_model


# Function to get unique park names from CSV
def get_unique_parks():
    data_path = os.path.join(
        settings.MODELS_ROOT_RECOM, "Data", "final_count_dataframe.csv"
    )
    df = pd.read_csv(data_path)
    unique_parks = (
        df["park"].unique().tolist()
    )  # Ensure column name is 'park' as per your CSV
    return unique_parks


# Function to get unique birds names from CSV
def get_unique_birds():
    data_path = os.path.join(
        settings.MODELS_ROOT_RECOM, "Data", "final_count_dataframe.csv"
    )
    df = pd.read_csv(data_path)
    unique_birds = (
        df["bird"].unique().tolist()
    )  # Ensure column name is 'park' as per your CSV
    return unique_birds


# Function to predict ratings for a given bird across all parks, sorted by rating
def recommend_parks(bird_name, top_n=None):
    parks = get_unique_parks()  # Load park names from CSV
    model = load_model()  # Load your model

    # Predict ratings for each park for the given bird
    predictions = []
    for park in parks:
        pred = model.predict(uid=bird_name, iid=park)
        predictions.append((park, pred.est))

    # Sort predictions by estimated rating in descending order
    predictions.sort(key=lambda x: x[1], reverse=True)

    # Return only top N parks if top_n is specified, else return all
    return predictions[:top_n] if top_n else predictions


class LocationRecommendationBot:

    def __init__(self):
        self.client = OpenAI()

    def talk_to_gpt(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{prompt}",
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"An error occurred: {e}")
            return "Sorry, your request can'be proccessed. Feel free to ask me\
                  anything within my capabilities mentioned earlier"

    def extract_bird_name(self, message, conversation_history):

        bird_list = get_unique_birds()
        extended_prompt = f"Take {message} and Conversation history: {conversation_history} into consideration to understand, which is the bird\
            in the bird in this list {bird_list} user is intrested in. If you can identify, Just give me the bird name only that is in this list {bird_list}\
            without any additional text. Otherwise ask more questions"

        extracted_bird_name = self.talk_to_gpt(extended_prompt)
        return extracted_bird_name

    def formulate_natural_response(self, predictions, conversation_history):

        extended_prompt = f"This output displays predictions from my collaborative filtering model: {predictions}. \
            It lists the top five parks, as previously requested by the user {conversation_history}.\
            Please present these predictions in a clear and natural language format. Don't mention the model used or technical\
            information in your response "

        return_message = self.talk_to_gpt(extended_prompt)
        return return_message

    def handle_message(self, request):

        conversation_history = request.session.get("conversation_history", [])
        conversation_history = conversation_history[-10:]
        try:
            user_query = request.data.get("query", "")
            # From Bird Prediction state to extracting the information
            bird_name = self.extract_bird_name(user_query, conversation_history[-2:])
            # bird_name = "Lesser Frigatebird"
            print("identified bird :" + bird_name)
            if bird_name:
                predictions = recommend_parks(bird_name, top_n=5)
                locations = [location for location, score in predictions]
                print(locations)
                return_message = self.formulate_natural_response(
                    locations, conversation_history
                )
                return {"response": return_message}

            else:
                return {
                    "response": "Please provide the bird name as accurately as you can for me to do park recomendation"
                }

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."
