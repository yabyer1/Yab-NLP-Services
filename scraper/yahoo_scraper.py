import requests, csv
from bs4 import BeautifulSoup
from time import sleep
import psycopg2
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
}

KEYWORDS = ["brexit", "inflation", "elections", "interest rates", "immigration", "Ukraine", "Russia", "Tariffs", "Trump"]
from urllib.parse import urlparse, parse_qs, unquote

def extract_final_url(yahoo_redirect_url):
    try:
        parsed = urlparse(yahoo_redirect_url)
        qs = parse_qs(parsed.query)
        if 'RU' in qs:
            return unquote(qs['RU'][0])
    except Exception as e:
        print(f"⚠️ Failed to extract final URL: {e}")
    return yahoo_redirect_url  # fallback

def fetch_article_text(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        time.sleep(3)  # Let JS render

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # Grab ALL visible text
        text = soup.get_text(separator='\n', strip=True)

        # Optional: filter out junky lines
        lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 20]
        return "\n".join(lines)

    except Exception as e:
        print(f"⚠️ Selenium failed on {url}: {e}")
        return ""

def get_article(card):
    headline = card.h4.text if card.h4 else ""
    source = card.find('span', class_='s-source').text if card.find('span', class_='s-source') else ""
    posted = card.find('span', class_='fc-2nd').text if card.find('span', class_='fc-2nd') else ""
    desc = card.find('p').text if card.find('p') else ""
    link = card.a['href'] if card.a else ""
    return [headline, source, posted, desc, link]

def get_the_news(search):
    template = 'https://news.search.yahoo.com/search?p={}'
    url = template.format(search.replace(" ", "+"))

    articles = []
    links = set()

    while True:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')
        cards = soup.find_all('div', class_='NewsArticle')

        for card in cards:
            article = get_article(card)
            link = article[-1]
            if link not in links:
                links.add(link)
                articles.append(article)

        next_link = soup.find('a', class_='next')
        if next_link:
            url = next_link.get('href')
            sleep(1.5)
        else:
            break

    return articles

# --- NLP microservices (optional, plug in your existing endpoints) ---
def summarize_article(text):
    try:
        r = requests.get("http://localhost:8001/summarize", params={"text": text})
        return r.json().get("summary", "")
    except:
        return ""

def analyze_sentiment(text):
    try:
        r = requests.get("http://localhost:8000/sentiment", params={"text": text})
        return r.json().get("label", "unknown")
    except:
        return "error"

# --- Save to DB ---
def save_to_pg(article, summary, sentiment, url, published_at=None):
    if not published_at:
        published_at = datetime.utcnow()  
    conn = psycopg2.connect(
        dbname="nlp_articles",
        user="nlp_user",
        password="secret",
        host="localhost",
        port="5433"
    )
    cursor = conn.cursor()
    unique_id = f"YQ_{hash(article[-1]) % 1000000}"

    cursor.execute("""
        INSERT INTO nyt_articles (
            id, headline, summary, url, published_date,
            full_text, sentiment, summary_generated, entities, scraped_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (
        unique_id,
        article[0],  # headline
        article[3],  # short Yahoo blurb
        url,  # link
        published_at,  # published date string
        full_text,  # full text (fallback to blurb)
        sentiment,
        summary,
        json.dumps([]),
        datetime.utcnow()
    ))
    conn.commit()
    conn.close()

# --- Main ---
if __name__ == "__main__":
    for keyword in KEYWORDS:
        print(f"🔍 Searching: {keyword}")
        articles = get_the_news(keyword)
        print(f"🔗 Found {len(articles)} articles for {keyword}")
        
        for art in articles:
            real_url = extract_final_url(art[4])
            full_text = art[3]
            summary = summarize_article(art[3])
            sentiment = analyze_sentiment(art[3])
            save_to_pg(art, summary, sentiment, real_url, art[2])
            print(f"✅ Saved: {art[0]}")
