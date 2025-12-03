from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from modules.file_ops import append_product_list
import modules.scraping_steps as scraper

def run_scrape(url: str):
    """
    Main scraper entrypoint.
    Called by FastAPI or any external script.
    """
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        all_products = scraper.scrape_all_products_by_brand_toggle(driver, url)
        append_product_list("../data/jollyes_products.json", all_products)
        return {
            "model_name": "Dog Food Scraper",
            "url": url,
            "files_written": [
                "data/jollyes_products.json"
            ]
        }

    finally:
        driver.quit()