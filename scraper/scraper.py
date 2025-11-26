# scraper/scraper.py
import time
import json
import os
from typing import List
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from selenium.common.exceptions import TimeoutException, WebDriverException

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # project root (news2signals/)
DATA_PATH = os.path.join(ROOT_DIR, "data", "sample_output.json")


def make_driver(headless: bool = False, wait: float = 1.0) -> webdriver.Chrome:
    """
    Create and return a Selenium Chrome WebDriver with sensible defaults.
    - headless: run without opening a visible browser window (True for servers).
    - wait: implicit wait for DOM to settle after navigation.
    """
    opts = Options()
    #if headless:
    #    opts.add_argument("--headless=new")  # modern headless mode
    #    opts.add_argument("--disable-gpu")
    # Some useful flags for scraping stability
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("start-maximized")
    # optional: pretend to be a regular browser
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    # auto-manage chromedriver binary
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    # a short implicit wait: useful for JS-rendered elements
    driver.implicitly_wait(int(wait))
    return driver

import re

ARTICLE_RE = re.compile(r".*-\d+\.html$")  # ends with -<digits>.html

def get_moneycontrol_links(driver: webdriver.Chrome, limit: int = 10) -> List[str]:
    """
    Extract article URLs from Moneycontrol homepage using robust selectors
    and filter to only real article pages (ending with -<digits>.html).
    """
    base = "https://www.moneycontrol.com/"
    driver.get(base)
    time.sleep(2)  # let JS run
    # try scroll to load lazy content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.0)

    soup = BeautifulSoup(driver.page_source, "lxml")
    links = []

    # selectors that commonly contain article anchors
    selectors = [
        "a.list_title",            # headline links you found
        "a[href*='/news/']",
        "a[href*='/article/']",
        "a[href*='-news-']",
        "a.newslist-box",
        "div.clearfix a",
    ]

    for sel in selectors:
        for a in soup.select(sel):
            href = a.get("href")
            if not href:
                continue
            url = urljoin(base, href)
            # Keep only actual article pages (pattern matched)
            if ARTICLE_RE.match(url):
                links.append(url)
            if len(links) >= limit:
                break
        if len(links) >= limit:
            break

    # dedupe while preserving order
    links = list(dict.fromkeys(links))
    print("DEBUG: extracted article links (filtered):", len(links))
    return links[:limit]


def extract_article_text(driver: webdriver.Chrome, url: str) -> str:
    """
    Open an article URL and extract main text.
    Uses page_load_timeout and sanity checks on page_source length.
    """
    try:
        # set a page load timeout so driver.get won't hang forever
        driver.set_page_load_timeout(20)  # seconds
        driver.get(url)
    except TimeoutException:
        print(f"  TimeoutException loading {url} — trying to continue")
    except WebDriverException as e:
        print(f"  WebDriverException loading {url}: {e}")
        return ""

    time.sleep(0.8)  # let JS finish

    # sanity check: if page source is tiny, skip
    ps = driver.page_source or ""
    if len(ps) < 3000:
        print(f"  Page source too small ({len(ps)} bytes). Skipping.")
        return ""

    soup = BeautifulSoup(ps, "lxml")

    # Article selectors — try a few options
    selectors = [
        "div.article_text",
        "div.mcontent",
        "div.article",
        "div#content",
        "article",
    ]

    for sel in selectors:
        node = soup.select_one(sel)
        if node:
            text = node.get_text(separator="\n").strip()
            if len(text) > 120:
                return " ".join(line.strip() for line in text.splitlines() if line.strip())

    # fallback: attempt to join <p> tags but ensure enough content
    paragraphs = soup.select("article p") or soup.select("p")
    text = " ".join([p.get_text(strip=True) for p in paragraphs])
    if len(text) > 120:
        return text.strip()

    # nothing useful found
    return ""



def run_scrape(limit: int = 5):
    """
    Main driver for scraping:
    - Launches Selenium
    - Fetches links from homepage
    - Visits each article and extracts text
    - Stores JSON output to data/sample_output.json
    """
    driver = make_driver(headless=True, wait=1.0)
    try:
        links = get_moneycontrol_links(driver, limit=limit)
        print(f"Found {len(links)} article links.")
        results = []
        for idx, link in enumerate(links, start=1):
            print(f"[{idx}/{len(links)}] Fetching: {link}")
            try:
                article_text = extract_article_text(driver, link)
                if not article_text:
                    print(f"  Skipped (no article content): {link}")
                    continue
                results.append({"url": link, "text": article_text})

            except Exception as e:
                print(f"  Failed to fetch article {link}: {e}")

        # ensure data folder exists
        os.makedirs(os.path.join(ROOT_DIR, "data"), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(results)} articles to {DATA_PATH}")
        time.sleep(10)

    finally:
        driver.quit()


if __name__ == "__main__":
    run_scrape(limit=6)
