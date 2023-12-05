import requests
from bs4 import BeautifulSoup

def get_tx(link:str):
    response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.select_one(".myFnExpandBox_searchVal")