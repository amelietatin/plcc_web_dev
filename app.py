
from io import StringIO ## for Python 3
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ee
import geemap.geemap as geemap
import geopandas as gpd
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd

import requests

# Page configuration
st.set_page_config(page_title="Land Cover Change Predictions", page_icon="🔍", layout="centered")

#############################################################################################################################################
#############################################################################################################################################
# DATA

# Load data
df = pd.read_csv('raw_data/final_data_2015_2035.csv')

# Timerange
date_range_df = pd.read_csv('raw_data/date_ranges.csv', sep=',')

#pa shapefile
pa_sample = gpd.read_file("raw_data/sample_protected_areas_624/protected_areas_624.shp")

# GEE SERVICE ACCOUNT
service_account = 'project-lc@lewagon-lc-amelietatin.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, './key.json')
ee.Initialize(credentials)

#Import protected areas GEE asset
shapefile = ee.FeatureCollection("projects/lewagon-lc-amelietatin/assets/sample_protected_areas_624")


#############################################################################################################################################
#############################################################################################################################################
# DROPDOWNS

#SITECODES
sitecodes = pa_sample['SITECODE'].unique()
selected_sitecode = st.selectbox(
    label='Sitecode:',
    options=sitecodes,
    index=0,
    help='Select a Sitecode',
)

#YEARS
years = date_range_df['Year'].unique()
selected_year = st.selectbox(
        label='Year:',
        options=list(years),
        index=0,
        help='Select a Year',
)

#QUARTERS
quarters = {'Q1': '01-01', 'Q2': '04-01', 'Q3': '07-01', 'Q4': '10-01'}
#quarters = date_range_df['Quartal'].unique()
#Create dropdown for quarters
quarter_dropdown = st.selectbox(
    label='Quarter:',
    options=list(quarters.keys()),
    index=0,
    help='Select a Quarter',
    )

st.write(quarter_dropdown)
#############################################################################################################################################
#############################################################################################################################################
# AMELIE
#############################################################################################################################################
#############################################################################################################################################

#Define which quartal
start = date_range_df[(date_range_df['Quartal'] == quarter_dropdown) & (date_range_df['Year'] == selected_year)]['Start_Date'].values[0]
end = date_range_df[(date_range_df['Quartal'] == quarter_dropdown) & (date_range_df['Year'] == selected_year)]['End_Date'].values[0]

with st.container():
    st.markdown('<h2 style="font-size:24px;">Part I: Land Cover Proportion by Quarter</h2>', unsafe_allow_html=True)
    st.markdown("This section will display the change in land cover over time using images.")

    # Convert start and end dates to ee.Date
    START = ee.Date(str(start))
    END = ee.Date(str(end))

    # Filter the shapefile for the specific protected area
    specific_feature_collection = shapefile.filter(ee.Filter.eq('SITECODE', selected_sitecode))
    geometry = specific_feature_collection.geometry()

    # Create a filter based on the geometry and date range
    col_filter = ee.Filter.And(
        ee.Filter.geometry(geometry),
        ee.Filter.date(START, END),
    )

    # Apply the filter to the DynamicWorld and Sentinel-2 collections
    dw_col = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filter(col_filter).filterBounds(geometry)
    dw_col_clipped = dw_col.map(lambda image: image.clip(geometry))
    s2_col = ee.ImageCollection('COPERNICUS/S2').filter(col_filter)

    # Join corresponding DW and S2 images
    dw_s2_col = ee.Join.saveFirst('s2_img').apply(
        dw_col_clipped,
        s2_col,
        ee.Filter.equals(leftField='system:index', rightField='system:index'),
    )

    # Extract an example DW image and its source S2 image
    dw_image = ee.Image(dw_s2_col.first())
    s2_image = ee.Image(dw_image.get('s2_img'))

    # Define land cover class names and their corresponding color palette
    CLASS_NAMES = [
        'water', 'trees', 'grass', 'flooded_vegetation', 'crops',
        'shrub_and_scrub', 'built', 'bare', 'snow_and_ice'
    ]
    VIS_PALETTE = [
        '419bdf', '397d49', '88b053', '7a87c6', 'e49635',
        'dfc35a', 'c4281b', 'a59b8f', 'b39fe1'
    ]

    # Create an RGB image of the label (most likely class) on [0, 1]
    dw_rgb = (
        dw_image.select('label')
        .visualize(min=0, max=8, palette=VIS_PALETTE)
        .divide(255)
    )

    # Get the most likely class probability
    top1_prob = dw_image.select(CLASS_NAMES).reduce(ee.Reducer.max())

    # Create a hillshade of the most likely class probability on [0, 1]
    top1_prob_hillshade = ee.Terrain.hillshade(top1_prob.multiply(100)).divide(255)

    # Combine the RGB image with the hillshade
    dw_rgb_hillshade = dw_rgb.multiply(top1_prob_hillshade)

    # Get lon and lat of protected area
    dict_pa = specific_feature_collection.getInfo()
    lon = dict_pa.get('features')[0].get('properties').get('lon')
    lat = dict_pa.get('features')[0].get('properties').get('lat')

    # Initialize map
    m = geemap.Map(center=(lat, lon), zoom=14)

    # Add protected area layer
    m.addLayer(geometry, {}, 'Protected Area')

    # Add Dynamic World layer
    m.addLayer(dw_rgb_hillshade, {'min': 0, 'max': 0.65}, 'Dynamic World Dataset')


    # Display map in Streamlit
    m.to_streamlit(height=600)


