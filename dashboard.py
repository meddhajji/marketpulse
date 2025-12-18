# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="MarketPulse - Laptop Insights",
    page_icon="💻",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    conn = sqlite3.connect('marketpulse.db')
    df = pd.read_sql("SELECT * FROM laptops_clean_new", conn)
    conn.close()
    return df

# Calculate quality score
def calculate_quality_score(row):
    """
    Quality scoring system:
    CPU: i3=30, i5=50, i7=70, i9=90, M1=60, M2=80, M3=100, 
         Ryzen-3=35, Ryzen-5=55, Ryzen-7=75, Ryzen-9=95
         Ultra-5=55, Ultra-7=75, Ultra-9=95
    RAM: 4GB=20, 8GB=40, 16GB=70, 32GB=100, 64GB=120
    """
    cpu_scores = {
        'I3': 30, 'I5': 50, 'I7': 70, 'I9': 90,
        'M1': 60, 'M2': 80, 'M3': 100,
        'RYZEN-3': 35, 'RYZEN-5': 55, 'RYZEN-7': 75, 'RYZEN-9': 95,
        'ULTRA-5': 55, 'ULTRA-7': 75, 'ULTRA-9': 95
    }
    
    ram_scores = {
        4: 20, 8: 40, 16: 70, 32: 100, 64: 120
    }
    
    cpu_score = cpu_scores.get(row['cpu'], 25)  # Default 25 for unknown
    ram_score = ram_scores.get(row['ram'], row['ram'] * 5)  # Fallback formula
    
    total_score = cpu_score + ram_score
    
    # Value ratio: score per 1000 DH
    value_ratio = (total_score / row['price']) * 1000 if row['price'] > 0 else 0
    
    return total_score, value_ratio

