import requests
import re
import json
from Utils.utils import clean_number


def power():
    # API URL
    url = "https://www.power.no/api/v2/products?ids=3251951"

    # Headers (Optional, to mimic a browser)
    headers = {"User-Agent": "Mozilla/5.0"}

    # Fetch the JSON response
    response = requests.get(url, headers=headers)
    data = response.json()  # Convert response to JSON

    # Extract the price
    if data and "price" in data[0]:
        price = data[0]["price"]  # Since it's inside a list
        price = clean_number(price)  # Clean the price
    else:
        raise ValueError("Price not found in the response")

    return price


def obs():
    # API URL
    url = "https://www.obs.no/klar/herreklar/jakker-herre/vatterte-jakker-herre/2840945?v=Obs-7022324994646"

    # Headers (Optional, to mimic a browser)
    headers = {"User-Agent": "Mozilla/5.0"}

    # Fetch the JSON response
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.content:
        match = re.search(r'window\.CURRENT_PAGE\s*=\s*({.*?});', response.text, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)  # Parse the JSON object

            except json.JSONDecodeError:
                raise ValueError("Extracted content is not valid JSON")
        else:
            raise ValueError("window.CURRENT_PAGE not found in the response")
    else:
        raise ValueError("Failed to fetch data or empty response")

    # Extract the price
    if data and "price" in data and "current" in data["price"] and "inclVat" in data["price"]["current"]:
        price = data["price"]["current"]["inclVat"]
        price = clean_number(price)  # Clean the price
    else:
        raise ValueError("Price not found in the response")

    return price


if __name__ == '__main__':
    obs()
