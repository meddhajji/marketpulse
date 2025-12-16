from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
import datetime
import sqlite3

def scrape_avito():
    print("Starting MarketPulse Scraper...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # CRITICAL: No screen on cloud
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # ... inside scrape_avito() ...
    print("Starting MarketPulse Scraper...")
    # ... rest of code remains the same ...
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://www.avito.ma/fr/maroc/ordinateurs_portables"
    driver.get(url)
    time.sleep(5) 

    products = []
    items = driver.find_elements(By.CSS_SELECTOR, "a.sc-1jge648-0.jZXrfL")
    print(f"Found {len(items)} items. Processing...")

    for item in items:
        try:
            # 1. Link
            link = item.get_attribute("href")
            
            # 2. Title (Using specific class we found earlier)
            # Sometimes there are multiple <p> tags, we want the one with product name style
            # If this fails, we fall back to text parsing
            try:
                # The class you found earlier for title
                title = item.find_element(By.CSS_SELECTOR, "p.sc-1x0vz2r-0.iHApav").text
            except:
                # Fallback: Find the longest line in the text block (titles are usually long)
                lines = item.text.split('\n')
                title = max(lines, key=len) 

            # 3. Price (Text Parsing - Robust method)
            all_text = item.text
            lines = all_text.split('\n')
            price = 0.0
            
            for line in lines:
                if "DH" in line:
                    # Clean: "10 900 DH" -> 10900.0
                    clean = line.replace("DH", "").replace(" ", "").replace("\u202f", "").replace(",", ".")
                    try:
                        val = float(clean)
                        # Filter out weird small numbers (sometimes "1 DH" is used for 'call me')
                        if val > 100: 
                            price = val
                            break
                    except:
                        continue
            
            if price > 0:
                products.append({
                    "date": datetime.date.today(),
                    "title": title,
                    "price": price,
                    "link": link,
                    "source": "Avito"
                })
                # print(f"Got: {title} - {price}")

        except Exception as e:
            continue

    driver.quit()
    
    # Save
    if products:
        df = pd.DataFrame(products)
        conn = sqlite3.connect('marketpulse.db')
        # if_exists='append' adds new rows. 'replace' overwrites.
        # For now, let's use 'replace' to keep the DB clean while testing.
        df.to_sql('laptops', conn, if_exists='replace', index=False)
        conn.close()
        print(f"✅ Successfully database updated with {len(products)} laptops.")
    else:
        print("❌ No items scraped.")

if __name__ == "__main__":
    scrape_avito()