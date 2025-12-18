# edit_item.py
import sqlite3

def edit_specific_item():
    conn = sqlite3.connect('marketpulse.db')
    cursor = conn.cursor()
    
    # First, let's find the item
    search_title = "%Ordinateur Portable 13 pouces HP Stream SSD 32Go%"
    cursor.execute("""
        SELECT title, brand, cpu, ram, price 
        FROM laptops_clean_new 
        WHERE title LIKE ?
    """, (search_title,))
    
    result = cursor.fetchone()
    
    if result:
        print("Found item:")
        print(f"Title: {result[0]}")
        print(f"Brand: {result[1]}")
        print(f"CPU: {result[2]}")
        print(f"RAM: {result[3]}")
        print(f"Price: {result[4]}")
        
        # Update the RAM to 0 (or remove it from clean data)
        confirm = input("\nSet RAM to 0 to exclude this item? (y/n): ")
        
        if confirm.lower() == 'y':
            cursor.execute("""
                UPDATE laptops_clean_new 
                SET ram = 0 
                WHERE title LIKE ?
            """, (search_title,))
            
            conn.commit()
            print("✓ Item updated - will be filtered out in next analysis")
        else:
            # Alternative: Set a reasonable RAM value
            ram_value = input("Enter RAM value to set (or press Enter to skip): ")
            if ram_value:
                cursor.execute("""
                    UPDATE laptops_clean_new 
                    SET ram = ? 
                    WHERE title LIKE ?
                """, (int(ram_value), search_title))
                conn.commit()
                print(f"✓ RAM set to {ram_value}GB")
    else:
        print("Item not found in database")
    
    conn.close()

if __name__ == "__main__":
    edit_specific_item()