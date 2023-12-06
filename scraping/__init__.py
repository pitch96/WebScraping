import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
# import pandas as pd
from bs4 import BeautifulSoup
import time

def scraping_website(input_url):
# Set the Octo HTTP server port
    OCTO_HTTP_SERVER = 58888
    # Get the URL input from the user
    url = input_url

    # Define the local API URL
    LOCAL_API = f'http://localhost:{OCTO_HTTP_SERVER}/api/profiles'
    profile_id = '993dc73bd68e47598a037df53d39f003'

    # Start a session and get the debug port
    data = requests.post(
        f'{LOCAL_API}/start', json={'uuid': profile_id, 'headless': False, 'debug_port': True}
    ).json()
    port = data["debug_port"]

    # Set up Chrome options with debuggerAddress
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')

    # Initialize the Chrome driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    # Navigate to the specified URL
    driver.get(url)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source,features="html.parser")

    heading = soup.find('h1','headline').text.strip()
    location = soup.find('small').text.replace('Show map', '').replace('–', '').replace('\n', '').strip()
    description = soup.find('div', 'translatable charter-data').text.strip()

    calendar_element = driver.find_element(By.ID, 'booking_date_availability_form_search')
    calendar_element.click()
    months_and_prefixes = [("December", "2023-12-"), ("January", "2024-1-"), ("February", "2024-2-"), ("March", "2024-3-"), ("April", "2024-4-"), ("May", "2024-5-"), ("June", "2024-6-"), ("July", "2024-7-"), ("August", "2024-8-"), ("September", "2024-9-"), ("October", "2024-10-"),("November", "2024-11-"), ]
    availability_dates = []
    for month, prefix in months_and_prefixes:
        all_days = driver.find_elements(By.CSS_SELECTOR, '.datepicker-days table.table-condensed tbody tr td')
        days = []
        for i, day in enumerate(all_days, start=1):
            if day.get_attribute('class') == "day":
                days.append(day.text)
        separator = ", " 
        days = separator.join(days)
        availability_dates.append(f'{prefix}{days}')
            
        # if month != "October":
        next_button = driver.find_element(By.CSS_SELECTOR, '.datepicker-days table.table-condensed thead tr:nth-of-type(2) th.next')
        next_button.click()
    separator = "\n" 
    availability_dates = separator.join(availability_dates)

    trips = soup.find_all('li', 'package-item')

    package_titles = []
    package_prices = []
    package_dates = []
    package_descriptions = []
    type_fishings = []
    fishing_techniques = []
    targeted_of_fishes = []

    for id, trip in enumerate(trips):
        
        #package title
        package_title_div = trip.find('span', 'package-title')
        package_title = package_title_div.text.strip() if package_title_div else ""
        package_titles.append(package_title)
        
        #package price
        package_price_div = trip.find('div', class_='price js-package-recalculated-price')
        package_price = package_price_div.text.strip() if package_price_div else ""
        package_prices.append(package_price)
        
        #package booking date
        package_date_temp = []
        package_date = trip.find_all('div', 'description-content') if trip.find_all('div', 'description-content') else ""
        for package_date_detail in package_date:
            package_date_temp.append(package_date_detail.text.strip())
        separator = "\n"
        package_date_temp = separator.join(package_date_temp)
        package_dates.append(package_date_temp)
        
        #package description
        package_description_div = trip.find('div', 'row-space-top-2')
        package_description = package_description_div.text.strip() if package_description_div else ""
        package_descriptions.append(package_description)
        
        #Types of fishing and Fishing Techniques
        type_fishing_temp = []
        fishing_technique_temp = []
        type_tech_fishings = trip.find_all('div', 'package-fishing-types-and-techniques') if trip.find_all('div', 'package-fishing-types-and-techniques') else ""
        for id, type_tech_fishing in enumerate(type_tech_fishings):
            if id == 0:
                type_fishing_temp.append(type_tech_fishing.text.strip().replace('\n', ',').replace(',,,,,', '\n')) 
            else:
                fishing_technique_temp.append(type_tech_fishing.text.strip().replace('\n', ',').replace(',,,,,', '\n'))
        separator = "\n"
        type_fishing_temp = separator.join(type_fishing_temp)
        fishing_technique_temp = separator.join(fishing_technique_temp)
        type_fishings.append(type_fishing_temp)
        fishing_techniques.append(fishing_technique_temp)
        
        #Targeted Fishes
        target_fishes_temp = []
        target_fishes = trip.find_all('div', 'package-fish-name text-center') if trip.find_all('div', 'package-fish-name text-center') else ""
        for target_fish in target_fishes:
            target_fishes_temp.append(target_fish.text.strip())
        separator = "\n"
        target_fishes_temp = separator.join(target_fishes_temp)
        targeted_of_fishes.append(target_fishes_temp)

    import pandas as pd

    # Assuming you have variables like heading, location, description, availability_dates, and package_titles defined

    # Create a DataFrame for the main data
    FishingData = {
        "Outfitter Name": [heading],
        "Location": [location],
        "Description": [description],
        "Availability Dates": [availability_dates],
    }

    df = pd.DataFrame(FishingData)

    # Convert the "Package Name" column to a dictionary of lists
    package_data = {
        "Package Name": package_titles
    }
    package_price = {
        "Price" : package_prices
    }

    package_dat = {
        "Package Dates" : package_dates
    }

    trip_details = {
        "Trip Detail" : package_descriptions
    }

    type_of_fishing = {
        "Types of fishing" : type_fishings
    }

    fishing_of_techniques = {
        "Fishing techniques" : fishing_techniques
    }

    targeted_of_fish = {
        "Targeted fish" : targeted_of_fishes
    }

    # Create a new DataFrame from the dictionary
    package_df = pd.DataFrame(package_data)

    price_df = pd.DataFrame(package_price)

    package_dates_df = pd.DataFrame(package_dat)

    package_detail_df = pd.DataFrame(trip_details)

    type_of_fishing_df = pd.DataFrame(type_of_fishing)

    fishing_of_techniques_df = pd.DataFrame(fishing_of_techniques)

    targeted_fish_df = pd.DataFrame(targeted_of_fish)

    # Concatenate the main DataFrame and the package DataFrame
    result_df = pd.concat([df, package_df, price_df, package_dates_df, package_detail_df, type_of_fishing_df, fishing_of_techniques_df, targeted_fish_df], axis=1)

    # Save the combined DataFrame to a CSV file with 'utf-8' encoding
    result_df.to_csv('result.csv', index=False, encoding='utf-8', header=True)
        
    driver.quit()     