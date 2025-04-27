import multiprocessing
import requests
import os
import json
import psycopg2
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# --- Load config
load_dotenv()
nyt_api_key = os.getenv("NYT_API_KEY")
URL = "https://api.nytimes.com/svc/archive/v1/{year}/{month}.json"

# --- Selenium setup
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
service = Service('/usr/local/bin/chromedriver')

# --- Helper functions
def fetch_articles_by_month(year, month):
    try:
        url = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json"
        params = {"api-key": nyt_api_key}
        response = requests.get(url, params=params, timeout=20)
        if response.status_code != 200:
            print(f"❌ Failed to fetch {year}-{month:02d}: {response.status_code}")
            return []
        data = response.json()
        return data['response']['docs']
    except Exception as e:
        print(f"❌ Error fetching archive {year}-{month:02d}: {e}")
        return []

def fetch_article_text(driver, url):
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ''
        for p in paragraphs:
            text = p.get_text()
            if text and not text.startswith('By') and 'Advertisement' not in text:
                article_text += text + ' '
        return article_text.strip()
    except Exception as e:
        print(f"⚠️ Error fetching article text from {url}: {e}")
        return ""

def save_to_pg(article, full_text, sentiment, summary_generated, entities):
    try:
        conn = psycopg2.connect(
            dbname="nlp_articles",
            user="nlp_user",
            password="secret",
            host="localhost",
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
    except Exception as e:
        print(f"❌ DB Save Error: {e}")

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

# --- Worker process per month
def process_month(year, month):
    print(f"🚀 Starting scrape for {year}-{month:02d}")

    driver = webdriver.Chrome(service=service, options=options)
    articles = fetch_articles_by_month(year, month)
    print(f"✅ Found {len(articles)} articles for {year}-{month:02d}")

    for article in articles:
        article['url'] = article.get('web_url', '')

        if 'published_date' not in article:
            article['published_date'] = datetime.utcnow().isoformat()

        if not article['url']:
            continue

        full_text = fetch_article_text(driver, article['url'])

        if len(full_text.strip()) < 300:
            continue

        sentiment = analyze_sentiment(full_text)
        summary_generated = summarize_article(full_text)
        article['summary'] = article.get('abstract', '') or summary_generated
        entities = extract_entities(full_text)

        save_to_pg(article, full_text, sentiment, summary_generated, entities)
        print(f"✅ Saved {article['headline']['main'][:70]}...")

        time.sleep(random.uniform(1, 2))  # polite

    driver.quit()
    print(f"🏁 Finished scrape for {year}-{month:02d}")

# --- Parallelize scraping
if __name__ == "__main__":
    processes = []
    for year in range(2023, 2025):
        for month in range(1, 13):
            if year == 2025 and month > 4:
                break  # only up to April 2025
            p = multiprocessing.Process(target=process_month, args=(year, month))
            processes.append(p)
            p.start()
            time.sleep(random.uniform(0.5, 1.5))  # small stagger to avoid instant flood

    for p in processes:
        p.join()
