from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Function to scrape weather data for a given station, month, and year
def scrape_weather_data(station_name, month, year):
    try:
        # Wait for the temperature element to be visible
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "cityname"))
        )
        
        # Click on the button
        button.click()
        
        # Wait for the dropdown menu to appear
        dropdown_menu = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dropdown-menu"))
        )
        
        # Find the desired option in the dropdown menu
        desired_option = dropdown_menu.find_element(By.XPATH, f"//a[contains(text(), '{station_name}')]")
        
        # Click on the desired option
        desired_option.click()

        time.sleep(10)

        # Select year
        year_button = driver.find_element(By.ID, "year")
        year_button.click()
        year_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//ul[@class='dropdown-menu']/li/a[contains(text(), '{year}')]"))
        )
        year_option.click()

        time.sleep(10)

        # Select month
        month_button = driver.find_element(By.ID, "month")
        month_button.click()
        month_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//ul[@class='dropdown-menu']/li/a[contains(text(), '{month}')]"))
        )
        month_option.click()
        
        time.sleep(10)
        
        # Click on the display button
        display_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "display"))
        )
        display_button.click()
        
        time.sleep(30)

        # Wait for the table to be present
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-calendar"))
        )

        # Extract table HTML
        table_html = table.get_attribute("outerHTML")

        # Use pandas to parse the HTML table
        dfs = pd.read_html(table_html)

        # Select the first DataFrame (assuming there's only one table)
        df = dfs[0]

        # Add station name, month, and year as columns
        df.insert(0, 'Year', year)
        df.insert(0, 'Month', month)
        df.insert(0, 'Station', station_name)

        # Write DataFrame to CSV file
        filename = f"{station_name}_{month}_{year}.csv"
        df.to_csv(filename, index=False)

        print(f"Table data for {station_name}, {month} {year} saved to '{filename}'")

    except Exception as e:
        print(f"An error occurred while scraping data for {station_name}, {month} {year}: {e}")

# Initialize Chrome WebDriver
driver = driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Maximize the browser window
driver.maximize_window()

# Navigate to the website
driver.get("http://www.weather.gov.sg/climate-historical-daily/")

# Give the page some time to load
time.sleep(5)

# List of station names
station_names = [
    "Paya Lebar", "Macritchie Reservoir", "Lower Peirce Reservoir", "Jurong (North)",
    "Semakau Island", "Admiralty", "Admiralty West", "Pulau Ubin", "East Coast Parkway",
    "Marina Barrage", "Ang Mo Kio", "Choa Chu Kang (West)", "Serangoon North", "Newton",
    "Lim Chu Kang", "Marine Parade", "Choa Chu Kang (Central)", "Tuas South", "Pasir Panjang",
    "Jurong Island", "Dhoby Ghaut", "Nicoll Highway", "Botanic Garden", "Choa Chu Kang (South)",
    "Khatib", "Whampoa", "Tengah", "Changi", "Seletar", "Pasir Ris (West)", "Kampong Bahru",
    "Jurong Pier", "Ulu Pandan", "Serangoon", "Jurong (East)", "Mandai", "Tai Seng",
    "Jurong (West)", "Upper Thomson", "Clementi", "Buangkok", "Sentosa Island", "Chai Chee",
    "Boon Lay (West)", "Bukit Panjang", "Kranji Reservoir", "Upper Peirce Reservoir", "Kent Ridge",
    "Tanjong Pagar", "Queenstown", "Tanjong Katong", "Somerset (Road)", "Sembawang", "Punggol",
    "Tuas West", "Simei", "Boon Lay (East)", "Toa Payoh", "Tuas", "Bukit Timah", "Yishun",
    "Buona Vista", "Pasir Ris (Central)"
]

# List of months
months = [ "January", "February", "October", "November", "December"]



years = [str(year) for year in range(2018, 2025,6)]


for year in years:
    for month in months:
        if year == "2018" and month in ["January", "February"]:
            continue
        elif year == "2024" and month in ["October", "November", "December"]:
            continue
        for station_name in station_names:
            scrape_weather_data(station_name, month, year)

# Close the browser
driver.quit()
