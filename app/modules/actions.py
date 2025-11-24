import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def human_like_delay(action: str):
    '''Returns a human like delay based on type of action performed'''
    action_types = {
        "simple" : (1,3),
        'reflex' : (0.2,1),
        'read' : (3,7)
    }
    delay = random.uniform(*action_types[action])
    time.sleep(delay)
    return None

def accept_cookies(driver, timeout: int = 10):
    '''Clicks the accept all cookies button, uses several known xpaths'''
    xpaths = [
        '//button[@data-cky-tag="accept-button"]',
        '//button[@aria-label="Accept All"]',
        '//button[contains(text(), "Accept All")]',
        '//button[contains(text(), "Accept")]',
    ]
    for xp in xpaths:
        try:
            # Give up to 10 seconds for the button to be clickable
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            btn.click()
            print(f"Clicked cookie button using XPath: {xp}")
            return
        except Exception:
            continue


def get_model_title(driver):
    '''Scrapes the model title from the page and returns as string'''
    try:
        el = driver.find_element(
            By.XPATH,
            '//h1[contains(@class, "ModelHeaderStyles__ModelTitle")]'
        )
        return el.text.strip()
    except Exception:
        return None

def get_model_card_stats(driver) -> dict:
    '''Scrapes the summary stats from ModelCarFeatureList on page and returns a dictionary'''
    stats = {}

    # All rows in that feature list
    rows = driver.find_elements(
        By.XPATH,
        '//ul[contains(@class, "ModelCardFeatureList")]/li'
    )

    for row in rows:
        try:
            # Find the wrapper that contains the two text spans
            wrapper = row.find_element(
                By.XPATH,
                './/span[contains(@class, "ModelCardFeatureListItemTextWrapper")]'
            )

            # Find the two text spans *inside* that wrapper
            text_spans = wrapper.find_elements(
                By.XPATH,
                './/span[contains(@class, "ModelCardFeatureListItemText")]'
            )

            if len(text_spans) == 2:

                # First span = label, second span = value
                label_raw = text_spans[0].text.strip()
                value = text_spans[1].text.strip()

                # Clean label: remove ':' and '*' at the end if present
                label = label_raw.rstrip(':*').strip()

                stats[label] = value
            
            else:
                continue

        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    return stats

def expand_accordion(driver, section):
    """ Expands a given accordion section by clicking its header """
    xpath = (
        '//div[contains(@class, "AccordionItemStyles__AccordionItemTitle") '
        f'and .//span[contains(normalize-space(.), "{section}")]]'
    )

    header = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )

    # Execute Javascript inside browser to scroll and click
    driver.execute_script("arguments[0].scrollIntoView(true);", header)

    try:
        header.click()
    except Exception:
    # Click via JS if normal click fails
        driver.execute_script("arguments[0].click();", header)


def get_features(driver, section = 'Interior Features') -> dict:
    """
    Scrape a specified part of the accordion section.
    Returns a dict: { feature_name: bool_available }
    """
    features = {}

    try:
        # Wait for any accordion to be on the page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "AccordionItemStyles__AccordionItemContainer")]')
            )
        )
        
        # Wait for and click section of accordion

        expand_accordion(driver, section)
        container = driver.find_element(
            By.XPATH,
            (
                '//div[contains(@class, "AccordionItemStyles__AccordionItemContainer")]'
                f'[.//span[contains(normalize-space(.), "{section}")]]'
            )
        )

    except Exception as e:
        print(f"Could not find {section} accordion: {e}")
        return features

    # Table rows inside element
    rows = container.find_elements(By.XPATH, './/table//tr')

    for i, row in enumerate(rows, start=1):
        try:
            name_el = row.find_element(By.XPATH, './td[1]')
            feature_name = name_el.text.strip()

            icon_el = row.find_element(
                By.XPATH,
                './td[2]//span[contains(@class, "IconStyles__StyledIcon")]'
            )

            raw_title = icon_el.get_attribute("title") or ""
            icon_title = raw_title.lower()

            # map 'check-circled' / 'cross-circled' -> bool
            if "check" in icon_title:
                available = True
            elif "cross" in icon_title:
                available = False
            else:
                available = None  # unexpected case

            features[feature_name] = available
            
        except Exception as e:
                print(f"Skipping a row due to error: {e}")
        pass
    return features