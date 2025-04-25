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
# Fetch list of articles
def fetch_nyt_finance_articles(pages=100, start_date=None, end_date=None):
    articles = []
    for page in range(pages):
        params = {
            "q": "finance",
            "sort": "newest",
            "api-key": nyt_api_key,
            "page": page
        }
        if start_date:
            params["begin_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        success = False
        retries = 0
        while not success and retries < 3:
            try:
                response = requests.get(URL, params=params, timeout=10)
                if response.status_code == 200:
                    success = True
                    data = response.json()
                    docs = data.get("response", {}).get("docs", [])
                    if not docs:
                        print(f"🔚 No more articles at page {page}")
                        return articles
                    for article in docs:
                        articles.append({
                            "headline": article["headline"]["main"],
                            "url": article["web_url"],
                            "published_date": article["pub_date"],
                            "summary": article.get("abstract", "no summary available")
                        })
                else:
                    print(f"⚠️ Error {response.status_code} at page {page}: {response.text}")
                    retries += 1
                    sleep_time = 3 * retries + random.uniform(0, 2)
                    print(f"⏳ Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
            except Exception as e:
                print(f"🔥 Exception at page {page}: {e}")
                retries += 1
                time.sleep(3 * retries)

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
LOG_FILE = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/scraper/scraped_log.csv"
if __name__ == "__main__":
   for year in range(2010, 2025):
    for month in range(1, 13):
        start = f"{year}{month:02d}01"
        end_day = calendar.monthrange(year, month)[1]
        end = f"{year}{month:02d}{end_day}"
        print(f"\n📅 Scraping articles for {start} to {end}...")
        try:
            articles = fetch_nyt_finance_articles(pages=100, start_date=start, end_date=end)
            driver = webdriver.Chrome(service=service, options=options)
            for i, article in enumerate(articles):
                print(f"\n📰 {i+1}: {article['headline']}")
        
                full_text = fetch_article_text(article['url'])
            
                print("fetched text")
                sentiment = analyze_sentiment(full_text)
                print("fetched sentiment")
                summary = summarize_article(full_text)
                print("fetched summary")
                entities = extract_entities(full_text)
                print("fetched entities")
                save_to_pg(article, full_text, sentiment, summary, entities)
                print(f"✅ Saved to DB with sentiment='{sentiment}'")
            driver.quit()
            log_scrape_result(LOG_FILE, year, month, start, end, len(articles), True)
        except Exception as e:
            print(f"❌ Failed to scrape {start}-{end}: {e}")
            log_scrape_result(LOG_FILE, year, month, start, end, 0, False, str(e))
        time.sleep(random.uniform(3, 6))

