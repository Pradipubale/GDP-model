import streamlit as st
import pandas as pd
import math
from pathlib import Path

# -----------------------------------------------------------------------------
# Set page configuration
st.set_page_config(
    page_title='GDP Dashboard',
    page_icon='🌍',
    layout='wide',
    initial_sidebar_state='expanded'
)

# -----------------------------------------------------------------------------
# Header section with styling
st.markdown("""
    <div style='text-align: center'>
        <h1 style='color:#1f77b4;'>🌍 Global GDP Dashboard</h1>
        <p>Browse historical GDP data from the 
        <a href='https://data.worldbank.org/' target='_blank'>World Bank Open Data</a>.</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Load GDP data
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
# Sidebar filters
with st.sidebar:
    st.header("🔎 Filters")

    min_year = gdp_df['Year'].min()
    max_year = gdp_df['Year'].max()

    from_year, to_year = st.slider(
        'Select year range',
        min_value=min_year,
        max_value=max_year,
        value=[min_year, max_year]
    )

    countries = gdp_df['Country Code'].unique()

    selected_countries = st.multiselect(
        'Select countries',
        countries,
        ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN']
    )

# -----------------------------------------------------------------------------
# Filter data based on user selection
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

# -----------------------------------------------------------------------------
# GDP Trends Chart
st.subheader('📈 GDP Trends Over Time')
st.caption('This chart shows the GDP evolution over the selected years for each country.')

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
# GDP Summary Metrics
st.subheader(f'💰 GDP Summary in {to_year}')
first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]
    with col:
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
                label=f"{country} GDP",
                value=f"{last_gdp:,.0f}B USD",
                delta=growth,
                delta_color=delta_color
            )
        except:
            st.metric(label=f"{country} GDP", value="Data unavailable")

# -----------------------------------------------------------------------------
# Optional: Show raw data table
with st.expander("📄 View Raw Data Table"):
    st.dataframe(filtered_gdp_df, use_container_width=True)

# -----------------------------------------------------------------------------
# Footer
st.markdown("""
    <hr>
    <div style='text-align: center; font-size: small;'>
        Built with ❤️ using <a href='https://streamlit.io/' target='_blank'>Streamlit</a> |
        Data Source: <a href='https://data.worldbank.org/' target='_blank'>World Bank</a>
    </div>
""", unsafe_allow_html=True)
