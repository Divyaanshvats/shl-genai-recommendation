from scraper.selenium_crawler import setup_driver, scrape_page
import json

def test():
    driver = setup_driver()
    try:
        print("Testing Page 1 extraction...")
        items = scrape_page(driver, 0)
        print(f"Items found: {len(items)}")
        if items:
            for i, item in enumerate(items[:3]):
                print(f"[{i}] {item['name']} - {item['url']}")
                print(f"    Types: {item['test_type']}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test()
