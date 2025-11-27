import time
from pathlib import Path
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

DROPDOWN_XPATH = '//*[@id="category"]/div/div[2]/div[2]/div[1]/div/select'
PRODUCT_LIST_XPATH = '//*[@id="category"]/div/div[2]/div[2]/div[2]/div'
PRODUCT_TILE_SELECTOR = "div.product-tile"

PROGRESS_XPATH = "//div[contains(@class,'progress-row')]/p"
SHOW_MORE_XPATH = "//div[contains(@class,'progress-row')]//a[contains(., 'Show More')]"

PRICE_REGEX = r"£\s*\d+(?:\.\d+)?"

BRAND_FILTER_CONTAINER_XPATH = '//*[@id="category"]/div/div[2]/div[1]/div/div/div[2]'
BRAND_ITEM_SELECTOR = "div.checklist.filter-block a.generic-selector-name"
BRAND_FILTER_CONTAINER_CSS = "div.filters-row.filters-brand div.filters-content"
SIDEBAR_SCROLL_CONTAINER_CSS = "div.sidebar.product-filter.scrollbar"


def current_timestamp() -> str:
    '''Returns the UTC timestamp format'''
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# def get_brand_filters(driver, timeout: int = 10, max_scroll_steps: int = 200):
#     """
#     Scrolls through the (likely virtualised) Brand filter list and returns a list of:
#         [{'name': 'Royal Canin', 'url': 'https://...brand=Royal%20Canin', 'count': '144'}, ...]

#     Works even when only a few brand nodes exist in the DOM at once:
#       - repeatedly read *visible* brand entries
#       - scroll the container down by one viewport
#       - accumulate unique brands by href / name
#       - stop when scrollTop stops changing (we're at the bottom) or max_scroll_steps reached.
#     """
#     # 1) Locate the brand filters-content container
#     try:
#         container = WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS))
#         )
#     except TimeoutException:
#         print("[ERROR] Brand filter container not found.")
#         return []

#     # Make sure it's in view
#     try:
#         driver.execute_script(
#             "arguments[0].scrollIntoView({block: 'center'});", container
#         )
#     except Exception:
#         pass

#     # Start at the top
#     try:
#         driver.execute_script("arguments[0].scrollTop = 0;", container)
#     except Exception:
#         pass

#     # We'll accumulate unique brands across all scroll positions
#     seen_by_href = {}  # href -> {name, url, count}

#     last_scroll_top = -1
#     still_rounds = 0

#     for step in range(max_scroll_steps):
#         try:
#             links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
#         except StaleElementReferenceException:
#             # Container may be re-rendered; re-find it and retry once
#             try:
#                 container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
#                 links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
#             except Exception:
#                 break

#         # 2) Read visible brands on this "page" of the virtualised list
#         for link in links:
#             try:
#                 href = link.get_attribute("href")
#                 if not href:
#                     continue

#                 spans = link.find_elements(By.TAG_NAME, "span")
#                 name_text = None
#                 count_text = None
#                 for s in spans:
#                     cls = s.get_attribute("class") or ""
#                     if "ml-count" in cls:
#                         count_text = s.text.strip()
#                     else:
#                         if name_text is None:
#                             name_text = s.text.strip()

#                 if not name_text:
#                     continue

#                 if href not in seen_by_href:
#                     seen_by_href[href] = {
#                         "name": name_text,
#                         "url": href,
#                         "count": count_text or "",
#                     }
#             except StaleElementReferenceException:
#                 # if one link goes stale mid-loop, just skip it
#                 continue

#         # 3) Scroll down by one viewport height
#         try:
#             scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
#             client_height = driver.execute_script("return arguments[0].clientHeight;", container)
#             scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
#         except StaleElementReferenceException:
#             try:
#                 container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
#                 scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
#                 client_height = driver.execute_script("return arguments[0].clientHeight;", container)
#                 scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
#             except Exception:
#                 break

#         # If we can't scroll further (bottom reached)
#         if scroll_top + client_height >= scroll_height - 2:
#             still_rounds += 1
#         else:
#             still_rounds = 0

#         if still_rounds >= 3:
#             # we hit the bottom several times -> done
#             break

#         # If scrollTop isn't changing, we're probably stuck
#         if scroll_top == last_scroll_top:
#             still_rounds += 1
#             if still_rounds >= 3:
#                 break
#         else:
#             last_scroll_top = scroll_top

