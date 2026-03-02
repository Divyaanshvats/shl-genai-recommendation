"""
SHL Product Catalogue Full Scraper (Selenium-based)
Correctly handles JS-rendered content on SHL website
Scrapes 377+ individual test assessments

URL: https://www.shl.com/solutions/products/product-catalog/
Pagination: ?start=0, ?start=12, ?start=24 ... (12 per page)
There are 2 sections: Pre-packaged Job Solutions & Individual Test Solutions
"""

import time
import json
import os
import re
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

BASE_URL = "https://www.shl.com"
CATALOGUE_URL = "https://www.shl.com/solutions/products/product-catalog/"
PAGE_SIZE = 12

# SHL test type tooltip/key class -> full name
# Based on DOM inspection: spans with class "product-catalogue__key"
# The tooltip content has the type name
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


def setup_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_test_types_from_cell(cell, driver) -> list[str]:
    """Extract test type codes from a table cell using JS."""
    try:
        result = driver.execute_script("""
            var cell = arguments[0];
            var spans = cell.querySelectorAll('span[class*="product-catalogue__key"]');
            var types = [];
            spans.forEach(function(span) {
                // Try data-tooltip attribute
                var tooltip = span.getAttribute('data-tooltip-id') || 
                              span.getAttribute('data-type') ||
                              span.getAttribute('aria-label') || '';
                // Try text content
                var text = span.textContent.trim().toUpperCase();
                if (text.length === 1) types.push(text);
                // Try class for type indicator
                var cls = span.className;
                var match = cls.match(/--([A-Z])/);
                if (match) types.push(match[1]);
            });
            return types;
        """, cell)
        return list(set(result or []))
    except Exception:
        return []


def extract_support_indicators(cell, driver) -> str:
    """Check if a support indicator cell (remote/adaptive) shows Yes."""
    try:
        result = driver.execute_script("""
            var cell = arguments[0];
            // Check for any filled/visible indicator
            var spans = cell.querySelectorAll('span, img, svg, i');
            for (var i = 0; i < spans.length; i++) {
                var el = spans[i];
                var cls = el.className || '';
                // SHL uses specific classes for yes/no
                if (cls.indexOf('-no') === -1 && el.offsetWidth > 0) {
                    return 'Yes';
                }
            }
            // Check if cell has any meaningful content
            var text = cell.textContent.trim();
            if (text === '●' || text === '✓' || text === 'Yes') return 'Yes';
            return 'No';
        """, cell)
        return result or "No"
    except Exception:
        return "No"


