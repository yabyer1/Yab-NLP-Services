import psycopg2

def init_pg_db():
    conn = psycopg2.connect(
        dbname="nlp_articles",
        user="nlp_user",
        password="secret",
        host="localhost",  # if inside Docker, use 'postgres'
        port="5433"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nyt_articles (
            id TEXT PRIMARY KEY,
            headline TEXT,
            summary TEXT,
            url TEXT,
            published_date TIMESTAMP,
            full_text TEXT,
            sentiment TEXT,
            summary_generated TEXT,
            entities JSONB,
            scraped_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_pg_db()