#         # Perform scroll: move down by one viewport
#         try:
#             driver.execute_script(
#                 "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
#                 container,
#             )
#         except StaleElementReferenceException:
#             try:
#                 container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
#                 driver.execute_script(
#                     "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
#                     container,
#                 )
#             except Exception:
#                 break

#         time.sleep(0.3)  # small delay to allow new items to render

#     brands = list(seen_by_href.values())
#     print(f"[INFO] Collected {len(brands)} unique brand filters across virtualised list.")
#     return brands

def get_brand_filters(driver, timeout: int = 10, max_scroll_steps: int = 200):
    """
    Scrolls through the (likely virtualised) Brand filter list and returns a list of:
        [{'name': 'Royal Canin', 'url': 'https://...brand=Royal%20Canin', 'count': '144'}, ...]
    """

    # --- NEW: "hydrate" the page in headless by forcing a scroll cycle ---
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.7)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.7)
    except Exception:
        pass

    # 1) Locate the brand filters-content container
    try:
        container = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS))
        )
    except TimeoutException:
        print("[ERROR] Brand filter container not found.")
        return []

    # Make sure it's in view
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", container
        )
    except Exception:
        pass

    # --- NEW: wait for at least a few brand items to be present ---
    # sometimes the container appears first, items get injected a bit later
    min_initial_items = 5
    for _ in range(20):  # up to ~10 seconds (20 * 0.5s)
        try:
            initial_links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
            if len(initial_links) >= min_initial_items:
                break
        except StaleElementReferenceException:
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
            except Exception:
                break
        time.sleep(0.5)

    # Start at the top of the brand list
    try:
        driver.execute_script("arguments[0].scrollTop = 0;", container)
    except Exception:
        pass

    # We'll accumulate unique brands across all scroll positions
    seen_by_href = {}  # href -> {name, url, count}

    last_scroll_top = -1
    still_rounds = 0

    for step in range(max_scroll_steps):
        try:
            links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
        except StaleElementReferenceException:
            # Container may be re-rendered; re-find it and retry once
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
                links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
            except Exception:
                break

        # 2) Read visible brands on this "page" of the virtualised list
        for link in links:
            try:
                href = link.get_attribute("href")
                if not href:
                    continue

                spans = link.find_elements(By.TAG_NAME, "span")
                name_text = None
                count_text = None
                for s in spans:
                    cls = s.get_attribute("class") or ""
                    if "ml-count" in cls:
                        count_text = s.text.strip()
                    else:
                        if name_text is None:
                            name_text = s.text.strip()

                if not name_text:
                    continue

                if href not in seen_by_href:
                    seen_by_href[href] = {
                        "name": name_text,
                        "url": href,
                        "count": count_text or "",
                    }
            except StaleElementReferenceException:
                # if one link goes stale mid-loop, just skip it
                continue

        # 3) Scroll down by one viewport height
        try:
            scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
            client_height = driver.execute_script("return arguments[0].clientHeight;", container)
            scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
        except StaleElementReferenceException:
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
                scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
                client_height = driver.execute_script("return arguments[0].clientHeight;", container)
                scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
            except Exception:
                break

        # If we can't scroll further (bottom reached)
        if scroll_top + client_height >= scroll_height - 2:
            still_rounds += 1
        else:
            still_rounds = 0

        if still_rounds >= 3:
            # we hit the bottom several times -> done
            break

        # If scrollTop isn't changing, we're probably stuck
        if scroll_top == last_scroll_top:
            still_rounds += 1
            if still_rounds >= 3:
                break
        else:
            last_scroll_top = scroll_top

        # Perform scroll: move down by one viewport
        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
                container,
            )
        except StaleElementReferenceException:
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
                    container,
                )
            except Exception:
                break

        time.sleep(0.3)  # small delay to allow new items to render

    brands = list(seen_by_href.values())
    print(f"[INFO] Collected {len(brands)} unique brand filters across virtualised list.")
    return brands


