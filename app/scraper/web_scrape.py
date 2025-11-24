from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraper.schemas import SUMMARY_SCHEMA, FEATURES_SCHEMA
import modules.actions as actions
import modules.parse as parse

def run_scrape(url: str):
    """
    Main scraper entrypoint.
    Called by FastAPI or any external script.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to URL
        driver.get(url)

        # Click accept cookies if prompted
        actions.accept_cookies(driver)

        # Get model title
        title = actions.get_model_title(driver)

        # Raise a runtime error if we can't find the title (car name)
        if not title:
            raise RuntimeError("Could not find model title on page")

        # Pipeline for summary section
        parse.summary_pipeline(
            driver,
            SUMMARY_SCHEMA,
            title,
            path="../data/summary.json"
        )

        # Pipeline for Accordion (interior, entertainment) section
        parse.accordion_section_pipeline(
            driver,
             ["Interior Features","Entertainment", "Driver Convenience","Security","Exterior Features","Passive Safety","Wheels","Engine/Drivetrain/Suspension"],
            FEATURES_SCHEMA,
            title
        )

        return {
            "model_name": title,
            "url": url,
            "files_written": [
                "data/summary.json",
                "data/interior_features.json",
                "data/entertainment.json",
                "data/driver convenience.json",
                "data/security.json",
                "data/exterior_features.json",
                "data/passive_safety.json",
                "data/wheels.json",
                "data/engine_drivetrain_suspension.json"
            ]
        }

    finally:
        driver.quit()