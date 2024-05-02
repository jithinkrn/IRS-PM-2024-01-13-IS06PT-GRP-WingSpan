from datetime import datetime, timedelta
import requests

API_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/singapore"
API_KEY = "WLJZW6CUBE7J9SYF3LZHBSXL5"

def fetch_and_store_current_weather(input_date, input_time):
    """Fetches and stores current weather data into global variables."""
    final_url = f"{API_URL}?unitGroup=metric&key={API_KEY}&contentType=json&startDateTime={input_date}T{input_time} \
                &endDateTime={input_date}T{input_time}"
    response = requests.get(final_url)
    if response.status_code == 200:
        weather_data = response.json()
        store_weather_data(weather_data['currentConditions'], input_date, input_time)  # Pass only the current conditions to store function
    else:
        print("Failed to retrieve weather data")

def fetch_and_store_future_weather(input_date, input_time):
    """Fetches and stores future weather data at 5 PM into global variables."""
    final_url = f"{API_URL}?unitGroup=metric&key={API_KEY}&contentType=json&startDateTime={input_date}T{input_time} \
                &endDateTime={input_date}T{input_time}"
    response = requests.get(final_url)
    if response.status_code == 200:
        weather_data = response.json()
        store_weather_data(weather_data['days'][0]['hours'][0], input_date, input_time)  # Assume the first hour is the one we need (5 PM)
    else:
        print("Failed to retrieve weather data")

def store_weather_data(current_conditions, input_date, input_time):
    """Stores weather data into global variables from the fetched current conditions."""
    global fetch_temperature, fetch_wind_speed, fetch_wind_direction, fetch_visibility, fetch_cloud_cover
    fetch_temperature = current_conditions.get('temp')
    fetch_wind_speed = current_conditions.get('windspeed')
    fetch_wind_direction = current_conditions.get('winddir')
    fetch_visibility = current_conditions.get('visibility')
    fetch_cloud_cover = current_conditions.get('cloudcover')
    # print(f"Data: Date {input_date}, Time {input_time}, Temp {fetch_temperature}°C, \
    #     Wind {fetch_wind_speed} km/h at {fetch_wind_direction}°, Visibility {fetch_visibility} km, \
    #     Cloud Cover {fetch_cloud_cover}%")