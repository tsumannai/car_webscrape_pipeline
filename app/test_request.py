import argparse
import requests

parser = argparse.ArgumentParser(description="Call FastAPI scraper endpoint")
parser.add_argument("url", help="Model URL to scrape")

args = parser.parse_args()

payload = {"url": args.url}
response = requests.post("http://127.0.0.1:8000/scrape", json=payload)

print(response.json())