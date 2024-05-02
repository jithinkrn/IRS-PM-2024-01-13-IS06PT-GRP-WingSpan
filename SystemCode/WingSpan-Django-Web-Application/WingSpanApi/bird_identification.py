from rest_framework.response import Response
import time
from openai import OpenAI


class BirdIdentificationBot:

    def __init__(self):
        self.chat_response = ""
        self.client = OpenAI()
        self.ASSISTANT_ID = "asst_KJ0rhIvSbbrK5cYlNtmFB52R"

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

        conversation_history = request.session.get("conversation_history", [])
        # Get the last 10 items of the conversation history
        conversation_history_recent = conversation_history[-10:]

        try:
            user_query = request.data.get("query", "")
            # From General predictionn chat to Identifying the prediction mode type

            extended_prompt = f"Based on the message: '{user_query}', your goal is to\
            accurately identify a bird using a semantic search of the \
            'Birds_Information.txt' data provided. If it seems like I'm\
            looking for general bird information instead, please clarify\
            what specific details or support I need regarding bird \
            identification. Keep our conversation realistic and clear, \
            so I can provide the correct information. Remember, avoid \
            mentioning the document name directly in your response. \
            Let's make our exchange as natural as possible\
            take Conversation history:{conversation_history_recent} into\
            consideration to undestand what i am saying\
            Don't include source and References from the attachment \
            in your response. Don't mention any technical detail or\
            attachment used as well"
            response = self.talk_to_assistant(extended_prompt)
            return {"response": response}

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."
