"""
SHL Product Catalogue Scraper
Scrapes all Individual Test Solutions from SHL catalogue
Target: 377+ assessments with full metadata
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import os
import re
from tqdm import tqdm

BASE_URL = "https://www.shl.com"
CATALOGUE_URL = "https://www.shl.com/solutions/products/product-catalog/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.shl.com/",
    "Connection": "keep-alive",
}

# SHL test type letter -> full name mapping
TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "M": "Motivation",
    "O": "Personality & Behaviour",
    "P": "Personality & Behaviour",
    "S": "Simulations",
    "T": "Technology",
    "V": "Video Interview",
}


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_catalogue_page(session: requests.Session, start: int) -> str:
    """Fetch a paginated catalogue listing page."""
    params = {"start": start}
    resp = session.get(CATALOGUE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_catalogue_page(html: str) -> list[dict]:
    """Parse assessment rows from a catalogue listing page."""
    soup = BeautifulSoup(html, "lxml")
    assessments = []

    # Main table with assessments
    table = soup.find("table", class_=lambda c: c and "custom__table" in c)
    if not table:
        # Try alternative selector
        table = soup.find("div", class_=lambda c: c and "custom__table" in c)

    if not table:
        return assessments

    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        # Name & URL cell (first cell)
        name_cell = cells[0]
        link_tag = name_cell.find("a")
        if not link_tag:
            continue

        name = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        if not href:
            continue
        url = urljoin(BASE_URL, href)

        # Remote Testing (cell index 1) - check for filled dot/circle
        remote_cell = cells[1]
        remote_support = "Yes" if remote_cell.find(class_=lambda c: c and ("circle" in c.lower() or "dot" in c.lower() or "-yes" in c.lower())) else "No"
        remote_support = "Yes" if remote_cell.find("span") and "-no" not in str(remote_cell).lower() else remote_support

        # Adaptive/IRT (cell index 2)
        adaptive_cell = cells[2]
        adaptive_support = "Yes" if adaptive_cell.find(class_=lambda c: c and ("circle" in c.lower() or "dot" in c.lower() or "-yes" in c.lower())) else "No"
        adaptive_support = "Yes" if adaptive_cell.find("span") and "-no" not in str(adaptive_cell).lower() else adaptive_support

        # Test Types (cell index 3+) - look for span letters
        test_type_letters = []
        for cell in cells[3:]:
            spans = cell.find_all("span", class_=lambda c: c and "filter-icon" in c)
            for span in spans:
                letter = span.get_text(strip=True).upper()
                if letter in TEST_TYPE_MAP:
                    test_type_letters.append(letter)
            # Also try getting data attribute
            for span in cell.find_all("span"):
                text = span.get_text(strip=True).upper()
                if len(text) == 1 and text in TEST_TYPE_MAP:
                    test_type_letters.append(text)

        test_types = list(set([TEST_TYPE_MAP[l] for l in test_type_letters if l in TEST_TYPE_MAP]))

        assessments.append({
            "name": name,
            "url": url,
            "remote_support": remote_support,
            "adaptive_support": adaptive_support,
            "test_type": test_types,
            "description": "",
            "duration": None,
        })

    return assessments


def parse_catalogue_page_v2(html: str) -> list[dict]:
    """
    Alternative parser using the known SHL table structure.
    SHL uses a table where each row has:
    col0: Assessment name (link)
    col1: Remote Testing (dot icon)
    col2: Adaptive/IRT (dot icon)
    col3+: Test type icons (letters A,B,C,K,P,S...)
    """
    soup = BeautifulSoup(html, "lxml")
    assessments = []

    # Find all anchor tags linking to product catalog view pages
    all_rows = []

    # Try finding table body rows
    for tbody in soup.find_all("tbody"):
        for tr in tbody.find_all("tr"):
            all_rows.append(tr)

    if not all_rows:
        # Try divs with assessment items
        for div in soup.find_all("div", class_=lambda c: c and "product-catalogue" in str(c).lower()):
            all_rows.append(div)

    for row in all_rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        link_tag = cells[0].find("a", href=True)
        if not link_tag:
            continue

        href = link_tag["href"]
        # Only keep actual assessment detail links
        if "/solutions/products/product-catalog/" not in href and "/products/product-catalog/" not in href:
            continue

        name = link_tag.get_text(strip=True)
        if not name:
            continue

        url = urljoin(BASE_URL, href)

        # Check remote support - look for filled circle images or specific classes
        remote_html = str(cells[1]) if len(cells) > 1 else ""
        adaptive_html = str(cells[2]) if len(cells) > 2 else ""

        # SHL uses specific CSS classes for Yes/No indicators
        remote_support = "Yes" if ('catalogue-header__new-' in remote_html and '-no' not in remote_html) else "No"
        adaptive_support = "Yes" if ('catalogue-header__new-' in adaptive_html and '-no' not in adaptive_html) else "No"

        # More reliable: check for any img or specific span
        if cells[1:]:
            imgs_remote = cells[1].find_all("img")
            if imgs_remote:
                remote_support = "Yes"

        # Collect test type letters from remaining cells
        test_type_letters = []
        for cell in cells[3:]:
            for span in cell.find_all("span"):
                cls = " ".join(span.get("class") or [])
                txt = span.get_text(strip=True).upper()
                if txt in TEST_TYPE_MAP:
                    test_type_letters.append(txt)
            # Extract from class names like "type-K" or "shl-type-A"
            for elem in cell.find_all(True):
                for cls in (elem.get("class") or []):
                    match = re.search(r'[-_]([A-Z])$', cls)
                    if match and match.group(1) in TEST_TYPE_MAP:
                        test_type_letters.append(match.group(1))

        test_types = list(set([TEST_TYPE_MAP[l] for l in test_type_letters]))

        assessments.append({
            "name": name,
            "url": url,
            "remote_support": remote_support,
            "adaptive_support": adaptive_support,
            "test_type": test_types,
            "description": "",
            "duration": None,
        })

    return assessments


def has_next_page(html: str) -> bool:
    """Check if there are more pages to scrape."""
    soup = BeautifulSoup(html, "lxml")
    # Look for next button / pagination
    next_links = soup.find_all("a", string=lambda t: t and "next" in t.lower())
    if next_links:
        return True
    # Look for pagination with more pages
    pagination = soup.find(class_=lambda c: c and "pagination" in str(c).lower())
    if pagination:
        current_active = pagination.find(class_=lambda c: c and "active" in str(c).lower())
        if current_active and current_active.find_next_sibling():
            return True
    return False


def get_total_count(html: str) -> int:
    """Try to extract total assessment count from the page."""
    soup = BeautifulSoup(html, "lxml")
    # Look for "Showing X of Y results" text
    for text in soup.stripped_strings:
        match = re.search(r'(\d+)\s+(?:results?|assessments?|products?)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


def crawl_all_assessments(session: requests.Session, page_size: int = 12) -> list[dict]:
    """Crawl all pages of the SHL catalogue."""
    all_assessments = {}
    start = 0
    page_num = 1
    max_empty_pages = 3
    empty_count = 0

    print("=" * 60)
    print("Starting SHL Catalogue Crawl")
    print("=" * 60)

    first_html = fetch_catalogue_page(session, 0)
    total = get_total_count(first_html)
    if total:
        print(f"Total assessments reported: {total}")

    while True:
        print(f"\nScraping page {page_num} (start={start})...")
        try:
            html = fetch_catalogue_page(session, start)
        except Exception as e:
            print(f"  Error fetching page: {e}")
            break

        # Try both parsers
        page_assessments = parse_catalogue_page_v2(html)
        if not page_assessments:
            page_assessments = parse_catalogue_page(html)

        if not page_assessments:
            empty_count += 1
            print(f"  No assessments found on page {page_num}. Empty count: {empty_count}")
            if empty_count >= max_empty_pages:
                print("  Too many empty pages. Stopping.")
                break
        else:
            empty_count = 0
            new_count = 0
            for a in page_assessments:
                if a["url"] not in all_assessments:
                    all_assessments[a["url"]] = a
                    new_count += 1
            print(f"  Found {len(page_assessments)} assessments ({new_count} new). Total: {len(all_assessments)}")

            if new_count == 0:
                print("  No new assessments. Catalogue exhausted.")
                break

        start += page_size
        page_num += 1
        time.sleep(1.5)  # Be polite

    return list(all_assessments.values())


def save_raw(assessments: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(assessments)} assessments to {path}")


def main():
    session = get_session()
    assessments = crawl_all_assessments(session)

    print(f"\n{'='*60}")
    print(f"CRAWL COMPLETE: {len(assessments)} assessments found")
    if len(assessments) < 377:
        print(f"WARNING: Only {len(assessments)} found. Target is 377+")
    else:
        print(f"SUCCESS: Met 377+ target!")
    print(f"{'='*60}")

    save_raw(assessments, "data/raw/assessments_raw.json")


if __name__ == "__main__":
    main()