import requests
from bs4 import BeautifulSoup

def get_tx(addr:str):
    response = requests.get(f"https://etherscan.io/address/{addr}", headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.select_one(".myFnExpandBox_searchVal")
    hashval = temp.get_text() if (temp != None) else None
    temp = soup.select_one("#availableBalance > div.overflow-y-auto.scrollbar-custom.px-3.pb-3 > ul > li.nav-item.list-custom-ERC20 > a > div:nth-child(1) > span")
    amount = float(temp.get_text().replace(" SIX", "").replace(",","")) if (temp != None) else None
    return (hashval, amount)