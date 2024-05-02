from rest_framework.response import Response
import time
from openai import OpenAI
import base64
import os
from django.conf import settings
from PIL import Image
import io


client = OpenAI()
GPT_MODEL = "gpt-4-vision-preview"


class ImageIdentificationBot:

    def __init__(self):
        self.chat_response = ""
        self.state = ""
        self.client = OpenAI()

    def identify_bird(self, user_query, image_path):
        try:
            # Construct the full path to the image file
            image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            birds_list_path = os.path.join(
                settings.BASE_DIR,
                "Data",
                "BirdInformation",
                "Singapore_Bird_Name_List.txt",
            )

            # Read the list of birds from the text file
            with open(birds_list_path, "r", encoding="utf-8") as file:
                birds_list = file.read()

            # open, resize image and convert to base64
            with Image.open(image_path) as img:
                img_resized = img.resize((200, 200))
                buffer = io.BytesIO()
                img_resized.save(buffer, format="JPEG")
                base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{user_query}. Give me the possible answers if you do not have a definite answer.\
                                        Here are possible birds: {birds_list}. Do not mention the documents/record used or the\
                                        locations in it in the response",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
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

    def handle_message(self, request, image_path):
        # Retrieve the full conversation history from the session
        conversation_history = request.session.get("conversation_history", [])
        # Get the last 10 items of the conversation history
        conversation_history_recent = conversation_history[-10:]
        try:
            user_query = request.data.get("query", "")

            extended_prompt = f"Based on the message: '{user_query}', and the attached\
            image determine if I'm trying to identify a specific bird.\
            My goal is to accurately identify a bird using image provided.\
            Please look into the attached 'Singapore_Bird_Name_List.txt' \
            to look for the possible birds Remember, avoid mentioning the\
            document name directly in your response. Let's make the response\
            as natural as possible\
            take Conversation history:{conversation_history_recent} into \
            consideration to undestand what i am saying "
            response = self.identify_bird(extended_prompt, image_path)
            return {"response": response}

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."
