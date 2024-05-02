from django.shortcuts import render
from WingSpanApi.bird_information import BirdInformationBot
from WingSpanApi.bird_identification import BirdIdentificationBot
from WingSpanApi.bird_identification_image import ImageIdentificationBot
from WingSpanApi.bird_prediction import BirdPredictionBot

from WingSpanApi.location_recommendation import LocationRecommendationBot
from WingSpanApi.bird_heatmap import BirdHeatMapBot
from .models import MyModel
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings

client = OpenAI()
birdInformationBot = BirdInformationBot()
birdIdentificationBot = BirdIdentificationBot()
imageIdentificationBot = ImageIdentificationBot()
birdPredictionBot = BirdPredictionBot()
locationRecommendationBot = LocationRecommendationBot()
hotspotMap = BirdHeatMapBot()

GPT_MODEL = "gpt-4"


def index(request):
    items = MyModel.objects.all()
    return render(request, "index.html", {"items": items})


class handlerequest(APIView):
    def __init__(self):
        self.known_intents = [
            "Greeting",
            "Bird Information",
            "Bird Identification",
            "Spotting Prediction",
            "Hotspot Map",
            "Park Recommendation",
        ]

    # identify user intent using LLM
    def identify_intent(self, user_message, session):

        # Append the new user message to the conversation history
        conversation_history = session.get("conversation_history", [])
        conversation_history.append({"role": "user", "content": user_message})
        # Debugging - printing conversation_history
        history_str = "\n".join(
            f"{entry['role'].title()}: {entry['content']}"
            for entry in conversation_history
        )

        print(history_str)

        # This function sends the message to the LLM to identify the intent
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Classify the intent of this user message: '{user_message}'\n\n"
                        "Greeting\nBird Information\nBird Identification\nHotspot Map\nSpotting Prediction\n\nPark Recommendation\n"
                        f"Take the conversation history into consideration: {conversation_history}\n"
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            model=GPT_MODEL,
            temperature=0,
        )

        # Extracting the intent from the response
        intent = response.choices[0].message.content
        if intent in self.known_intents:
            # Save the new intent and conversation history to the session
            session["intent"] = intent
            session["conversation_history"] = conversation_history
            session.save()
            return intent
        else:
            # Handle unknown or unclear intent
            session["intent"] = "Unclear Intent"
            session.save()
            return session["intent"]

    # To keep only 5 images at application server
    def manage_file_limit(self, directory_path, max_files=5):
        files = [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))
        ]
        files.sort(key=os.path.getmtime)

        # If there are more than max_files, remove the oldest
        while len(files) > max_files:
            os.remove(files[0])
            files.pop(0)

    def post(self, request, *args, **kwargs):

        latest_message = ""
        user_query = request.data.get("query", "")
        # Handling file upload
        image = request.FILES.get("image", None)
        if image:
            # saving the image to your media root
            # After saving a new image, ensure the media folder doesn't exceed the max number of images
            try:
                image_path = default_storage.save(image.name, ContentFile(image.read()))
                self.manage_file_limit(settings.MEDIA_ROOT, max_files=5)
            except Exception as e:
                print(f"Error during file handling: {e}")
            # add user chat to the HTTP session to track intents
            request.session["intent"] = "Image based Identification"
            conversation_history = request.session.get("conversation_history", [])
            conversation_history.append({"role": "user", "content": user_query})
            request.session["conversation_history"] = conversation_history
            # call the image based indetification
            latest_message = imageIdentificationBot.handle_message(request, image_path)
            # add bot resposnse to the HTTP session to track intents
            conversation_history = request.session.get("conversation_history", [])
            conversation_history.append({"role": "Bot", "content": latest_message})
            request.session.save()
            return Response(latest_message, status=status.HTTP_200_OK)

        else:
            session_intent = request.session.get("intent")
            new_intent = self.identify_intent(user_query, request.session)

            # If the intent has changed, or if there was no previous intent, use the new one
            if session_intent != new_intent:
                intent = new_intent
            else:
                intent = session_intent

            if intent == "Unclear Intent":
                latest_message = {
                    "response": "I'm not quite sure what you're asking. Could you provide more information or clarify your request?"
                }

            elif intent == "Greeting":
                latest_message = {
                    "response": "Hello! I'm here to assist you with all things bird-related. Whether you're curious about different bird species, looking for bird watching hotspots, or need help identifying a feathered friend, just ask away!"
                }

            elif intent == "Bird Information":
                latest_message = birdInformationBot.handle_message(request)

            elif intent == "Bird Identification":
                latest_message = birdIdentificationBot.handle_message(request)

            elif intent == "Spotting Prediction":
                latest_message = birdPredictionBot.handle_message(request)

            elif intent == "Park Recommendation":
                latest_message = locationRecommendationBot.handle_message(request)

            elif intent == "Hotspot Map":
                latest_message = hotspotMap.handle_message(request)
                print(intent)
                return Response(latest_message, status=status.HTTP_200_OK)

            else:
                latest_message = {
                    "response": "Hi, Please provide more information for me to understand your request"
                }
            # Append the chat message to the conversation history
            conversation_history = request.session.get("conversation_history", [])
            conversation_history.append({"role": "Bot", "content": latest_message})
            request.session.save()
            print(intent)
            return Response(latest_message, status=status.HTTP_200_OK)
