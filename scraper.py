from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import datetime
import sqlite3
import random

def init_db():
    """Create database with unique constraint on link"""
    conn = sqlite3.connect('marketpulse_raw.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_listings (
            scrape_date TEXT,
            title TEXT,
            price REAL,
            link TEXT UNIQUE,
            page INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_last_scraped_page():
    """Resume from last successful page"""
    try:
        conn = sqlite3.connect('marketpulse_raw.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(page) FROM new_listings")
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
    except:
        return 0

def save_batch_to_db(data):
    """Append new items without duplicates"""
    if not data: 
        return
    
    conn = sqlite3.connect('marketpulse_raw.db')
    df = pd.DataFrame(data)
    
    # Use 'append' instead of 'replace', ignore duplicates
    try:
        df.to_sql('new_listings', conn, if_exists='append', index=False)
        print(f"✓ Saved {len(data)} new items")
    except sqlite3.IntegrityError:
        # Handle duplicates by inserting one by one
        saved = 0
        for _, row in df.iterrows():
            try:
                row.to_frame().T.to_sql('new_listings', conn, if_exists='append', index=False)
                saved += 1
            except sqlite3.IntegrityError:
                continue  # Skip duplicate
        print(f"✓ Saved {saved}/{len(data)} items (skipped duplicates)")
    
    conn.close()

def scrape_mass_avito(start_page=1, end_page=500, batch_size=10):
    """
    Scrape Avito with resume capability and duplicate handling
    
    Args:
        start_page: Starting page (default: 1)
        end_page: Ending page (use 500 for ~15,000 items)
        batch_size: Save progress every N pages
    """
    print(f"Launching Scraper (Pages {start_page} to {end_page})...")
    
    # Initialize database
    init_db()
    
    # Check for resume
    last_page = get_last_scraped_page()
    if last_page > 0:
        resume = input(f"Found existing data up to page {last_page}. Resume from page {last_page + 1}? (y/n): ")
        if resume.lower() == 'y':
            start_page = last_page + 1
    
    # Setup Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Optional: Run headless for faster scraping
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    
    base_url = "https://www.avito.ma/fr/maroc/ordinateurs_portables"
    
    batch_products = []
    total_scraped = 0
    failed_pages = []

    try:
        for page in range(start_page, end_page + 1):
            try:
                print(f"Page {page}/{end_page} | Total: {total_scraped} items", end="\r")
                
                url = base_url if page == 1 else f"{base_url}?o={page}"
                driver.get(url)
                
                # Random human-like delay
                time.sleep(random.uniform(2.5, 5))
                
                # Check if page loaded correctly
                items = driver.find_elements(By.CSS_SELECTOR, "a.sc-1jge648-0.jZXrfL")
                
                if not items:
                    print(f"\nNo items found on page {page} - might be end of listings")
                    break
                
                page_count = 0
                for item in items:
                    try:
                        link = item.get_attribute("href")
                        
                        # Title extraction
                        try: 
                            title = item.find_element(By.CSS_SELECTOR, "p.sc-1x0vz2r-0.iHApav").text
                        except: 
                            title = item.text.split('\n')[0] if item.text else "Unknown"

                        # Price extraction
                        price = 0.0
                        for line in item.text.split('\n'):
                            if "DH" in line:
                                try:
                                    clean = line.replace("DH", "").replace(" ", "").replace("\u202f", "").replace(",", ".")
                                    price = float(clean)
                                    break
                                except: 
                                    continue
                        
                        if price > 0 and title != "Unknown":
                            batch_products.append({
                                "scrape_date": str(datetime.date.today()),
                                "title": title,
                                "price": price,
                                "link": link,
                                "page": page
                            })
                            page_count += 1
                            
                    except Exception as e:
                        continue
                
                total_scraped += page_count
                
                # Save batch progress
                if page % batch_size == 0:
                    print(f"\nCheckpoint at page {page}...")
                    save_batch_to_db(batch_products)
                    batch_products = []
                
                # Longer pause every 50 pages to avoid detection
                if page % 50 == 0:
                    pause = random.uniform(10, 20)
                    print(f"\nTaking a {pause:.1f}s break...")
                    time.sleep(pause)
                    
            except TimeoutException:
                print(f"\nTimeout on page {page}")
                failed_pages.append(page)
                continue
            except Exception as e:
                print(f"\nError on page {page}: {e}")
                failed_pages.append(page)
                continue

    except KeyboardInterrupt:
        print("\n\nScraping stopped by user")
    finally:
        # Save remaining items
        if batch_products:
            print(f"\nSaving final batch...")
            save_batch_to_db(batch_products)
        
        driver.quit()
        
        # Final report
        print(f"\n{'='*50}")
        print(f"Scraping Complete!")
        print(f"Total items scraped: {total_scraped}")
        if failed_pages:
            print(f"Failed pages: {failed_pages}")
        print(f"{'='*50}")
        
        # Show database stats
        conn = sqlite3.connect('marketpulse_raw.db')
        count = pd.read_sql("SELECT COUNT(*) as total FROM new_listings", conn)
        conn.close()
        print(f"Total in database: {count['total'][0]} items")

if __name__ == "__main__":
    # Scrape all ~15,000 items (approximately 430 pages)
    scrape_mass_avito(start_page=1, end_page=500, batch_size=10)