import sys
import time
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from app.core.config import settings

def sanitize_url(url: str) -> str:
    if not url:
        return url
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = f"{parsed.username}:*****@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            parsed = parsed._replace(netloc=netloc)
        return urlunparse(parsed)
    except Exception:
        return url

def wait_for_db():
    db_url = settings.admin_database_url
    sanitized_url = sanitize_url(db_url)
    
    print(f"Checking database connectivity using admin/direct URL: {sanitized_url}")
    
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        
    for i in range(1, 31):
        try:
            engine = create_engine(db_url, connect_args=connect_args)
            with engine.connect() as conn:
                print("Database is ready and accessible!")
                sys.exit(0)
        except Exception as e:
            print(f"Database connection attempt {i} failed: {e}")
            if i < 30:
                print("Sleeping 1s...")
                time.sleep(1)
                
    print("Database connection timed out after 30 attempts.")
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
