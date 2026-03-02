"""
SHL Assessment Detail Page Parser
Fetches individual assessment pages to enrich with description & duration
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.shl.com/solutions/products/product-catalog/",
}


def parse_duration(text: str) -> int | None:
    """Extract numeric duration in minutes from text like '40 minutes' or '25-35 mins'."""
    if not text:
        return None
    # Try to find a number, take first number found
    numbers = re.findall(r'\d+', text)
    if numbers:
        # If range like "25-35", take average
        if len(numbers) >= 2 and '-' in text:
            return (int(numbers[0]) + int(numbers[1])) // 2
        return int(numbers[0])
    return None


def fetch_assessment_detail(session: requests.Session, url: str) -> dict:
    """
    Fetch and parse an individual assessment detail page.
    Returns a dict with description and duration.
    """
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        details = {
            "description": "",
            "duration": None,
        }

        # --- Description ---
        # Usually in a paragraph under the main content section
        desc_candidates = [
            soup.find("div", class_=lambda c: c and "product__description" in c),
            soup.find("div", class_=lambda c: c and "description" in str(c).lower()),
            soup.find("section", class_=lambda c: c and "overview" in str(c).lower()),
        ]
        for cand in desc_candidates:
            if cand:
                desc_text = cand.get_text(separator=" ", strip=True)
                if len(desc_text) > 20:
                    details["description"] = desc_text[:500]
                    break

        if not details["description"]:
            # Try meta description
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                details["description"] = meta["content"][:500]

        if not details["description"]:
            # Try og:description
            og = soup.find("meta", attrs={"property": "og:description"})
            if og and og.get("content"):
                details["description"] = og["content"][:500]

        if not details["description"]:
            # Fallback: first meaningful paragraph
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 50:
                    details["description"] = text[:500]
                    break

        # --- Duration ---
        # Look for text patterns like "Approximate Completion Time: 40 mins"
        full_text = soup.get_text(separator=" ")
        duration_patterns = [
            r'(?:completion|assessment|test|timing|time)[^.]*?(\d[\d\-\s]*)\s*(?:min|minute)',
            r'(\d[\d\-\s]*)\s*(?:min|minute)',
            r'approximately\s+(\d+)',
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                duration = parse_duration(match.group(1))
                if duration and 1 <= duration <= 180:
                    details["duration"] = duration
                    break

        return details

    except Exception as e:
        return {"description": "", "duration": None}


def enrich_assessments(
    session: requests.Session,
    assessments: list[dict],
    delay: float = 0.8
) -> list[dict]:
    """Enrich all assessments with details from their individual pages."""
    print(f"\nEnriching {len(assessments)} assessments with detail pages...")

    for assessment in tqdm(assessments, desc="Fetching details"):
        url = assessment.get("url", "")
        if not url:
            continue

        # Only fetch if we don't already have description
        if assessment.get("description") and assessment.get("duration"):
            continue

        detail = fetch_assessment_detail(session, url)
        if detail["description"]:
            assessment["description"] = detail["description"]
        if detail["duration"]:
            assessment["duration"] = detail["duration"]

        time.sleep(delay)

    return assessments
