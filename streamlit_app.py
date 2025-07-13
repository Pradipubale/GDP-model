import streamlit as st
import pandas as pd
import math
import pycountry
from pathlib import Path

# -------------------------------------------------------------------
# Page Configuration
st.set_page_config(
    page_title="🌍 Global GDP Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Background Styling with Overlay
st.markdown("""
    <style>
        body {
            background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/World_map_blank_without_borders.svg/1920px-World_map_blank_without_borders.svg.png');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }
        .stApp {
            background-color: rgba(255, 255, 255, 0.9);
        }
        .header-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
        }
        .header-text h1 {
            color: #1f77b4;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .header-text p {
            font-size: 1.1rem;
            color: #555;
        }
        .header-image img {
            max-width: 260px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        section[data-testid="stSidebar"] {
            background-color: #f0f4f8;
            padding: 1.5rem;
        }
        .metric-container div[data-testid="metric-container"] {
            background: white;
            padding: 1.2rem;
            border-radius: 10px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
            transition: 0.3s ease-in-out;
        }
        .metric-container div[data-testid="metric-container"]:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        }
        .footer {
            text-align: center;
            color: #999;
            font-size: 0.85rem;
            margin-top: 2rem;
            padding: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Load Data
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "data/gdp_data.csv"
    raw_df = pd.read_csv(data_path)
    df = raw_df.melt(
        id_vars=['Country Code'],
        value_vars=[str(y) for y in range(1960, 2023)],
        var_name='Year',
        value_name='GDP'
    )
    df['Year'] = pd.to_numeric(df['Year'])
    return df

gdp_df = load_data()

# -------------------------------------------------------------------
# Header Section
st.markdown("""
    <div class="header-section">
        <div class="header-text">
            <h1>🌍 Global GDP Dashboard</h1>
            <p>Explore decades of GDP data by country from the 
            <a href="https://data.worldbank.org/" target="_blank">World Bank</a>.</p>
        </div>
        <div class="header-image">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/World_map_blank_without_borders.svg/640px-World_map_blank_without_borders.svg.png">
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Country Helper with Flag
def get_country_name(code):
    try:
        return pycountry.countries.get(alpha_3=code).name
    except:
        return code

def get_flag_emoji(code):
    try:
        country = pycountry.countries.get(alpha_3=code)
        return f"https://flagcdn.com/w40/{country.alpha_2.lower()}.png"
    except:
        return None

# -------------------------------------------------------------------
# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filter Options")

    min_year, max_year = int(gdp_df['Year'].min()), int(gdp_df['Year'].max())
    year_range = st.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(2010, 2022))

    country_list = sorted(gdp_df['Country Code'].unique())
    default = ['USA', 'CHN', 'DEU', 'IND', 'JPN']

    country_names = {
        code: f"{get_country_name(code)} ({code})" for code in country_list
    }
    name_to_code = {v: k for k, v in country_names.items()}

    selection = st.multiselect(
        "Select Countries", 
        options=list(country_names.values()), 
        default=[country_names[c] for c in default]
    )

    selected_countries = [name_to_code[name] for name in selection]

# -------------------------------------------------------------------
# Filtered Data
filtered_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries)) &
    (gdp_df['Year'] >= year_range[0]) &
    (gdp_df['Year'] <= year_range[1])
]

# -------------------------------------------------------------------
# GDP Trends Chart
st.subheader("📈 GDP Trends Over Time")
if not selected_countries:
    st.info("Please select one or more countries to display the chart.")
else:
    chart_df = filtered_df.pivot(index="Year", columns="Country Code", values="GDP")
    st.line_chart(chart_df, use_container_width=True)

# -------------------------------------------------------------------
# GDP Summary Metrics
st.subheader(f"💰 GDP Summary in {year_range[1]}")
first_year_df = gdp_df[gdp_df["Year"] == year_range[0]]
last_year_df = gdp_df[gdp_df["Year"] == year_range[1]]

metric_cols = st.columns(4)

with st.container():
    for i, country in enumerate(selected_countries):
        col = metric_cols[i % 4]
        with col:
            try:
                first = first_year_df[first_year_df["Country Code"] == country]["GDP"].iat[0] / 1e9
                last = last_year_df[last_year_df["Country Code"] == country]["GDP"].iat[0] / 1e9

                if math.isnan(first) or first == 0:
                    growth = "n/a"
                    delta_color = "off"
                else:
                    growth = f"{last / first:.2f}x"
                    delta_color = "normal"

                flag_url = get_flag_emoji(country)
                name = get_country_name(country)

                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="flag-title">
                        <img src="{flag_url}">
                        <strong>{name}</strong>
                    </div>
                """, unsafe_allow_html=True)
                st.metric(label="", value=f"{last:,.0f}B USD", delta=growth, delta_color=delta_color)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception:
                st.metric(label=f"{country} GDP", value="Data not available")

# -------------------------------------------------------------------
# Show Raw Data Table
with st.expander("📄 View Raw Data Table"):
    st.dataframe(filtered_df, use_container_width=True)

# -------------------------------------------------------------------
# Footer
st.markdown("""
    <div class="footer">
        Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a> |
        Source: <a href="https://data.worldbank.org/" target="_blank">World Bank Open Data</a>
    </div>
""", unsafe_allow_html=True)