def click_brand_filter(driver, brand_name: str,
                       timeout: int = 10,
                       max_scroll_steps: int = 200) -> bool:
    """
    On the *current* category page, scroll the Brand filter list,
    find the entry whose visible name == brand_name, and click it
    (toggling it on or off).

    Returns True if clicked successfully, False otherwise.
    """
    # 1) Locate the brand filters-content container
    try:
        container = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS))
        )
    except TimeoutException:
        print(f"[ERROR] Brand filter container not found when trying to click '{brand_name}'.")
        return False

    # Make sure it's in view and start at top
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", container
        )
        driver.execute_script("arguments[0].scrollTop = 0;", container)
    except Exception:
        pass

    # Snapshot state before click (to detect change)
    try:
        before_url = driver.current_url
        before_count = len(driver.find_elements(By.CSS_SELECTOR, ".product-list .product-tile"))
    except Exception:
        before_url = driver.current_url
        before_count = 0

    last_scroll_top = -1
    still_rounds = 0

    for step in range(max_scroll_steps):
        # 2) Look at currently visible brand entries
        try:
            links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
        except StaleElementReferenceException:
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
                links = container.find_elements(By.CSS_SELECTOR, BRAND_ITEM_SELECTOR)
            except Exception:
                break

        for link in links:
            try:
                # name span = the span without 'ml-count'
                spans = link.find_elements(By.TAG_NAME, "span")
                name_text = None
                for s in spans:
                    cls = s.get_attribute("class") or ""
                    if "ml-count" in cls:
                        continue
                    if name_text is None:
                        name_text = s.text.strip()

                if not name_text:
                    continue

                if name_text.strip() == brand_name.strip():
                    # Found our brand; click to toggle
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", link
                    )
                    try:
                        link.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", link)

                    # Wait for something to change: URL *or* product count
                    try:
                        WebDriverWait(driver, timeout).until(
                            lambda d: d.current_url != before_url or
                                      len(d.find_elements(By.CSS_SELECTOR,
                                                          ".product-list .product-tile")) != before_count
                        )
                    except TimeoutException:
                        # Not fatal; maybe change is small
                        pass

                    print(f"[INFO] Clicked brand filter '{brand_name}'.")
                    return True
            except StaleElementReferenceException:
                continue

        # 3) Scroll down by one viewport and keep searching
        try:
            scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
            client_height = driver.execute_script("return arguments[0].clientHeight;", container)
            scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
        except StaleElementReferenceException:
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
                scroll_top = driver.execute_script("return arguments[0].scrollTop;", container)
                client_height = driver.execute_script("return arguments[0].clientHeight;", container)
                scroll_height = driver.execute_script("return arguments[0].scrollHeight;", container)
            except Exception:
                break

        # bottom detection
        if scroll_top + client_height >= scroll_height - 2:
            still_rounds += 1
        else:
            still_rounds = 0

        if still_rounds >= 3:
            break

        if scroll_top == last_scroll_top:
            still_rounds += 1
            if still_rounds >= 3:
                break
        else:
            last_scroll_top = scroll_top

        try:
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
                container,
            )
        except StaleElementReferenceException:
            try:
                container = driver.find_element(By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS)
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
                    container,
                )
            except Exception:
                break

        time.sleep(0.3)

    print(f"[WARN] Could not find brand filter '{brand_name}' to click.")
    return False

# %%
# ---------- HELPERS ----------

