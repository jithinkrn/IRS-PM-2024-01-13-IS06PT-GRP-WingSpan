from rest_framework.response import Response
import time
from openai import OpenAI


class BirdInformationBot:

    def __init__(self):
        self.chat_response = ""
        self.client = OpenAI()
        self.ASSISTANT_ID = "asst_HYaulmpHqkMgj3ESR8nIzyZV"

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
            extended_prompt = f"message: '{user_query}'.Your goal is to get \
                accurate bird information form the attached 'Birds_Information.txt' \
                data with a semantic search.If my intention isn't clear, \
                please ask for more details on the kind of support I need from\
                your chat service regarding birds.Make the conversation so \
                realistic and give clarity so that I can provide correct \
                information. Do not tell what document use, i.e, the file name\
                'Birds_Information.txt' to the user in your reply.\
                Format your resposnse to sound natural. Take Conversation\
                history:{conversation_history_recent} into consideration to \
                undestand what i am saying\
                Don't inlude source and References from the attachment \
                in your response. Don't mention any technical detail or\
                attachment used as well"
            response = self.talk_to_assistant(extended_prompt)
            return {"response": response}

        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."
