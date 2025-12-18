# MarketPulse - Laptop market analysis dashboard - from Avito.ma



![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**MarketPulse** is a comprehensive laptop market analysis tool that scrapes, cleans, and visualizes laptop listings from Avito.ma. It provides actionable insights into pricing trends, brand distribution, and value-for-money recommendations.

## Features

- **Web Scraping**: Automated Selenium-based scraper with resume capability
- **Data Cleaning**: Intelligent parsing of laptop specifications (CPU, RAM, Brand)
- **Interactive Dashboard**: Streamlit-powered visualization with filtering
- **Quality Scoring**: Custom algorithm to identify best value laptops
- **Market Insights**: Brand distribution, price trends, and configuration analysis

## Dashboard Preview

![Dashboard Screenshot] (screenshots/1.png)(screenshots/2.png)(screenshots/3.png)(screenshots/4.png)(screenshots/5.png)(screenshots/6.png)(screenshots/7.png)(screenshots/8.png)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/meddhajji/marketpulse.git
cd marketpulse
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard
```bash
streamlit run dashboard.py
```

### Scrape Fresh Data (Optional)
```bash
python scraper.py
```

### Clean Scraped Data
```bash
python cleaner.py
```

## Data Pipeline
```
Avito.ma → Scraper → marketpulse_raw db → Cleaner → marketpulse db → Dashboard
```

1. **Scraping**: `scraper.py` collects ~13,000+ laptop listings
2. **Cleaning**: `cleaner.py` extracts specifications and filters invalid data ~1900+ clean laptop listings
3. **Analysis**: `dashboard.py` visualizes insights and identifies best deals

## Quality Scoring System

Laptops are scored based on:

**CPU Scores:**
- i3: 30 | i5: 50 | i7: 70 | i9: 90
- M1: 60 | M2: 80 | M3: 100
- Ryzen 3/5/7/9: 35/55/75/95

**RAM Scores:**
- 4GB: 20 | 8GB: 40 | 16GB: 70 | 32GB: 100

**Value Ratio:** `(CPU Score + RAM Score) / Price × 1000`

## Key Insights

- Analyzed **2,288 clean laptop listings**
- Price range: 500 DH - 50,000+ DH
- Most common config: **i5 with 8GB RAM**
- Best value segment: **6,000-10,000 DH**

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

feel free to use this project for your portfolio or learning.

## Contact

For questions or collaboration: meddhajji@outlook.com

---

**Note**: This project is for educational purposes. Always respect website terms of service when scraping.