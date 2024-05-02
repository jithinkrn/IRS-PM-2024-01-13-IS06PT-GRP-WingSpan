import pdfkit
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pdfkit
from pdfkit.configuration import Configuration

# Configure the path to wkhtmltopdf
# download and install from https://wkhtmltopdf.org/ first
wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = Configuration(wkhtmltopdf=wkhtmltopdf_path)

# Configure the WebDriver and navigate to the checklist page
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://records.singaporebirds.com/checklist/")

# Store the URLs to visit
species_urls = []

# Find all species links on the checklist page and store their URLs
species_links_selector = "tr.species th div.row > div.col-md-auto > a"
species_links = driver.find_elements(By.CSS_SELECTOR, species_links_selector)
for link in species_links:
    url = link.get_attribute("href")
    if url not in species_urls:
        species_urls.append(url)

all_species_info = ""  # This will hold all the information for the PDF

# # filename = "unique_species_urls.txt"
# filename = r"C:\IRS\WingSpanDataPreperationScripts\Bird_Information_Data_Extraction\unique_species_urls.txt"
# # Write the unique URLs to the file
# with open(filename, "w") as file:
#     for url in species_urls:
#         file.write(url + "\n")

# for species_url in species_urls[:5]:  # Only process the first 5 species URLs
for species_url in species_urls:
    species_info = {}  # Initialize the dictionary here for each species
    try:
        driver.get(species_url)
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        title = driver.title
        bird_name = title.split("–")[0].strip()
        all_species_info += f"{bird_name}\n"  # Add the bird name as a heading

        # Exclude sections with certain CSS classes
        excluded_classes = [
            ".featured-reports",
            ".external-links",
            ".references",
            ".recommended-citation",
        ]
        sections = driver.find_elements(
            By.CSS_SELECTOR, "section:not({})".format("):not(".join(excluded_classes))
        )

        for section in sections:
            paragraphs = section.find_elements(By.CSS_SELECTOR, "p")
            for paragraph in paragraphs:
                text = paragraph.text
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip()
                    value = value.strip().replace("\u8211", "-")  # Handle HTML entity
                    species_info[key] = value

        all_species_info += "\n".join([f"{k}: {v}" for k, v in species_info.items()])
        all_species_info += "\n\n"  # Add some space between species

    except Exception as e:
        print(f"An error occurred while processing {species_url}: {e}")
    finally:
        # add a short delay to reduce the load on the server
        time.sleep(1)

# Write the information to a text file
text_file_path = r"C:\IRS\WingSpanDataPreperationScripts\Bird_Information_Data_Extraction\All_Birds_Info.txt"
with open(text_file_path, "w", encoding="utf-8") as file:
    file.write(all_species_info)

# Close the WebDriver
driver.quit()
