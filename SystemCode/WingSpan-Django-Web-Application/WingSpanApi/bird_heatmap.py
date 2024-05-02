from rest_framework.response import Response
import time
from openai import OpenAI
import joblib
from datetime import datetime
import os
import pandas as pd
from django.conf import settings
import numpy as np
import plotly.graph_objects as go


class BirdHeatMapBot:

    def __init__(self):
        self.chat_response = ""
        self.client = OpenAI()
        self.ASSISTANT_ID = "asst_irnfPIIMr49e7xiqvaiq54fV"

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

    def handle_message(self, request):

        try:

            user_query = request.data.get("query", "")

            heatmap_model_path = os.path.join(
                settings.MODELS_ROOT, "gradient_boosting_regressor_model.pkl"
            )

            try:
                print("Attempting to load model...")
                model = joblib.load(heatmap_model_path)
                print("Model loaded successfully.")
            except Exception as e:
                print("Error loading model:", e)

            current_week = datetime.now().isocalendar()[1]

            location_list_path = os.path.join(
                settings.BASE_DIR,
                "Data",
                "HeatMap",
                "longitude_latitude.csv",
            )

            latitude_longitude_data = pd.read_csv(location_list_path)

            # # Extract latitude and longitude values
            # latitudes = latitude_longitude_data['Latitude'].tolist()
            # longitudes = latitude_longitude_data['Longitude'].tolist()
            # Get the current week
            current_week = datetime.now().isocalendar()[1]

            # Add the current week to latitude_longitude_data
            latitude_longitude_data["Week"] = current_week

            latitude_longitude_data["Distance"] = (
                (
                    latitude_longitude_data["Latitude"]
                    - latitude_longitude_data["Longitude"]
                )
                ** 2
            ) ** 0.5

            # Define features for prediction (including Latitude, Longitude, and Current_Week)
            features_for_prediction = latitude_longitude_data[["Distance", "Week"]]

            # Create a grid of latitude, longitude, and current week
            # grid = [(lat, long, current_week) for lat, long in zip(latitude_longitude_data['Latitude'], latitude_longitude_data['Longitude'])]

            # Generate predictions for the grid using the trained model
            predicted_counts = model.predict(features_for_prediction)

            # avg_latitude = np.mean([lat for lat, _, _ in grid])
            # avg_longitude = np.mean([lon for _, lon, _ in grid])
            # Create a Plotly figure
            fig = go.Figure()

            # Add a densitymapbox trace to the figure
            fig.add_trace(
                go.Densitymapbox(
                    lat=latitude_longitude_data["Latitude"],
                    lon=latitude_longitude_data["Longitude"],
                    z=predicted_counts,
                    radius=10,  # Adjust the radius as needed
                    colorscale="Viridis",  # Adjust the colorscale as needed
                    colorbar=dict(
                        title="Predicted Counts",  # Colorbar title
                    ),
                    hoverinfo="z",  # Show predicted counts on hover
                )
            )

            # Update layout to customize the map
            fig.update_layout(
                mapbox_style="open-street-map",  # Map style (other options: "carto-positron", "carto-darkmatter", etc.)
                mapbox_center={
                    "lat": np.mean(latitude_longitude_data["Latitude"]),
                    "lon": np.mean(latitude_longitude_data["Longitude"]),
                },  # Center of the map
                mapbox_zoom=10,  # Initial zoom level
            )

            # Show the figure
            # fig.show()
            # response = Response(img_data, content_type='image/png')

            # return {"response": response}
            fig_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
            print(fig_html)
            return {"response": fig_html}

            # # Return a JSON response containing the HTML string of the plot
            # return JsonResponse({"response": fig_html})

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."