#############################################################################################################################################
#############################################################################################################################################
# FLORI
#############################################################################################################################################
#############################################################################################################################################


# url_base='https://landcoverapi-f37abimraq-ew.a.run.app/'
# response = requests.get(url=url_base+'/data').json()
# df = pd.DataFrame(response)

#Drop 'Unnamed: 0' column if it exists (as I haad this problem before)
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

df_lc = df.drop(columns=['temperature_quarterly_mean', 'precipitation_quarterly_mean', 'water-vapor-pressure_quarterly_mean', 'cloud-cover_quarterly_mean'])
df_eco = df[["SITECODE", "quarter_start", "temperature_quarterly_mean", "precipitation_quarterly_mean", "water-vapor-pressure_quarterly_mean", "cloud-cover_quarterly_mean"]].copy()

# Integration of graph code
df_lc['quarter_start'] = pd.to_datetime(df_lc['quarter_start'])
df_eco['quarter_start'] = pd.to_datetime(df_lc['quarter_start'])


with st.container():
    st.markdown('<h2 style="font-size:24px;">Part II: Predictions of Change in Land Cover Proportions over time</h2>', unsafe_allow_html=True)
    st.markdown("This section will display the predicted change over the next 10 years.")


    # Define color dictionary for land cover categories
    color_dict = {
        'Trees': '#397d49',
        'Snow and Ice': '#b39fe1',
        'Water': '#419bdf',
        'Bare Ground': '#a59b8f',
        'Crops': '#e49635',
        'Grass': '#88b053',
        'Shrub and Scrub': '#dfc35a',
        'Built Area': '#c4281b',
        'Flooded Vegetation': '#7a87c6'
    }


def update_df(sitecode, quarter):
    filtered_pa_data = df_lc[df_lc['SITECODE'] == sitecode]
    start_date = quarters[quarter]
    quarter_dates = filtered_pa_data[filtered_pa_data['quarter_start'].dt.strftime('%m-%d') == start_date]
    return quarter_dates

quarter_dates = update_df(selected_sitecode, quarter_dropdown)

# change negative values for lc proportions to 0
quarter_dates.iloc[:, 3:] = quarter_dates.iloc[:, 3:].clip(lower=0)

def update_plot(quarter_dates, sitecode, quarter):
    fig, ax = plt.subplots(figsize=(16, 8))

    # Set the Seaborn style
    sns.set(style="whitegrid")

    # Get colors for the categories from the color dictionary, falling back to default if not found
    colors = [color_dict.get(col, 'grey') for col in quarter_dates.columns if col not in ['quarter_start', 'SITECODE']]

    quarter_dates.set_index('quarter_start').plot(kind='area', stacked=True, color=colors, alpha=0.8, ax=ax)
    ax.set_title(f'Land Cover Proportions Over the Years for {sitecode} - {quarter}', fontsize=18)
    ax.set_xlabel('Year', fontsize=16)
    ax.set_ylabel('Proportion', fontsize=16)
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.legend(title='Land Cover Category', bbox_to_anchor=(0, -0.15), ncol = 2, loc='upper left', fontsize=16, title_fontsize='18')
    ax.grid(False)

    ax.axvline(pd.to_datetime('2025-01-01'), color='r', linestyle='--')

    # Return the Matplotlib figure object
    return fig

fig = update_plot(quarter_dates, selected_sitecode, quarter_dropdown)

# Display the plot in Streamlit
st.pyplot(fig)


# Additional graphs for temperature, precipitation, water-vapor-pressure, and cloud-cover:
with st.container():
    import plotly.graph_objects as go

    # Filter the data for the selected sitecode and quarter
    quarter_data = df_eco[df_eco['SITECODE'] == selected_sitecode]
    quarter_data = quarter_data[quarter_data['quarter_start'].dt.quarter == int(quarter_dropdown[1])]

    # Create the figure
    fig = go.Figure()

    # Add traces for each ecological variable
    fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['temperature_quarterly_mean'], mode='lines', name='Temperature', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['precipitation_quarterly_mean'], mode='lines', name='Precipitation', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['water-vapor-pressure_quarterly_mean'], mode='lines', name='Water Vapor Pressure', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['cloud-cover_quarterly_mean'], mode='lines', name='Cloud Cover', line=dict(color='orange')))

    # Update layout to add hover mode and legend positioning
    fig.update_layout(
        hovermode='x', legend=dict(x=0, y=-0.65), xaxis_title='Year', yaxis_title='Value',
        xaxis=dict(tickmode='array', tickvals=quarter_data['quarter_start'], tickformat="%Y")
        )

    #add line in 2025 to mark the start of predicted values
    fig.add_shape(
        type="line",
        x0="2025",
        y0=0,
        x1="2025",
        y1=1,
        line=dict(color="red", width=2, dash="dash"),
        xref="x",
        yref="paper"
    )

    # Show the plot
    st.plotly_chart(fig)


# Add footer
st.markdown("""
    <div class="footer">
        Created with ❤️ by Amélie, Tim, Flori, and Ali
    </div>
    """, unsafe_allow_html=True)
