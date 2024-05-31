import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium



# Page configuration
st.set_page_config(page_title="Land Cover Change Predictions", page_icon="🔍", layout="centered")

# Load data
#df = pd.read_csv('raw_data/pivot_pa_2015_2024.csv')
df = pd.read_csv('raw_data/final_data_2015_2035.csv')

# Drop 'Unnamed: 0' column if it exists (as I haad this problem before)
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

if 'temperature_quarterly_mean' in df.columns:
    df = df.drop(columns=['temperature_quarterly_mean'])

if 'precipitation_quarterly_mean' in df.columns:
    df = df.drop(columns=['precipitation_quarterly_mean'])

if 'water-vapor-pressure_quarterly_mean' in df.columns:
    df = df.drop(columns=['water-vapor-pressure_quarterly_mean'])

if 'cloud-cover_quarterly_mean' in df.columns:
    df = df.drop(columns=['cloud-cover_quarterly_mean'])

# Integration of graph code
df['quarter_start'] = pd.to_datetime(df['quarter_start'])

col1, col2 = st.columns(2)

with st.container():
    st.markdown('<h2 style="font-size:24px;">Part I: Land Cover Proportion by Quarter</h2>', unsafe_allow_html=True)
    st.markdown("This section will display the change in land cover over time using images.")

    # for year in range(2015, 2025):
    #     st.markdown(f"### Year {year}")
    #     st.image(f'path/to/your/image_{year}.png', caption=f'Land Cover in {year}', use_column_width=True)

with st.container():
    st.markdown('<h2 style="font-size:24px;">Part II: Predictions of Change in Land Cover Proportions over time</h2>', unsafe_allow_html=True)
    st.markdown("This section will display the predicted change over the next 10 years.")

    # Define available quarters
    quarters = {'Q1': '01-01', 'Q2': '04-01', 'Q3': '07-01', 'Q4': '10-01'}

    # Create dropdown for SITECODEs
    sitecodes = df['SITECODE'].unique()
    selected_sitecode = st.selectbox(
        label='Sitecode:',
        options=sitecodes,
        index=0,
        help='Select a Sitecode',
    )

    # Create dropdown for quarters
    quarter_dropdown = st.selectbox(
        label='Quarter:',
        options=list(quarters.keys()),
        index=0,
        help='Select a Quarter',
    )

    # Define color dictionary for land cover categories
    color_dict = {
        'Trees': '#228B22',
        'Snow and Ice': '#B0E0E6',
        'Water': '#1E90FF',
        'Bare Ground': '#A9A9A9',
        'Crops': '#FFD700',
        'Grass': '#32CD32',
        'Shrub and Scrub': '#8B4513',
        'Built Area': '#FF0000',
        'Flooded Vegetation': '#00FF00'
    }
#Import protected areas shapefile
protected_areas = gpd.read_file("../raw_data/sample_protected_areas_624/protected_areas_624.shp")
protected_areas_sample = protected_areas.iloc[[0]]

# Create the Folium map
def create_folium_map(gdf):
    # Create a base map
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)
    # Add the shapefile to the map
    folium.GeoJson(protected_areas_sample).add_to(m)
    return m
folium_map = create_folium_map(protected_areas_sample)
# Display the Folium map in Streamlits
st_folium(folium_map, width=700, height=500)


# Upload CSV
df = pd.read_csv('raw_data/Final_df_model_lc_2015_2024.csv')

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: black;
        text-align: center;
        margin-bottom: 20px;
        line-height: 2.5; /* Adjust line height */
    } """)

    #st.write(df.head())
    #st.write(quarters.get(quarter_dropdown))

    # Define function to update plot
    # def update_df(sitecode, quarter):
    #     filtered_pa_data = df[df['SITECODE'] == sitecode]
    #     quarter_dates = filtered_pa_data[filtered_pa_data['date'].dt.strftime('%m-%d') == quarters.get(quarter_dropdown)]
    #     return quarter_dates

def update_df(sitecode, quarter):
    filtered_pa_data = df[df['SITECODE'] == sitecode]
    start_date = quarters[quarter]
    quarter_dates = filtered_pa_data[filtered_pa_data['quarter_start'].dt.strftime('%m-%d') == start_date]
    return quarter_dates

#st.write(update_df(selected_sitecode, quarter_dropdown))

quarter_dates = update_df(selected_sitecode, quarter_dropdown)

#st.write("Filtered Data:")
#st.write(quarter_dates)

# change negative values for lc proportions to 0
quarter_dates.iloc[:, 3:] = quarter_dates.iloc[:, 3:].clip(lower=0)

def update_plot(quarter_dates, sitecode, quarter):
    fig, ax = plt.subplots(figsize=(16, 8))

    # Set the Seaborn style
    sns.set(style="whitegrid")

    # Get colors for the categories from the color dictionary, falling back to default if not found
    colors = [color_dict.get(col, 'grey') for col in quarter_dates.columns if col not in ['quarter_start', 'SITECODE']]

    quarter_dates.set_index('quarter_start').plot(kind='area', stacked=True, color=colors, alpha=0.8, ax=ax)
    ax.set_title(f'Land Cover Proportions Over the Years for {sitecode} - Quarter {quarter}', fontsize=16)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Proportion', fontsize=12)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.legend(title='Land Cover Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, title_fontsize='12')
    ax.grid(False)

    ax.axvline(pd.to_datetime('2025-01-01'), color='r', linestyle='--')

    # Return the Matplotlib figure object
    return fig

fig = update_plot(quarter_dates, selected_sitecode, quarter_dropdown)

# Display the plot in Streamlit
st.pyplot(fig)

# with st.container():
#     st.markdown('<h2 style="font-size:24px;">Addition: Change Over Time for Ecological Data</h2>', unsafe_allow_html=True)

#     # Additional variables to plot
#     additional_variables = ['temperature_quaterly_mean', 'precipitation_quaterly_mean', 'water-vapor-pressure_quarterly_mean', 'cloud-cover_quarterly_mean']

#     # Loop over additional variables and create individual plots
#     for variable in additional_variables:
#         fig_variable, ax_variable = plt.subplots(figsize=(16, 8))
#         df.set_index('quarter_start')[variable].plot(ax=ax_variable)
#         ax_variable.set_title(f'{variable.replace("_", " ").title()} Over Time', fontsize=14)
#         ax_variable.set_xlabel('Year', fontsize=12)
#         ax_variable.set_ylabel('Value', fontsize=12)
#         ax_variable.tick_params(axis='x', labelsize=12)
#         ax_variable.tick_params(axis='y', labelsize=12)
#         st.pyplot(fig_variable)

# Add footer
st.markdown("""
    <div class="footer">
        Created with ❤️ by Amélie, Tim, Flori, and Ali
    </div>
    """, unsafe_allow_html=True)
