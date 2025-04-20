import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import selenium 
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
import time 
from selenium.webdriver.chrome.service import Service

options = Options()
options.add_argument("--headless")  
options.add_argument("--disable-gpu")

# Path to ChromeDriver binary
service = Service('/usr/local/bin/chromedriver')


# Load API key from .env
load_dotenv()
nyt_api_key = os.getenv("NYT_API_KEY")

URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

# Fetch list of articles
def fetch_nyt_finance_articles(pages=1):
    articles = []
    for page in range(pages):
        params = {
            "q": "finance",
            "sort": "newest",
            "api-key": nyt_api_key,
            "page": page
        }

        response = requests.get(URL, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            continue

        data = response.json()
        docs = data.get("response", {}).get("docs", [])

        for article in docs:
            articles.append({
                "headline": article["headline"]["main"],
                "url": article["web_url"],
                "published_date": article["pub_date"],
                "summary": article.get("abstract", "no summary available")
            })

    return articles

def fetch_article_text(url):
    driver.get(url)
    article_text = ''
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    paragraph = soup.find_all('p')
    for i in paragraph:
        a = i.get_text()
        if a != 'Advertisement' and a != 'Supported by' and a != 'Send any friend a story' and a != 'As a subscriber, you have 10 gift articles to give each month. Anyone can read what you share.' and not a.startswith("By"):
            article_text += a 
            article_text += " "
    time.sleep(8)
    return article_text
# Dummy test
if __name__ == "__main__":
    articles = fetch_nyt_finance_articles(pages=1)
    for i, article in enumerate(articles):
        print(f"\n\n📰 Article {i + 1}: {article['headline']}")
        print(f"🔗 URL: {article['url']}")
        print(f"📝 Summary: {article['summary']}")
        print(f"📅 Published: {article['published_date']}")
        print("\n📄 Full Text:")
        driver = webdriver.Chrome(service=service, options=options)
        full_text = fetch_article_text(article['url'])
        driver.quit()
        print(full_text)  # limit output if long