def scrape_page(driver, start: int) -> list[dict]:
    """Scrape one page of the catalogue listing."""
    url = f"{CATALOGUE_URL}?start={start}"

    try:
        driver.get(url)
        # Wait for any table row to appear
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr td a"))
        )
        time.sleep(2)
    except Exception as e:
        print(f"    Timeout or error loading page (start={start}): {e}")
        return []

    # Use JavaScript to extract all assessment data from the page
    assessments = driver.execute_script("""
        var rows = document.querySelectorAll('tbody tr');
        var results = [];

        rows.forEach(function(row) {
            var cells = row.querySelectorAll('td');
            if (cells.length < 4) return;

            var linkEl = cells[0].querySelector('a');
            if (!linkEl) return;

            var href = linkEl.getAttribute('href') || '';
            var name = linkEl.textContent.trim();
            if (!name || !href) return;

            // Full URL
            var url = href.startsWith('http') ? href : 'https://www.shl.com' + href;

            // Remote Testing (cell 1) - check for visible non-no indicators
            var remoteCell = cells[1];
            var remoteSpans = remoteCell.querySelectorAll('span, img');
            var remoteSupport = 'No';
            remoteSpans.forEach(function(el) {
                var cls = el.className || '';
                if (cls.indexOf('-no') === -1 && cls.length > 0) {
                    remoteSupport = 'Yes';
                }
            });

            // Adaptive/IRT (cell 2)
            var adaptiveCell = cells[2];
            var adaptiveSpans = adaptiveCell.querySelectorAll('span, img');
            var adaptiveSupport = 'No';
            adaptiveSpans.forEach(function(el) {
                var cls = el.className || '';
                if (cls.indexOf('-no') === -1 && cls.length > 0) {
                    adaptiveSupport = 'Yes';
                }
            });

            // Test types from remaining cells (cell 3+)
            var testTypes = [];
            for (var i = 3; i < cells.length; i++) {
                var typeSpans = cells[i].querySelectorAll('span[class*="product-catalogue"],span[class*="filter"]');
                typeSpans.forEach(function(span) {
                    var txt = span.textContent.trim().toUpperCase();
                    if (txt.length === 1 && /[A-Z]/.test(txt)) {
                        testTypes.push(txt);
                    }
                    var cls = span.className || '';
                    var match = cls.match(/--([A-Z])(?:\s|$)/);
                    if (match) testTypes.push(match[1]);
                });
            }

            // Deduplicate test types
            var uniqueTypes = [...new Set(testTypes)];

            results.push({
                name: name,
                url: url,
                remote_support: remoteSupport,
                adaptive_support: adaptiveSupport,
                test_type_codes: uniqueTypes,
                description: '',
                duration: null,
            });
        });

        return results;
    """)

    if not assessments:
        return []

    # Map test type codes to full names
    type_full_map = {
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

    for a in assessments:
        codes = a.pop("test_type_codes", [])
        a["test_type"] = list(set([type_full_map.get(c, c) for c in codes if c in type_full_map]))

    return assessments


def scrape_detail_page(driver, url: str) -> dict:
    """Scrape an individual assessment detail page for description and duration."""
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        time.sleep(1)

        result = driver.execute_script("""
            // Get description
            var desc = '';
            var descSelectors = [
                '.product-hero__description',
                '.product-hero p',
                '[class*="description"] p',
                'main p',
                '.product p'
            ];
            for (var i = 0; i < descSelectors.length; i++) {
                var el = document.querySelector(descSelectors[i]);
                if (el && el.textContent.trim().length > 30) {
                    desc = el.textContent.trim().substring(0, 500);
                    break;
                }
            }

            // Fallback: meta description
            if (!desc) {
                var meta = document.querySelector('meta[name="description"]');
                if (meta) desc = meta.getAttribute('content') || '';
            }

            // Get duration
            var duration = null;
            var fullText = document.body.textContent;
            var durationMatch = fullText.match(/(\\d+)\\s*(?:to|-|–)\\s*(\\d+)\\s*min/i);
            if (durationMatch) {
                duration = Math.round((parseInt(durationMatch[1]) + parseInt(durationMatch[2])) / 2);
            } else {
                var singleMatch = fullText.match(/(\\d+)\\s*min(?:utes?)?/i);
                if (singleMatch) {
                    var d = parseInt(singleMatch[1]);
                    if (d >= 1 && d <= 180) duration = d;
                }
            }

            // Remote + Adaptive support from detail page
            var remoteEl = document.querySelector('[class*="remote"]');
            var adaptiveEl = document.querySelector('[class*="adaptive"]');

            return {
                description: desc,
                duration: duration,
            };
        """)

        return result or {"description": "", "duration": None}

    except Exception:
        return {"description": "", "duration": None}


def run_selenium_scraper() -> list[dict]:
    """Main scraper function using Selenium."""
    print("="*60)
    print("SHL Assessment Catalogue Scraper (Selenium)")
    print("="*60)

    driver = setup_driver()
    all_assessments = {}

    try:
        start = 0
        page = 1
        max_empty = 3
        empty_streak = 0

        print("\nPhase 1: Scraping catalogue listing pages...")

        while empty_streak < max_empty:
            print(f"\n  Page {page} (start={start})...")
            page_items = scrape_page(driver, start)

            if not page_items:
                empty_streak += 1
                print(f"  Empty page. Streak: {empty_streak}/{max_empty}")
            else:
                empty_streak = 0
                new_count = 0
                for item in page_items:
                    if item["url"] not in all_assessments:
                        all_assessments[item["url"]] = item
                        new_count += 1
                print(f"  Found {len(page_items)} items ({new_count} new). Total: {len(all_assessments)}")

                if new_count == 0:
                    print("  No new items found, catalogue likely exhausted.")
                    break

            start += PAGE_SIZE
            page += 1
            time.sleep(1.2)

            # Safety cap at 50 pages
            if page > 50:
                print("Reached page 50 limit.")
                break

        assessments_list = list(all_assessments.values())
        print(f"\nListings scraped: {len(assessments_list)}")

        # Phase 2: Enrich with detail pages
        print("\nPhase 2: Enriching with detail page data...")
        os.makedirs("data/raw", exist_ok=True)
        out_path = "data/raw/assessments.json"
        
        # Initial save of all listings before enrichment
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(assessments_list, f, indent=2, ensure_ascii=False)
        print(f"  Saved {len(assessments_list)} listings to {out_path} (before enrichment)")

        for i, assessment in enumerate(tqdm(assessments_list, desc="Detail pages")):
            # Skip if already enriched (in case of restart)
            if assessment.get("description") and len(assessment["description"]) > 50 and assessment.get("duration"):
                continue
                
            detail = scrape_detail_page(driver, assessment["url"])
            if detail.get("description"):
                assessment["description"] = detail.get("description")
            if detail.get("duration"):
                assessment["duration"] = detail.get("duration")

            # Apply defaults
            if not assessment.get("description"):
                assessment["description"] = f"SHL assessment: {assessment['name']}"
            if not assessment.get("duration"):
                assessment["duration"] = 30

            # Save incrementally every 10 items
            if i % 10 == 0:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(assessments_list, f, indent=2, ensure_ascii=False)

            if i % 20 == 0:
                time.sleep(0.5)

    finally:
        driver.quit()

    return list(all_assessments.values())


def main():
    assessments = run_selenium_scraper()

    print(f"\n{'='*60}")
    print(f"TOTAL: {len(assessments)} assessments")
    if len(assessments) >= 377:
        print("✓ 377+ TARGET MET!")
    else:
        print(f"✗ Only {len(assessments)} found. Need 377+")
    print("="*60)

    os.makedirs("data/raw", exist_ok=True)
    out_path = "data/raw/assessments.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to: {out_path}")

    if assessments:
        print("\nSample:")
        for k, v in assessments[0].items():
            print(f"  {k}: {v!r}")


if __name__ == "__main__":
    main()