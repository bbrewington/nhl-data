# import
# "#page-content-wrapper > div:nth-child(1) > table"

import requests
from bs4 import BeautifulSoup
import re

response = requests.get("https://moneypuck.com/data.htm")
soup = BeautifulSoup(response.content, "html.parser")

links = soup.find_all("a")  # Find all elements with the tag <a>
download_links = []
for link in links:
    link_href = link.get("href")
    if link_href:
        if re.search(".(csv|zip)", link.get("href")):
            print("Link:", link.get("href"), "Text:", link.string)
