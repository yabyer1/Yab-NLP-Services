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
from datetime import timedelta
from selenium.webdriver.chrome.service import Service
import sqlite3
from datetime import datetime
import psycopg2
import time
import random
import calendar
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

import csv
def log_scrape_result(log_path, year, month, start_date, end_date, num_articles, success, notes=""):
    file_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["year", "month", "start_date", "end_date", "num_articles", "success", "notes"])
        writer.writerow([year, month, start_date, end_date, num_articles, success, notes])

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
   
    return article_text
def fetch_articles_by_month(year, month):
    url = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json"
    params = {
        "api-key": nyt_api_key
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {year}-{month:02d}: {response.status_code}")
        return []

    data = response.json()
    articles = data['response']['docs']
    return articles

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
        article['headline']['main'],
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
LOG_FILE = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/scraper/scraped_log.csv"
if __name__ == "__main__":

    driver = webdriver.Chrome(service=service, options=options)
    for year in range(2024, 2025):
        for month in range(1, 13):
            

            articles = fetch_articles_by_month(year, month)

            print(f"✅ Fetched {len(articles)} articles for {month}/{year}")

            for article in articles:
                if 'published_date' not in article:
                    article['published_date'] = datetime.utcnow().isoformat()

                article['url'] = article['web_url']
                try:
                 full_text = fetch_article_text(article['url'])
                except Exception as e:
                    print(f"⚠️ Error fetching article {article['url']}: {e}")
                    continue
                if len(full_text.strip()) < 300:
                    print("⚠️ Skipping short article")
                    continue
                sentiment = analyze_sentiment(full_text)
                summary_generated = summarize_article(full_text)
                article['summary'] = article.get('abstract', '') 
                if not article['summary']:
                    article['summary'] = summary_generated
                entities = extract_entities(full_text)
                save_to_pg(article,full_text,sentiment, summary_generated, entities)
                print(f"\nsaved {article['headline']['main']} to db")

       
        
    driver.quit()


