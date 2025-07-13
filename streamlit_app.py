import streamlit as st
import pandas as pd
import math
from pathlib import Path

# ----------------------------------------------------------------------
# Set page configuration
st.set_page_config(
    page_title='GDP Dashboard',
    page_icon='🌍',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ----------------------------------------------------------------------
# Add custom CSS styles
st.markdown(
    """
    <style>
    /* Center the header and add some shadow */
    .header {
        text-align: center;
        color: #1f77b4;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 1px 1px 2px #ccc;
    }

    /* Style the subtitle */
    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 1rem;
    }

    /* Style sidebar header */
    .sidebar .sidebar-content {
        background-color: #f5f8fa;
    }

    /* Metric card hover effect */
    div[data-testid="metric-container"] {
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
        border-radius: 10px;
    }

    /* Style for data table header */
    .stDataFrame th {
        background-color: #1f77b4 !important;
        color: white !important;
        text-align: center;
    }

    /* Footer style */
    footer {
        text-align: center;
        font-size: small;
        color: gray;
        margin-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------------------------
# Header with an image
st.markdown(
    """
    <div class="header">
        <h1>🌍 Global GDP Dashboard</h1>
    </div>
    <div class="subtitle">
        Browse historical GDP data from the 
        <a href='https://data.worldbank.org/' target='_blank'>World Bank Open Data</a>.
    </div>
    <hr>
    """,
    unsafe_allow_html=True,
)

# Add a world map image below header
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/World_map_blank_without_borders.svg/1200px-World_map_blank_without_borders.svg.png",
    caption="World Map",
    use_column_width=True,
)

# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Sidebar filters with country flags (using emojis)
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

    # Map country codes to emojis for flags (limited sample)
    country_flags = {
        "DEU": "🇩🇪 Germany",
        "FRA": "🇫🇷 France",
        "GBR": "🇬🇧 UK",
        "BRA": "🇧🇷 Brazil",
        "MEX": "🇲🇽 Mexico",
        "JPN": "🇯🇵 Japan"
    }

    countries = gdp_df['Country Code'].unique()
    display_countries = [country_flags.get(c, c) for c in countries]

    selected_countries_flags = st.multiselect(
        'Select countries',
        options=display_countries,
        default=[country_flags[c] for c in ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'] if c in country_flags]
    )

    # Map back from selected flags to country codes
    selected_countries = [
        code for code, flag in country_flags.items() if flag in selected_countries_flags
    ]

# ----------------------------------------------------------------------
# Filter data based on user selection
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) &
    (gdp_df['Year'] >= from_year) &
    (gdp_df['Year'] <= to_year)
]

# ----------------------------------------------------------------------
# GDP Trends Chart
st.subheader('📈 GDP Trends Over Time')
st.caption('This chart shows the GDP evolution over the selected years for each country.')

if selected_countries:
    # Prepare data for line_chart (pivoted so each country is a column)
    chart_data = filtered_gdp_df.pivot(index='Year', columns='Country Code', values='GDP')

    st.line_chart(chart_data, use_container_width=True)
else:
    st.info("Please select at least one country from the sidebar.")

# ----------------------------------------------------------------------
# GDP Summary Metrics with flags & hover effect
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

            flag = country_flags.get(country, country)

            st.metric(
                label=f"{flag} GDP",
                value=f"{last_gdp:,.0f}B USD",
                delta=growth,
                delta_color=delta_color
            )
        except:
            st.metric(label=f"{country} GDP", value="Data unavailable")

# ----------------------------------------------------------------------
# Optional: Show raw data table with styled dataframe
with st.expander("📄 View Raw Data Table"):
    st.dataframe(filtered_gdp_df.style.format({"GDP": "{:,.0f}"}), use_container_width=True)

# ----------------------------------------------------------------------
# Footer with small heart icon and link styling
st.markdown(
    """
    <hr>
    <footer>
        Built with ❤️ using <a href='https://streamlit.io/' target='_blank'>Streamlit</a> |
        Data Source: <a href='https://data.worldbank.org/' target='_blank'>World Bank</a>
    </footer>
    """,
    unsafe_allow_html=True
)
