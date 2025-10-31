# In scraper.py
import requests
from bs4 import BeautifulSoup


def get_page(urls, selectors):
    results = []
    html_contents = []
    for url, selector in zip(urls, selectors):
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.content
            html_contents.append(html_content)
            soup = BeautifulSoup(html_content, 'html.parser')
            element = soup.select_one(selector)
            if element:
                results.append(element.get_text())
            else:
                results.append(None)
        else:
            html_contents.append(None)
            results.append(None)
    return results, html_contents


def check_medium_in_stock(html_content, selector):
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.select_one(selector)
    if element:
        return element.get('data-cy-instock') == 'true'
    else:
        return False
