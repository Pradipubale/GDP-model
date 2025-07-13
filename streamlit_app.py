import streamlit as st
import pandas as pd
import math
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO

# -----------------------------------------------------------------------------
# Page config with wide layout
st.set_page_config(
    page_title='GDP Dashboard',
    page_icon='🌍',
    layout='wide',
    initial_sidebar_state='expanded'
)

# -----------------------------------------------------------------------------
# Banner image (replace URL with any image you want)
banner_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1350&q=80"
try:
    response = requests.get(banner_url)
    response.raise_for_status()
    banner_img = Image.open(BytesIO(response.content))
    st.image(banner_img, use_container_width=True)
except Exception:
    st.warning("Failed to load banner image.")

# -----------------------------------------------------------------------------
# Header text with style
st.markdown("""
    <div style='text-align: center; margin-top: -50px; margin-bottom: 30px;'>
        <h1 style='color:#1f77b4; font-family: Arial, sans-serif;'>🌍 Global GDP Dashboard</h1>
        <p style='font-size:18px;'>Explore historical GDP data from the 
        <a href='https://data.worldbank.org/' target='_blank'>World Bank Open Data</a>.</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Load GDP data function
@st.cache_data
def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent / 'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    gdp_df = raw_gdp_df.melt(
        id_vars=['Country Code'],
        value_vars=[str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        var_name='Year',
        value_name='GDP',
    )
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Sidebar filters with better titles and emojis
with st.sidebar:
    st.header("🔎 Filters")

    min_year = gdp_df['Year'].min()
    max_year = gdp_df['Year'].max()

    from_year, to_year = st.slider(
        'Select year range ⏳',
        min_value=min_year,
        max_value=max_year,
        value=[min_year, max_year]
    )

    countries = gdp_df['Country Code'].unique()

    selected_countries = st.multiselect(
        'Select countries 🌐',
        countries,
        ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN']
    )

# -----------------------------------------------------------------------------
# Filter data by user selection
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

# -----------------------------------------------------------------------------
# GDP Trends Section with emoji and styling
st.subheader('📈 GDP Trends Over Time')
st.caption('GDP evolution over the selected years for each country.')

if selected_countries:
    st.line_chart(
        filtered_gdp_df,
        x='Year',
        y='GDP',
        color='Country Code',
        use_container_width=True
    )
else:
    st.info("Please select at least one country from the sidebar.")

# -----------------------------------------------------------------------------
# Function to get country flag emoji by country code (ISO Alpha-3 to emoji)
def country_code_to_emoji(code):
    mapping = {
        'DEU': 'DE',
        'FRA': 'FR',
        'GBR': 'GB',
        'BRA': 'BR',
        'MEX': 'MX',
        'JPN': 'JP',
    }
    alpha2 = mapping.get(code, None)
    if not alpha2:
        return ''
    OFFSET = 127397
    return chr(ord(alpha2[0]) + OFFSET) + chr(ord(alpha2[1]) + OFFSET)

# -----------------------------------------------------------------------------
# GDP Summary Metrics with flags and nice layout
st.subheader(f'💰 GDP Summary in {to_year}')
first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]
    with col:
        flag = country_code_to_emoji(country)
        try:
            first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1e9
            last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1e9

            if math.isnan(first_gdp) or first_gdp == 0:
                growth = 'n/a'
                delta_color = 'off'
            else:
                growth = f'{last_gdp / first_gdp:.2f}x'
                delta_color = 'normal'

            st.metric(
                label=f"{flag} {country} GDP",
                value=f"{last_gdp:,.0f}B USD",
                delta=growth,
                delta_color=delta_color
            )
        except:
            st.metric(label=f"{flag} {country} GDP", value="Data unavailable")

# -----------------------------------------------------------------------------
# Two-column layout for raw data and side image
with st.container():
    col1, col2 = st.columns([3, 1])

    with col1:
        with st.expander("📄 View Raw Data Table"):
            st.dataframe(filtered_gdp_df, use_container_width=True)

    with col2:
        side_img_url = "https://images.unsplash.com/photo-1497493292307-31c376b6e479?auto=format&fit=crop&w=500&q=80"
        try:
            response = requests.get(side_img_url)
            response.raise_for_status()
            side_img = Image.open(BytesIO(response.content))
            st.image(side_img, caption="Global economy concept", use_container_width=True)
        except Exception as e:
            st.warning("Failed to load side image.")
            st.write(f"Error: {e}")

# -----------------------------------------------------------------------------
# Footer with style
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: small; color: gray;'>
        Built with ❤️ using <a href='https://streamlit.io/' target='_blank'>Streamlit</a> | 
        Data Source: <a href='https://data.worldbank.org/' target='_blank'>World Bank</a>
    </div>
""", unsafe_allow_html=True)
