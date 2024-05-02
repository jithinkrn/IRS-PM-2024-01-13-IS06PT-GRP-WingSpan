from rest_framework.response import Response
import time
from openai import OpenAI
import re
import pandas as pd
import os
from datetime import datetime, timedelta
import ML_Bird_Prediction.Rf_BirdModel_Prediction as ml_bird
import joblib
from datetime import date
import ML_Bird_Prediction.fetch_singapore_weather as fetchWeather
import warnings
from django.conf import settings
import gzip


warnings.filterwarnings("ignore")


class BirdPredictionBot:

    def __init__(self):
        self.chat_response = ""
        self.state = "Spotting Prediction"
        self.client = OpenAI()
        self.ASSISTANT_ID = "asst_aRqNS4vVODlZ1Pka4ytJtHh1"
        self.identified_location = None
        self.identified_date = None

        Bird_data = os.path.join(
            settings.MODELS_ROOT_PRED, "Bird_Sighting_and_Weather.xlsx"
        )
        self.model_path = os.path.join(
            settings.MODELS_ROOT_PRED, "Models", "rf_bird_classifier.joblib.gz"
        )

        self.hotspot_regions_path = os.path.join(
            settings.MODELS_ROOT_PRED, "Data", "Location_and_Hotspot_region_map.xlsx"
        )

        self.df = pd.read_excel(Bird_data)
        self.df_retrieve_hotspot = pd.read_excel(self.hotspot_regions_path)
        self.valid_locations = self.df["Location"].unique().tolist()

        # retrieve weather info
        self.get_tempmax = None
        self.get_windspeed = None
        self.get_winddir = None
        self.get_visibility = None
        self.get_cloudcover = None
        self.mapped_station = None

    def talk_to_assistant(self, user_query):
        try:
            # Create a thread with the user's message
            thread = self.client.beta.threads.create(
                messages=[{"role": "user", "content": user_query}]
            )

            # Submit the thread to the assistant (as a new run) with your assistant ID
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=self.ASSISTANT_ID
            )

            # Wait for the run to complete
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                time.sleep(1)

            # Get the latest message from the thread
            message_response = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            messages = message_response.data
            latest_message = messages[0].content[0].text.value
            return latest_message

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."

    def extract_location_info(self, chat_response):
        identified_locations = []
        identified_locations_combined = None

        # Crucial part - extraction based on word count, case sensitivity, multiple and no occurences
        for location in self.valid_locations:
            pattern = r"\b" + re.escape(location) + r"\b"
            if re.search(pattern, chat_response):
                identified_locations.append(location)

        sorted_locations = sorted(
            identified_locations, key=lambda loc: len(loc.split()), reverse=True
        )
        if sorted_locations:
            highest_word_count = len(sorted_locations[0].split())
            sorted_locations = [
                loc
                for loc in sorted_locations
                if len(loc.split()) == highest_word_count
            ]

        if sorted_locations:
            if len(sorted_locations) > 1:
                identified_locations_combined = ", ".join(sorted_locations)
                self.chat_response = (
                    f"Multiple locations have been identified: {identified_locations_combined}. "
                    "Could you please specify a specific location?"
                )
                return False
            if len(sorted_locations) == 1:
                self.identified_location = sorted_locations[0]
                return True
        else:
            self.chat_response = (
                "The location you've mentioned isn't recognized in our database. "
                "Could you please specify a known location?"
            )
            return False

    def extract_date_info(self, chat_response):
        date_pattern = r"(\d{4}/\d{2}/\d{2})"
        date_match = re.search(date_pattern, chat_response)
        if date_match:
            self.identified_date = date_match.group(
                1
            )  # Extract the matched date string
            self.chat_response = "Great, thanks for providing the date information! I'll now proceed to use \
                                    my machine learning model to determine the likelihood of spotting the bird species."
            return True
        else:
            self.chat_response = "Could you help us in providing a valid date ?"
            return False

    def extract_other_details(self, identified_location, identified_date):

        try:
            todays_date = date.today()
            user_date = str(
                identified_date
            )  # Make sure 'identified_date' is defined prior to this line
            current_date = str(todays_date)

        except Exception as e:
            print(f"A date related error occurred : {e}")

        # Converting to datetime objects
        try:

            user_date = datetime.strptime(user_date, "%Y/%m/%d")
            current_date = datetime.strptime(current_date, "%Y-%m-%d")

        except Exception as e:
            print(f"An error occurred on converting user date: {e}")

        # Calculate the difference in days
        days_difference = (user_date - current_date).days

        # Check if the extracted date is within 15 days from today's date
        if 0 <= days_difference <= 15:
            # print("Processing using live API")
            if user_date.date() == current_date.date():
                today_time = datetime.now()
                current_time = today_time.strftime("%H:%M:%S")  # Current time
                try:
                    fetchWeather.fetch_and_store_current_weather(
                        user_date, current_time
                    )
                except Exception as e:
                    print(f"An at weather API: {e}")
                self.get_tempmax = fetchWeather.fetch_temperature
                self.get_windspeed = fetchWeather.fetch_wind_speed
                self.get_winddir = fetchWeather.fetch_wind_direction
                self.get_visibility = fetchWeather.fetch_visibility
                self.get_cloudcover = fetchWeather.fetch_cloud_cover
            elif (
                user_date.date() > current_date.date()
                and user_date <= current_date + timedelta(days=15)
            ):
                current_time = "17:00:00"  # 5 PM for future dates within 15 days
                try:
                    fetchWeather.fetch_and_store_future_weather(user_date, current_time)
                except Exception as e:
                    print(f"An at weather API: {e}")
                self.get_tempmax = fetchWeather.fetch_temperature
                self.get_windspeed = fetchWeather.fetch_wind_speed
                self.get_winddir = fetchWeather.fetch_wind_direction
                self.get_visibility = fetchWeather.fetch_visibility
                self.get_cloudcover = fetchWeather.fetch_cloud_cover
        else:
            # Create the date from which weather data needs to be extracted
            # print("Processing using past records")
            weather_year = 2023  # based on previous records else can keep (current_date.year - 1) in case data has been updated
            weather_date = user_date.replace(year=weather_year)

            self.df["Observation_Date"] = pd.to_datetime(self.df["Observation_Date"])

            # Attempt to retrieve the weather details from the previous records
            tempmax_value = self.df.loc[
                self.df["Observation_Date"] == weather_date, "tempmax"
            ].values
            windspeed_value = self.df.loc[
                self.df["Observation_Date"] == weather_date, "windspeed"
            ].values
            winddir_value = self.df.loc[
                self.df["Observation_Date"] == weather_date, "winddir"
            ].values
            visibility_value = self.df.loc[
                self.df["Observation_Date"] == weather_date, "visibility"
            ].values
            cloudcover_value = self.df.loc[
                self.df["Observation_Date"] == weather_date, "cloudcover"
            ].values

            # Extract the values if available, else set to 0
            self.get_tempmax = tempmax_value[0] if len(tempmax_value) > 0 else 0
            self.get_windspeed = windspeed_value[0] if len(windspeed_value) > 0 else 0
            self.get_winddir = winddir_value[0] if len(winddir_value) > 0 else 0
            self.get_visibility = (
                visibility_value[0] if len(visibility_value) > 0 else 0
            )
            self.get_cloudcover = (
                cloudcover_value[0] if len(cloudcover_value) > 0 else 0
            )

        self.mapped_station = self.df_retrieve_hotspot[
            self.df_retrieve_hotspot["Bird_Location"] == identified_location
        ]["Bird_Station"].values[0]

        # Uncomment to verify
        print("Temp: ", self.get_tempmax)
        print("WindSpeed: ", self.get_windspeed)
        print("WindDir: ", self.get_winddir)
        print("Visibility: ", self.get_visibility)
        print("Cloudcover: ", self.get_cloudcover)
        print("Mapped_station: ", self.mapped_station)

    def extract_information(self, message, conversation_history):
        extended_prompt = f"When you receive a message like: '{message}'; your task is to assess whether it's aimed at predicting \
                            the sighting of a certain bird species at a given location on a certain date. Your inputs for making this \
                            prediction will be the location and date provided in the query. Your objective is to identify which bird \
                            species might be spotted at the specified location on the given date. If the query explicitly outlines \
                            this goal, please respond in the following format: \
                            Answer: [Yes - Bird prediction, Location - (the extracted location from the message), Date - (the extracted date from the message in yyyy/mm/dd format)]. \
                            This format confirms the intent to predict the presence of a bird species at a particular place and time. \
                            If the query seems to be different unrelated to prediction, please specify what additional \
                            details or assistance is required for the prediction of birds. \
                            \n Ensure our interaction is grounded and straightforward to allow for accurate information exchange. \
                            Please avoid directly mentioning document names or my message in your responses, aiming for a natural dialogue flow. \
                            You need to respond with \
                            Answer: [Yes - Bird prediction, Location - (the specified location), Date - (the specified date)] only if the \
                            query provides all necessary details in the mentioned format. Take Conversation history: {conversation_history} into consideration \
                            to understand, learn and show the correct 'Answer' \
                            \n Location: Report the location extracted from the query, adhering to the exact phrasing provided, as it is case-sensitive. \
                            Date: If a complete date (year, month, day) is provided in the query, respond in the yyyy/mm/dd format. \
                            It's vital that your response precisely follows this format. Also consider the case, where if the user asks like today or tomorrow \
                            , then try to retrieve the respective current date using the online info (in the format of yyyy/mm/dd). \
                            \n If you encounter issues extracting the complete date, or if you only find partial date information, \
                            please request further clarity so the full date can be provided. Similarly, if determining the location from \
                            the query is challenging, ask for more detailed location information. "
        self.chat_response = self.talk_to_assistant(extended_prompt)
        # print(self.chat_response) #uncomment for debug purpose

        # To deal with the information extraction
        if (("Yes" or "yes") in self.chat_response) and (
            "Bird prediction" in self.chat_response
        ):
            if self.extract_location_info(self.chat_response):
                if self.extract_date_info(self.chat_response):
                    # print(self.identified_location)
                    # print(self.identified_date)
                    self.extract_other_details(
                        self.identified_location, self.identified_date
                    )
                    location = self.identified_location
                    future_date = datetime.strptime(self.identified_date, "%Y/%m/%d")
                    try:
                        with gzip.open(self.model_path, "rb") as f:
                            rf_classifier_model = joblib.load(f)

                        print("After load")
                    except Exception as e:
                        print(f"Error when loading model {e}")

                    try:
                        warnings.filterwarnings(
                            "ignore",
                            message="X does not have valid feature names, but RandomForestClassifier was fitted with feature names",
                        )
                        predicted_bird = ml_bird.predict_bird(
                            location,
                            future_date,
                            self.get_tempmax,
                            self.get_windspeed,
                            self.get_winddir,
                            self.get_visibility,
                            self.get_cloudcover,
                            self.mapped_station,
                            rf_classifier_model,
                            ml_bird.species_encoder,
                            ml_bird.location_encoder,
                            ml_bird.hotspot_encoder,
                        )

                    except Exception as e:
                        print(f"Error when predicting bird {e}")

                    try:
                        warnings.filterwarnings(
                            "ignore",
                            message="X does not have valid feature names, but RandomForestClassifier was fitted with feature names",
                        )

                        sorted_probabilities = ml_bird.predict_bird_probability(
                            location,
                            future_date,
                            self.get_tempmax,
                            self.get_windspeed,
                            self.get_winddir,
                            self.get_visibility,
                            self.get_cloudcover,
                            self.mapped_station,
                            rf_classifier_model,
                            ml_bird.species_encoder,
                            ml_bird.location_encoder,
                            ml_bird.hotspot_encoder,
                        )

                    except Exception as e:
                        print(f"Error when predicting bird_probability {e}")

                    # Uncomment the below section for debug purpose
                    print(
                        f"Predicted bird for {location} on {future_date}: {predicted_bird}"
                    )
                    print(
                        f"Other Top 5 most probable birds for {location} on {future_date} are:"
                    )
                    for bird, probability in sorted_probabilities:
                        print(f"{bird}: {probability:.2f}")

                    self.chat_response += f"\nPredicted bird for {location} on {future_date}: {predicted_bird[0]}\n"
                    self.chat_response += f"Other Top 5 most probable birds for {location} on {future_date} are:\n"
                    for bird, probability in sorted_probabilities:
                        self.chat_response += f"{bird}: {probability:.2f}\n"
                    self.identified_location = None
                    self.identified_date = None
                    self.get_tempmax = None
                    self.get_windspeed = None
                    self.get_winddir = None
                    self.get_visibility = None
                    self.get_cloudcover = None
                    self.mapped_station = None

    def handle_message(self, request):
        conversation_history_all = request.session.get("conversation_history", [])
        conversation_history = conversation_history_all[-10:]
        try:
            user_query = request.data.get("query", "")
            # From Bird Prediction state to extracting the information
            if self.state == "Spotting Prediction":
                self.extract_information(user_query, conversation_history)
                print(self.chat_response)
                return {"response": self.chat_response}

            else:
                return {
                    "response": "Please provide more information on what sort of prediction needs to be implemented"
                }

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."
