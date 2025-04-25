import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.reuters.com"
HEADERS = {
     "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
}

def get_article_links(section_url):
    res = requests.get(section_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = []

    for tag in soup.select('a[href]'):
        href = tag.get('href')
        if href and '/article/' in href:
            # Normalize link
            if href.startswith('/'):
                href = BASE_URL + href
            elif href.startswith('http'):
                pass  # already full
            else:
                href = BASE_URL + '/' + href
            links.append(href.split('?')[0])

    return list(set(links))


def get_article_text(url):
    res = requests.get(url, headers=HEADERS)
    print(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    paragraphs = soup.select('div.article-body__content__17Yit p')
    if not paragraphs:
        paragraphs = soup.select('article p')

    text = ' '.join(p.get_text(strip=True) for p in paragraphs)
    word_count = len(re.findall(r'\w+', text))

    return text if word_count >= 100 else None

def scrape_reuters_section(section_url, limit=10):
    article_links = get_article_links(section_url)
    print(f"Found {len(article_links)} articles. Scraping top {limit}...")

    results = []
    for url in article_links[:limit]:
        try:
            content = get_article_text(url)
            if content:
                print(f"[✓] {url}")
                results.append({"url": url, "content": content})
            else:
                print(f"[✗] Skipped (short content): {url}")
        except Exception as e:
            print(f"[!] Error scraping {url}: {e}")

    return results

# Example usage
if __name__ == "__main__":
    section = "https://www.reuters.com/world/"  # can also use /business/ or /markets/
    articles = scrape_reuters_section(section, limit=20)
    for a in articles:
        print(a)