# Main app
def main():
    st.markdown('<p class="main-header">MarketPulse - Laptop Market Analysis</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Calculate quality scores
    df[['quality_score', 'value_ratio']] = df.apply(
        lambda row: pd.Series(calculate_quality_score(row)), axis=1
    )
    
    # Sidebar filters
    st.sidebar.header("Filter Options")
    
    # Brand filter
    brands = ['All'] + sorted(df['brand'].unique().tolist())
    selected_brand = st.sidebar.selectbox("Select Brand", brands)
    
    # Price range
    min_price, max_price = int(df['price'].min()), int(df['price'].max())
    price_range = st.sidebar.slider(
        "Price Range (DH)",
        min_price, max_price,
        (min_price, max_price)
    )
    
    # RAM filter
    ram_options = sorted(df['ram'].unique().tolist())
    min_ram = st.sidebar.selectbox("Minimum RAM (GB)", ram_options, index=0)
    
    # CPU filter
    cpu_options = ['All'] + sorted(df['cpu'].unique().tolist())
    selected_cpu = st.sidebar.selectbox("CPU Type", cpu_options)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_brand != 'All':
        filtered_df = filtered_df[filtered_df['brand'] == selected_brand]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_range[0]) & 
        (filtered_df['price'] <= price_range[1]) &
        (filtered_df['ram'] >= min_ram)
    ]
    
    if selected_cpu != 'All':
        filtered_df = filtered_df[filtered_df['cpu'] == selected_cpu]
    
    # Overview metrics
    st.header("Market Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Laptops", f"{len(filtered_df):,}")
    with col2:
        st.metric("Average Price", f"{filtered_df['price'].mean():,.0f} DH")
    with col3:
        st.metric("Brands Available", len(filtered_df['brand'].unique()))
    with col4:
        st.metric("Price Range", f"{filtered_df['price'].min():.0f} - {filtered_df['price'].max():.0f} DH")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Brand Distribution")
        brand_counts = filtered_df['brand'].value_counts()
        fig_brand = px.pie(
            values=brand_counts.values,
            names=brand_counts.index,
            title="Market Share by Brand",
            hole=0.4
        )
        fig_brand.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_brand, use_container_width=True)
    
    with col2:
        st.subheader("CPU Distribution")
        cpu_counts = filtered_df['cpu'].value_counts().head(10)
        fig_cpu = px.bar(
            x=cpu_counts.index,
            y=cpu_counts.values,
            labels={'x': 'CPU Type', 'y': 'Count'},
            title="Top 10 CPU Types",
            color=cpu_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_cpu, use_container_width=True)
    
    # RAM distribution
    st.subheader("RAM Distribution")
    ram_counts = filtered_df['ram'].value_counts().sort_index()
    fig_ram = px.bar(
        x=ram_counts.index,
        y=ram_counts.values,
        labels={'x': 'RAM (GB)', 'y': 'Number of Laptops'},
        title="Laptops by RAM Capacity",
        text=ram_counts.values,
        color=ram_counts.values,
        color_continuous_scale='Viridis'
    )
    fig_ram.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_ram, use_container_width=True)
    
    # Price distribution
    st.subheader("Price Distribution")
    fig_price = px.histogram(
        filtered_df,
        x='price',
        nbins=50,
        title="Price Distribution",
        labels={'price': 'Price (DH)', 'count': 'Number of Laptops'},
        color_discrete_sequence=['#636EFA']
    )
    fig_price.add_vline(
        x=filtered_df['price'].median(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Median: {filtered_df['price'].median():.0f} DH"
    )
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Price vs Quality scatter
    st.subheader("Price vs Quality Score")
    fig_scatter = px.scatter(
        filtered_df,
        x='price',
        y='quality_score',
        color='brand',
        size='ram',
        hover_data=['title', 'cpu', 'ram'],
        title="Quality Score vs Price (bubble size = RAM)",
        labels={'price': 'Price (DH)', 'quality_score': 'Quality Score'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Best value laptops
    st.header("Top 20 Best Value Laptops")
    st.markdown("*Based on Quality/Price Ratio - Higher is better*")
    
    top_value = filtered_df.nlargest(20, 'value_ratio')[
        ['title', 'brand', 'cpu', 'ram', 'price', 'quality_score', 'value_ratio', 'link']
    ].reset_index(drop=True)
    
    # Display as interactive table
    st.dataframe(
        top_value.style.format({
            'price': '{:.0f} DH',
            'quality_score': '{:.0f}',
            'value_ratio': '{:.2f}'
        }).background_gradient(subset=['value_ratio'], cmap='Greens'),
        use_container_width=True,
        height=400
    )
    
    # Additional insights
    st.header("Market Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Most popular brand")
        top_brand = filtered_df['brand'].mode()[0]
        brand_pct = (filtered_df['brand'] == top_brand).sum() / len(filtered_df) * 100
        st.info(f"**{top_brand}** dominates with **{brand_pct:.1f}%** market share")
    
    with col2:
        st.subheader("Sweet spot price")
        median_price = filtered_df['price'].median()
        st.info(f"**{median_price:.0f} DH** - Most laptops cluster around this price")
    
    with col3:
        st.subheader("Most common config")
        common_ram = filtered_df['ram'].mode()[0]
        common_cpu = filtered_df['cpu'].mode()[0]
        st.info(f"**{common_cpu}** with **{common_ram}GB RAM** is most common")
    
    # Price by brand boxplot
    st.subheader("Price range by rrand")
    top_brands = filtered_df['brand'].value_counts().head(8).index
    df_top_brands = filtered_df[filtered_df['brand'].isin(top_brands)]
    
    fig_box = px.box(
        df_top_brands,
        x='brand',
        y='price',
        title="Price Distribution by Top Brands",
        labels={'price': 'Price (DH)', 'brand': 'Brand'},
        color='brand'
    )
    st.plotly_chart(fig_box, use_container_width=True)
    
    # Average price by RAM
    st.subheader("Average price by RAM capacity")
    avg_price_ram = filtered_df.groupby('ram')['price'].mean().sort_index()
    fig_ram_price = px.line(
        x=avg_price_ram.index,
        y=avg_price_ram.values,
        markers=True,
        title="How RAM affects price",
        labels={'x': 'RAM (GB)', 'y': 'Average price (DH)'},
        line_shape='spline'
    )
    st.plotly_chart(fig_ram_price, use_container_width=True)
    
    # Export data
    st.header("Export data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"marketpulse_laptops_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: gray;'>"
        f"Data from Avito.ma | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d')} | "
        f"Total items analyzed: {len(df):,}"
        f"</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
