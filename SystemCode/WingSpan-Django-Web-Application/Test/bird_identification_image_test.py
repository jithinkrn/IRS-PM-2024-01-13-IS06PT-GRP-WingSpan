import os
import requests
import random
import csv
from shutil import copy2

# Constants
DIRECTORY = "C:\\IRS\\Bird Images\\test"
API_ENDPOINT = "http://127.0.0.1:8000/handlerequest/"
CSV_FILE_PATH = os.path.join(DIRECTORY, "bird_identification_results.csv")


# Function to send image to the API
def send_image(image_path, filename_for_api):
    with open(image_path, "rb") as image_file:
        files = {
            "query": (None, "Identify this bird"),  # Query text
            "image": (
                filename_for_api,
                image_file,
                "image/jpeg",
            ),  # Use random filename
        }
        response = requests.post(API_ENDPOINT, files=files)
        if response.ok:
            return response.text
        else:
            print(
                f"Error sending {filename_for_api}: Status code {response.status_code}"
            )
            return "Error"


# Create or open the CSV file
with open(CSV_FILE_PATH, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Actual Bird", "Identified Bird"])

    # Loop through each file in the directory
    for filename in os.listdir(DIRECTORY):
        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
        ):  # Check for image files
            original_path = os.path.join(DIRECTORY, filename)
            random_filename = f"{random.randint(1000, 9999)}.jpg"
            temp_path = os.path.join(DIRECTORY, random_filename)

            # Copy and rename image to a temporary path
            copy2(original_path, temp_path)

            # Send the image to the API with the random filename
            identified_bird = send_image(temp_path, random_filename)

            # Write to CSV with the original filename
            writer.writerow([filename, identified_bird])

            # Remove the temporary file
            os.remove(temp_path)

print("Processing complete. Results are saved in 'bird_identification_results.csv'.")