def parse_progress(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse 'Showing 100 of 1027 products' style text.
    Returns (shown, total) or (None, None) if it doesn't match.
    """
    if not text:
        return None, None
    m = re.search(r"Showing\s+(\d+)\s+of\s+(\d+)", text)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def get_progress(driver, timeout: int = 10) -> Tuple[Optional[int], Optional[int]]:
    """
    Try to read the progress text. Returns (shown, total) or (None, None) if not found.
    Does NOT raise on timeout.
    """
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, PROGRESS_XPATH))
        )
        return parse_progress(el.text)
    except TimeoutException:
        return None, None
    except StaleElementReferenceException:
        # try once more with a short wait
        try:
            el = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, PROGRESS_XPATH))
            )
            return parse_progress(el.text)
        except Exception:
            return None, None


# ---------- STEP 1: SELECT PER-PAGE ----------

def set_per_page(driver, value: str = "100", timeout: int = 10) -> None:
    """
    Select the 'per page' dropdown value.
    Fallbacks:
      - if dropdown is not found, just return (scrape whatever is there)
      - if given value is not available, keeps current selection.
      - waits until at least 1 product tile is visible.
    """
    try:
        dropdown_element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, DROPDOWN_XPATH))
        )
    except TimeoutException:
        print("[WARN] per-page dropdown not found, continuing with default page size.")
        return

    try:
        dropdown = Select(dropdown_element)
        # Check if value exists before selecting
        available_values = [opt.get_attribute("value") for opt in dropdown.options]
        if value in available_values:
            dropdown.select_by_value(value)
        else:
            print(f"[WARN] per-page value '{value}' not available; using existing setting.")
    except Exception as e:
        print(f"[WARN] Failed to interact with dropdown: {e}")

    # Wait for some products to appear (or re-appear after change)
    try:
        WebDriverWait(driver, timeout * 2).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".product-list .product-tile")) > 0
        )
    except TimeoutException:
        print("[WARN] No product tiles detected after setting per-page; continuing anyway.")


# ---------- STEP 2: LOAD ALL PRODUCTS ----------

def load_all_products(driver,
                      max_clicks: int = 50,
                      timeout: int = 20) -> None:
    """
    Repeatedly clicks 'Show More' until:
      - Progress text says shown >= total, OR
      - 'Show More' button is not found/clickable, OR
      - Product count stops increasing, OR
      - max_clicks reached.
    Uses both progress text (if available) and product count as fallbacks.
    """
    # Initial progress (may be None, None)
    shown, total = get_progress(driver, timeout=5)
    print(f"[INFO] Initial progress: shown={shown}, total={total}")

    # Initial product count
    try:
        count_before = len(driver.find_elements(By.CSS_SELECTOR, PRODUCT_TILE_SELECTOR))
    except Exception:
        count_before = 0

    click_count = 0

    while True:
        # If progress text says we're done, stop
        if shown is not None and total is not None and shown >= total:
            print("[INFO] Progress text indicates all products loaded.")
            break

        if click_count >= max_clicks:
            print(f"[WARN] Reached max_clicks={max_clicks}, stopping 'Show More' loop.")
            break

        # Try to locate Show More
        try:
            show_more_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, SHOW_MORE_XPATH))
            )
        except TimeoutException:
            print("[INFO] 'Show More' button not found or not clickable. Assuming end.")
            break

        try:
            # Scroll and click via JS to avoid intercepted click issues
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", show_more_btn
            )
            driver.execute_script("arguments[0].click();", show_more_btn)
        except StaleElementReferenceException:
            print("[WARN] 'Show More' became stale, retrying once...")
            try:
                show_more_btn = driver.find_element(By.XPATH, SHOW_MORE_XPATH)
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", show_more_btn
                )
                driver.execute_script("arguments[0].click();", show_more_btn)
            except Exception:
                print("[ERROR] Failed to click 'Show More' after staleness; stopping.")
                break
        except Exception as e:
            print(f"[ERROR] Error clicking 'Show More': {e}")
            break

        click_count += 1

        # Wait until product count increases
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, PRODUCT_TILE_SELECTOR)) > count_before
            )
        except TimeoutException:
            print("[WARN] Product count did not increase after clicking 'Show More'; stopping.")
            break

        # Update counters
        new_count = len(driver.find_elements(By.CSS_SELECTOR, PRODUCT_TILE_SELECTOR))
        shown, total = get_progress(driver, timeout=3)
        count_before = new_count

        print(f"[INFO] After click {click_count}: product_count={new_count}, progress={shown}/{total}")


# ---------- STEP 3: SCRAPE PRODUCTS ----------

def parse_price_block(price_block_text: str) -> List[str]:
    """
    Extract all £-formatted prices from a given text block.
    """
    return [p.strip() for p in re.findall(PRICE_REGEX, price_block_text)]


def scrape_products(driver) -> List[Dict[str, Optional[str]]]:
    """
    Scrape all product tiles from the product-list container.
    Returns a list of dicts with:
        url, name, one_time_price, old_price,
        repeat_price, repeat_discount, promo_text, has_sale_tag
    """
    products: List[Dict[str, Optional[str]]] = []

    try:
        container = driver.find_element(By.XPATH, PRODUCT_LIST_XPATH)
    except NoSuchElementException:
        print("[ERROR] Product list container not found.")
        return products

    tiles = container.find_elements(By.CSS_SELECTOR, PRODUCT_TILE_SELECTOR)
    print(f"[INFO] Found {len(tiles)} product tiles.")

    for i, tile in enumerate(tiles, start=1):
        try:
            # --- LINK ---
            link_el = tile.find_element(By.CSS_SELECTOR, "a.product-link")
            product_url = link_el.get_attribute("href")

            # --- NAME ---
            name_el = tile.find_element(By.CSS_SELECTOR, "h3.ellipsis")
            name = name_el.text.strip()

            # --- PRICE BLOCK ---
            price_block = tile.find_element(By.CSS_SELECTOR, ".price-bottom .price")
            price_text = price_block.text

            prices = parse_price_block(price_text)
            one_time_price = prices[0] if prices else None

            # Old/original price if there is a <del>
            old_price = None
            del_els = price_block.find_elements(By.TAG_NAME, "del")
            if del_els:
                m = re.search(PRICE_REGEX, del_els[0].text)
                if m:
                    old_price = m.group(0).strip()

            # --- REPEAT & SAVE ---
            repeat_price = None
            repeat_discount = None

            save_price_blocks = tile.find_elements(By.CSS_SELECTOR, ".save-price span")
            if save_price_blocks:
                rs_text = save_price_blocks[0].text
                m = re.search(PRICE_REGEX, rs_text)
                if m:
                    repeat_price = m.group(0).strip()

                rs_discount_els = tile.find_elements(By.CSS_SELECTOR, ".rs-discount")
                if rs_discount_els:
                    repeat_discount = rs_discount_els[0].text.strip()

            # --- PROMOTION / DISCOUNT LABEL ---
            promo_text = None
            promo_els = tile.find_elements(By.CSS_SELECTOR, ".promotion-msg span")
            if promo_els:
                promo_text = promo_els[0].text.strip()

            # --- SALE TAG IMAGE FLAG ---
            has_sale_tag = bool(tile.find_elements(By.CSS_SELECTOR, "img.sale-tag"))

            products.append(
                {
                    "url": product_url,
                    "name": name,
                    "one_time_price": one_time_price,
                    "old_price": old_price,
                    "repeat_price": repeat_price,
                    "repeat_discount": repeat_discount,
                    "promo_text": promo_text,
                    "has_sale_tag": has_sale_tag,
                    "scrape_timestamp": current_timestamp(),
                }
            )

        except Exception as e:
            # Don't let a single bad tile kill the whole scrape
            print(f"[WARN] Failed to parse tile #{i}: {e}")

    return products
# %%
def scrape_all_products_by_brand_toggle(driver, base_url: str) -> List[Dict[str, Optional[str]]]:
    """
    For each brand:
      - Click brand checkbox ON
      - Set per-page to 100
      - Load all products via 'Show More'
      - Scrape products
      - Click brand checkbox OFF (to return to unfiltered state)
    Returns a list of product dicts with an added 'brand' field.
    """
    all_products: List[Dict[str, Optional[str]]] = []

    # Start from the base category page once
    driver.get(base_url)

    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, BRAND_FILTER_CONTAINER_CSS))
    )


    brand_filters = get_brand_filters(driver)
    if not brand_filters:
        print("[WARN] No brands found; nothing to scrape.")
        return all_products

    brand_names = [b["name"] for b in brand_filters]
    print(f"[INFO] Will scrape {len(brand_names)} brands.")

    for brand_name in brand_names:
        print(f"\n[INFO] Processing brand '{brand_name}'")

        # 1) Ensure we are on the base page with no brand filter applied.
        #    If something went wrong previously, you can uncomment this:
        # driver.get(base_url)

        # 2) Click brand ON
        if not click_brand_filter(driver, brand_name):
            print(f"[WARN] Skipping brand '{brand_name}' (could not toggle on).")
            continue

        # 3) Run your existing product pipeline under this filter
        set_per_page(driver, value="100", timeout=10)
        load_all_products(driver, max_clicks=50, timeout=20)
        products = scrape_products(driver)

        # 4) Attach brand
        for p in products:
            p["brand"] = brand_name

        print(f"[INFO] Scraped {len(products)} products for brand '{brand_name}'.")
        all_products.extend(products)

        # 5) Click brand OFF to clear the filter
        if not click_brand_filter(driver, brand_name):
            print(f"[WARN] Could not toggle OFF brand '{brand_name}'. "
                  f"You may want to reload base_url before next loop.")

    print(f"\n[INFO] Total products scraped across all brands: {len(all_products)}")
    return all_products
