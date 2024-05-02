import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# Function to safely extract text from an element, handling situations where the element may not be present
def safe_extract_text(driver, selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element.text
    except NoSuchElementException:
        return "null"

# Update the function to handle missing elements
def extract_identification_text(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        driver.get(url)

        identification_text = safe_extract_text(driver, "section.identification p")
        habitat_text = safe_extract_text(driver, "section.habitat p")
        size_text = safe_extract_text(driver, "section.size p")
        range_text = safe_extract_text(driver, "#main > div > section:nth-child(5)")
        taxonomy_text = safe_extract_text(driver, "#main > div > section:nth-child(6)")
        behaviour_text = safe_extract_text(driver, "section.behaviour p")
        localStatus_text = safe_extract_text(driver, "section.local-status p")
        conservationStatus_text = safe_extract_text(driver, "section.conservation-status p")
        location_text = safe_extract_text(driver, "section.location p")
        localSubSpecies_text = safe_extract_text(driver, "section.local-subspecies p")
        peak_weeks = safe_extract_text(driver, "#main > div > section.bar-chart > div > div.bar-chart-details.row.position-relative > div.float-end.text-end.col.d-inline-block.right-col.g-0 > div:nth-child(1) > span")
        print("Identification:", identification_text)
        print("Habitat:", habitat_text)
        print("Size:", size_text)
        print("Range:", range_text)
        print("Taxonomy:", taxonomy_text)
        print("Behaviour:", behaviour_text)
        print("Local Status:", localStatus_text)
        print("Conservation Status:", conservationStatus_text)
        print("Location:", location_text)
        print("Local Subspecies:", localSubSpecies_text)
        print("Peak Weeks:", peak_weeks)

        return identification_text, habitat_text, size_text, range_text, taxonomy_text, behaviour_text, localStatus_text, conservationStatus_text, location_text, localSubSpecies_text, peak_weeks
    
    except Exception as e:
        print(f"Error processing URL: {url}")
        print(e)
        return None
    finally:
        driver.quit()




def convertURL(species) :
    formatted_name = species.rstrip().lower().replace(' ','-')
    formatted_name = formatted_name.replace('\'','')
    formatted_url = "https://singaporebirds.com/species/" + formatted_name
    return formatted_url


# Read Excel file containing URLs
excel_file = "urls.xlsx"  # Update with your Excel file path
urls_df = pd.read_excel(excel_file)

# Create a new column for identification text
urls_df["Identification"] = ""
urls_df["Habitat"] = ""
urls_df["Size"] = ""


for index, row in urls_df.iterrows():
    url = convertURL(row["Species"])
    urls_df.at[index, "URL"] = url
    identification_text, habitat_text, size_text, range_text, taxonomy_text, behaviour_text, localStatus_text, conservationStatus_text, location_text, localSubSpecies_text, peak_weeks = extract_identification_text(url)


    if identification_text:
        print(f"Identification text for URL {url}: {identification_text}")
        urls_df.at[index, "Identification"] = identification_text
    else:
        urls_df.at[index, "Identification"] = "null"
        print(f"No identification text extracted for URL {url}")

    if habitat_text:
        print(f"Habitat text for URL {url}: {habitat_text}")
        urls_df.at[index, "Habitat"] = habitat_text
    else:
        urls_df.at[index, "Habitat"] = "null"
        print(f"No habitat text extracted for URL {url}")

    if size_text:
        print(f"Size text for URL {url}: {size_text}")
        urls_df.at[index, "Size"] = size_text
    else:
        urls_df.at[index, "Size"] = "null"
        print(f"No size text extracted for URL {url}")

    if range_text:
        print(f"Range text for URL {url}: {range_text}")
        urls_df.at[index, "Range"] = range_text
    else:
        urls_df.at[index, "Range"] = "null"
        print(f"No range text extracted for URL {url}")

    if taxonomy_text:
        print(f"Taxonomy text for URL {url}: {taxonomy_text}")
        urls_df.at[index, "Taxonomy"] = taxonomy_text
    else:
        urls_df.at[index, "Taxonomy"] = "null"
        print(f"No taxonomy text extracted for URL {url}")

    if behaviour_text:
        print(f"Behaviour text for URL {url}: {behaviour_text}")
        urls_df.at[index, "Behaviour"] = behaviour_text
    else:
        urls_df.at[index, "Behaviour"] = "null"
        print(f"No behaviour text extracted for URL {url}")

    if localStatus_text:
        print(f"Local Status text for URL {url}: {localStatus_text}")
        urls_df.at[index, "Local Status"] = localStatus_text
    else:
        urls_df.at[index, "Local Status"] = "null"
        print(f"No localStatus text extracted for URL {url}")

    if conservationStatus_text:
        print(f"Conservation Status text for URL {url}: {conservationStatus_text}")
        urls_df.at[index, "Conservation Status"] = conservationStatus_text
    else:
        urls_df.at[index, "Conservation Status"] = "null"
        print(f"No conservationStatus text extracted for URL {url}")

    if location_text:
        print(f"Location text for URL {url}: {location_text}")
        urls_df.at[index, "Location"] = location_text
    else:
        urls_df.at[index, "Location"] = "null"
        print(f"No location text extracted for URL {url}")

    if localSubSpecies_text:
        print(f"Local Subspecies text for URL {url}: {localSubSpecies_text}")
        urls_df.at[index, "Local Subspecies"] = localSubSpecies_text
    else:
        urls_df.at[index, "Local Subspecies"] = "null"
        print(f"No location text extracted for URL {url}")


    if peak_weeks:
        print(f"Peak Weeks text for URL {url}: {peak_weeks}")
        urls_df.at[index, "Peak Weeks"] = peak_weeks
    else:
        urls_df.at[index, "Peak Weeks"] = "null"
        print(f"No peak weeks text extracted for URL {url}")



# Save the updated DataFrame back to the Excel file
urls_df.to_excel(excel_file, index=False)