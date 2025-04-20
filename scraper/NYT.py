import json
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
import sqlite3
from datetime import datetime
import psycopg2

options = Options()
options.add_argument("--headless")  
options.add_argument("--disable-gpu")

# Path to ChromeDriver binary
service = Service('/usr/local/bin/chromedriver')


# Load API key from .env
load_dotenv()
nyt_api_key = os.getenv("NYT_API_KEY")

URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
def analyze_sentiment(text):
    try:
        r = requests.get("http://localhost:8000/sentiment", params={"text": text})
        return r.json().get("label", "unknown")
    except:
        return "error"

def summarize_article(text):
    try:
        r = requests.get("http://localhost:8001/summarize", params={"text": text})
        return r.json().get("summary", "")
    except:
        return ""

def extract_entities(text):
    try:
        r = requests.get("http://localhost:8003/preprocess", params={"text": text})
        return r.json().get("ner", [])
    except:
        return []

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
# --- Save to PostgreSQL ---
def save_to_pg(article, full_text, sentiment, summary_generated, entities):
    conn = psycopg2.connect(
        dbname="nlp_articles",
        user="nlp_user",
        password="secret",
        host="localhost",  # if inside Docker, use 'postgres'
        port="5433"
    )
    cursor = conn.cursor()

    unique_id = f"{article['published_date'][:10]}_{hash(article['url']) % 1000000}"

    cursor.execute("""
        INSERT INTO nyt_articles (
            id, headline, summary, url, published_date,
            full_text, sentiment, summary_generated, entities, scraped_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (
        unique_id,
        article['headline'],
        article['summary'],
        article['url'],
        article['published_date'],
        full_text,
        sentiment,
        summary_generated,
        json.dumps(entities),
        datetime.utcnow()
    ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    articles = fetch_nyt_finance_articles(pages=1)
    for i, article in enumerate(articles):
        print(f"\n📰 {i+1}: {article['headline']}")
        driver = webdriver.Chrome(service=service, options=options)
        full_text = fetch_article_text(article['url'])
        driver.quit()
        print("fetched text")
        sentiment = analyze_sentiment(full_text)
        print("fetched sentiment")
        summary = summarize_article(full_text)
        print("fetched summary")
        entities = extract_entities(full_text)
        print("fetched entities")
        save_to_pg(article, full_text, sentiment, summary, entities)
        print(f"✅ Saved to DB with sentiment='{sentiment}'")
