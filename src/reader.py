import os
import pandas as pd
import scraper
import requests
import sys
from bs4 import MarkupResemblesLocatorWarning
import warnings
from requestcompany import power, obs
from Utils.utils import clean_number

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

def price_change(old_price, new_price, company, webhook, url):
    old_price_cleaned = int(clean_number(old_price))
    cleaned_new_price = clean_number(new_price)
    try:
        new_price_cleaned = int(cleaned_new_price)
    except ValueError:
        print(f"Error converting cleaned new price to int: {cleaned_new_price}")
        return

    if new_price_cleaned < old_price_cleaned:
        message = (f"The price has gone down! It was {old_price_cleaned} kr, now it's {new_price_cleaned} kr. It has "
                   f"decreased by {old_price_cleaned - new_price_cleaned} kr for {company} page.\nLink: {url}")
        send_discord_message(message, webhook)

def send_discord_message(message, webhook):
    data = {
        "content": message
    }
    response = requests.post(webhook, json=data)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

def track_prices(file_path, webhook):
    abs_file_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_file_path):
        raise FileNotFoundError(f"The file {abs_file_path} does not exist.")

    df = pd.read_csv(abs_file_path, delimiter=',')  # Ensure correct delimiter
    df['price'] = df['price'].astype(str)  # Cast the price column to string

    for index, row in df.iterrows():
        url_variable = row['url']
        selector = row['selector']
        old_price = row['price']
        company = row['company']

        # Ensure the URL is valid
        if not url_variable.startswith('http'):
            print(f"Skipping invalid URL: {url_variable}")
            continue

        new_prices, html_contents = scraper.get_page([url_variable], [selector])
        new_price = new_prices[0]

        if company == 'rvrc':
            if scraper.check_medium_in_stock(url_variable, selector):
                print("Item is in stock")
                if clean_number(new_price) != clean_number(old_price):
                    price_change(old_price, new_price, company, webhook, url_variable)
                else:
                    print("Price has not changed")
            else:
                print(f"Item in {company} is out of stock")
        elif company == 'power':
            new_price_request = power()
            if clean_number(new_price_request) != clean_number(old_price):
                price_change(old_price, new_price_request, company, webhook, url_variable)
            else:
                print(f"Price has not changed for {company}")
        elif company == 'obs':
            new_price_request = obs()
            if clean_number(new_price_request) != clean_number(old_price):
                price_change(old_price, new_price_request, company, webhook, url_variable)
            else:
                print(f"Price has not changed for {company}")
        else:
            print(f"Company {company} not supported")


if __name__ == "__main__":
    webhook_url = os.getenv('DISCORD_WEBHOOK')
    if not webhook_url:
        print("Environment variable DISCORD_WEBHOOK is not set.")
        sys.exit(1)

    track_prices('data/rvrc-data.csv', webhook_url)