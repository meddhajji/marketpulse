# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="MarketPulse Morocco", page_icon="📈", layout="wide")

# 2. Load Data function
def load_data():
    conn = sqlite3.connect('marketpulse.db')
    df = pd.read_sql("SELECT * FROM laptops", conn)
    conn.close()
    return df

# 3. The "Brain" (Feature Engineering)
def process_data(df):
    # Extract Brand from Title
    def get_brand(title):
        title = title.lower()
        if "hp" in title: return "HP"
        if "dell" in title: return "Dell"
        if "lenovo" in title: return "Lenovo"
        if "macbook" in title or "apple" in title: return "Apple"
        if "asus" in title: return "Asus"
        if "acer" in title: return "Acer"
        return "Other"
    
    df['Brand'] = df['title'].apply(get_brand)
    return df

# --- UI LAYOUT ---

st.title("🇲🇦 MarketPulse: Avito Laptop Tracker")
st.markdown("Real-time intelligence for electronics resellers.")

try:
    df_raw = load_data()
    df = process_data(df_raw)

    # Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Laptops Tracked", len(df))
    col2.metric("Avg Market Price", f"{int(df['price'].mean())} DH")
    col3.metric("Most Popular Brand", df['Brand'].mode()[0])

    st.divider()

    # Layout: Sidebar filters
    st.sidebar.header("Filters")
    selected_brand = st.sidebar.multiselect("Select Brand", options=df['Brand'].unique(), default=df['Brand'].unique())
    price_range = st.sidebar.slider("Max Price (DH)", 0, int(df['price'].max()), 10000)

    # Filter Logic
    filtered_df = df[
        (df['Brand'].isin(selected_brand)) &
        (df['price'] <= price_range)
    ]

    # Visualizations
    c1, c2 = st.columns((2, 1))
    
    with c1:
        st.subheader("Price vs. Brand")
        # Interactive Scatter Plot
        fig = px.scatter(filtered_df, x="price", y="Brand", hover_data=["title"], color="Brand")
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.subheader("Market Share")
        # Pie Chart
        brand_counts = filtered_df['Brand'].value_counts().reset_index()
        brand_counts.columns = ['Brand', 'Count']
        fig2 = px.pie(brand_counts, values='Count', names='Brand', hole=0.4)
        st.plotly_chart(fig2, width='stretch')

    # Data Table
    st.subheader("Latest Listings")
    st.dataframe(
        filtered_df[['title', 'price', 'Brand', 'link']],
        column_config={
            "link": st.column_config.LinkColumn("Listing URL")
        },
        hide_index=True
    )

except Exception as e:
    st.error(f"Database error. Run scraper.py first! Error: {e}")
    