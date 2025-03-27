# In scraper.py
import requests
from bs4 import BeautifulSoup


def get_page(urls, selectors):
    results = []
    for url, selector in zip(urls, selectors):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            element = soup.select_one(selector)
            if element:
                results.append(element.get_text())
            else:
                results.append(None)
        else:
            results.append(None)
    return results
