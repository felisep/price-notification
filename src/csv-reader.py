import os
import pandas as pd
import scraper
import requests
import sys


def clean_number(number):
    return str(number).replace('kr', '').replace(' ', '').replace(',', '').replace('\u00A0', '')


def price_change(old_price, new_price, company, webhook, url):
    old_price_cleaned = int(clean_number(old_price))
    new_price_cleaned = int(clean_number(new_price))
    if new_price_cleaned < old_price_cleaned:
        message = f"The price has gone down! It was {old_price_cleaned} kr, now it's {new_price_cleaned} kr. It has decreased by {old_price_cleaned - new_price_cleaned} kr for {company} page.\nLink: {url}"
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
        html_content = html_contents[0]

        if new_price and html_content and scraper.check_medium_in_stock(html_content, selector):
            if clean_number(new_price) != clean_number(old_price):
                price_change(old_price, new_price, company, webhook, url_variable)
            else:
                print("Price has not changed")
        else:
            print("Item is not in stock or failed to retrieve price")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/csv-reader.py <webhook_url>")
        sys.exit(1)

    webhook_url = sys.argv[1]
    track_prices('data/rvrc-data.csv', webhook_url)