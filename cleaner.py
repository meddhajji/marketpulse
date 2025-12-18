import sqlite3
import pandas as pd
import re

def parse_specs(title):
    title_lower = title.lower()
    
    # 1. Brand Detection
    brand_match = re.search(
        r'(samsung|apple|huawei|xiaomi|oneplus|oppo|vivo|realme|asus|lenovo|dell|hp|acer|msi|lg|sony|nokia|motorola|google|macbook)',
        title_lower
    )
    if brand_match:
        found_brand = "Apple" if brand_match.group(0) == "macbook" else brand_match.group(0).capitalize()
    else:
        found_brand = "Other"
    
    # 2. CPU Detection
    cpu_match = re.search(r'(i[3579]|m[123]|ryzen\s?\d|ultra\s?\d)', title_lower)
    cpu = cpu_match.group(0).upper().replace(" ", "-") if cpu_match else "Unknown"
    
    # 3. RAM Detection (IMPROVED LOGIC)
    # Find all memory sizes mentioned (in GB or GO)
    memory_matches = re.findall(r'(\d+)\s?(go|gb)', title_lower)
    
    ram = 0
    
    if memory_matches:
        # Extract all numbers
        memory_values = [int(match[0]) for match in memory_matches]
        
        if len(memory_values) == 1:
            # Only one value found
            value = memory_values[0]
            # If <= 32, it's likely RAM. If > 32, it's likely storage (ignore)
            if value <= 32:
                ram = value
            else:
                ram = 0  # Storage mentioned, no RAM found
        
        elif len(memory_values) == 2:
            # Two values found (likely RAM/Storage combo like "8go/256go")
            # Take the SMALLER value as RAM
            ram = min(memory_values)
        
        else:
            # More than 2 values (rare case)
            # Take the smallest value that's <= 32 as RAM
            valid_ram_values = [v for v in memory_values if v <= 32]
            ram = min(valid_ram_values) if valid_ram_values else 0
    
    return found_brand, cpu, ram

def run():
    print("Starting Final Clean...")
    
    # Connect to RAW DB
    conn_raw = sqlite3.connect('marketpulse_raw.db')
    try:
        df = pd.read_sql("SELECT * FROM new_listings", conn_raw)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    finally:
        conn_raw.close()
    
    print(f"Loaded {len(df)} raw items.")
    
    # Apply Cleaning (Vectorized approach)
    specs = df['title'].apply(lambda x: pd.Series(parse_specs(x)))
    specs.columns = ['brand', 'cpu', 'ram']
    
    # Combine with original data
    df_clean = pd.concat([df, specs], axis=1)
    
    # Filter bad data (Price > 500 AND RAM > 0)
    df_final = df_clean[
        (df_clean['price'] > 500) & 
        (df_clean['ram'] > 0)
    ]
    
    # Save to PRODUCTION DB
    conn_prod = sqlite3.connect('marketpulse.db')
    df_final.to_sql('laptops_clean_new', conn_prod, if_exists='replace', index=False)
    conn_prod.close()
    
    print(f"\n{'='*60}")
    print(f"Cleaning Complete!")
    print(f"{'='*60}")
    print(f"Total raw items: {len(df)}")
    print(f"Clean items saved: {len(df_final)}")
    print(f"Filtered out: {len(df) - len(df_final)}")
    print(f"{'='*60}\n")
    
    # Show sample results
    print("Sample of cleaned data:")
    print(df_final[['title', 'brand', 'cpu', 'ram', 'price']].head(10).to_string())
    
    # Show RAM distribution
    print(f"\n{'='*60}")
    print("RAM Distribution:")
    print(df_final['ram'].value_counts().sort_index().to_string())
    print(f"{'='*60}")

if __name__ == "__main__":
    run()