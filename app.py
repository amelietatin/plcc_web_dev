from io import StringIO ## for Python 3
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import ee
import geemap.foliumap as geemap
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd

import requests


#############################################################################################################################################
#############################################################################################################################################
# Page configuration
st.set_page_config(page_title="Predicting Land Cover Changes in European Protected Areas", page_icon="🌍", layout="wide")


# Navigation between Page 1, 2 and 3
# Intro page
def intro():
    st.markdown("""
    <style>
        .st-emotion-cache-12fmjuu {
            visibility: hidden;
        }
        #project-introduction {
            color: white;
        }
        h1 {
            color: white !important;
            font-size: 36px !important;
        }
        h2, h3 {
            color: white !important;
            font-size: 28px !important;
        }
        p, li {
            font-size: 22px !important;  /* Increase the size of paragraph and list item text */
        }
        [data-testid=stSidebar] {
            background-color: #a2ac94;
        }
        [data-testid="stAppViewContainer"] > .main {
            background-image: url("https://adelphi.de/system/files/styles/og_image/private/image/mario-dobelmann-pdkvqvwyyu4-unsplash.jpg?itok=bDtzCR8p");
            background-size: 100vw 100vh;
            background-position: center;
            background-repeat: no-repeat;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Predicting Land Cover Changes in European Protected Areas")

    st.markdown("""
    <div style="font-size: 20px; color:white;">
    <h2>Why is this project important?</h2>
    <ul>
    <li> Landscapes around us are constantly changing due to factors like climate change, urbanization, and natural events </li>
    <li>Over the past three decades, Europe has lost 421 million birds from its protected areas ! </li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 20px; color:white;">
    <h2>How did we proceed?</h2>
    <ul>
    <li>One sample of NATURA 2000 protected areas</li>
    <li>9 Landcovers (based on satellite data)</li>
    <li>4 climate features (based on Copernicus data): historical and future data </li>
    <li>--> Deep Learning RNN model </li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


#############################################################################################################################################
#############################################################################################################################################

# Main page
def main():
    st.title("Land Cover Change Predictions")
    st.write("(I) Map of Protected Area, (II) Historical and Future Land Cover Proportions, (III) Timely Change of Ecological Variables")

    # DATA #

    @st.cache_data
    def load_gee():
        json_data = st.secrets["json_data"]
        #json_object = json.loads(json_data, strict=False)
        service_account = st.secrets["service_account"]
        credentials = ee.ServiceAccountCredentials(service_account, key_data=json_data)
        ee.Initialize(credentials)

        #Import protected areas GEE asset
        shapefile = ee.FeatureCollection("projects/lewagon-lc-amelietatin/assets/sample_protected_areas_624")
        return shapefile

    shapefile = load_gee()

    DATA_SOURCE = 'api'

    if DATA_SOURCE == 'api':

        @st.cache_data
        def get_data():
            table_names = ['final_df','bioregion', 'habitat_class', 'impact_management','species', 'date_ranges']
            url_local = 'http://localhost:8000//data?table_name='
            url_gcp= 'https://landcoverapi-zxm7fkrvaq-ew.a.run.app//data?table_name='

            table_dict = {}
            for table_name in table_names:
                response = requests.get(url=url_gcp+table_name).json()
                table = pd.DataFrame(response)
                table_dict[table_name] = table
            return table_dict

        table_dict = get_data()
        df = table_dict.get('final_df')
        bioregion = table_dict.get('bioregion')
        habitat_class = table_dict.get('habitat_class')
        impact_management = table_dict.get('impact_management')
        species = table_dict.get('species')
        date_range_df = table_dict.get('date_ranges')

        #Drop ‘Unnamed: 0’ column if it exists

        #df = df.drop('Unnamed: 0')


    if DATA_SOURCE == 'local':
        # Load data
        @st.cache_data
        def load_data():
            df = pd.read_csv('raw_data/final_table_no_negative.csv')

            #Drop ‘Unnamed: 0’ column if it exists
            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns=['Unnamed: 0'])

            return df

        #st.write(df)

        # Timerange
        @st.cache_data
        def load_date_range():
            date_range_df = pd.read_csv('raw_data/date_ranges.csv', sep=',')
            return date_range_df

        #pa shapefile
        # @st.cache_data
        # def load_pa_shapefile():
        #     pa_sample = gpd.read_file("raw_data/sample_protected_areas_624/protected_areas_624.shp")
        #     return pa_sample

        df = load_data()
        date_range_df = load_date_range()
        #pa_sample = load_pa_shapefile()
        # PAs infos
        bioregion = pd.read_csv('raw_data/pa_infos_csv/new_csvs/bioregion.csv', sep=',')
        impact_management = pd.read_csv('raw_data/pa_infos_csv/new_csvs/impact_management.csv', sep=',')
        species = pd.read_csv('raw_data/pa_infos_csv/new_csvs/species.csv', sep=',')
        habitat_class = pd.read_csv('raw_data/pa_infos_csv/new_csvs/habitat_class.csv', sep=',')

    ##SIDEBAR
    st.sidebar.header("User Input Parameters")

    #BIOREGION
    bioregion_sitecode = bioregion[bioregion['SITECODE'].isin(df['SITECODE'])]
    bioregions = bioregion_sitecode['BIOREGION'].unique()
    selected_bioregions = st.sidebar.selectbox(
        label='Bioregion:',
        options=bioregions,
        index=8,
        help='Select a Bioregion',
    )

    bioregion_sample = bioregion_sitecode[(bioregion_sitecode['BIOREGION'] == selected_bioregions)]
    #COUNTRY
    countries = bioregion_sample.COUNTRY_NAME.unique()
    selected_sitecode = st.sidebar.selectbox(
        label='Country:',
        options=countries,
        index=2,
        help='Select a Country',
    )


    #SITECODES NAMES FOR DROPDOWN
    sitecodes = bioregion_sample.SITENAME.unique()
    selected_sitecode = st.sidebar.selectbox(
        label='Protected Area:',
        options=sitecodes,
        index=1,
        help='Select a Protected Area',
    )

    selected_sitecode = bioregion_sample[(bioregion_sample['SITENAME'] == selected_sitecode)]['SITECODE'].values[0]

    #YEARS
    years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    selected_year = st.sidebar.select_slider(
            label='Year:',
            options=list(years),
            help='Select a Year',
    )

    #QUARTERS
    quarters = {'Q1': '01-01', 'Q2': '04-01', 'Q3': '07-01', 'Q4': '10-01'}
    default_ix = list(quarters.keys()).index('Q3')
    #Create dropdown for quarters
    quarter_dropdown = st.sidebar.radio(
        label='Quarter:',
        options=list(quarters.keys()),
        index=default_ix,
        help='Select a Quarter',
        )

    # Define legend on sidebar
     # Define legend on sidebar
    legend_html = """
    <div style='padding: 10px; background-color: #f4f4f4; border: 1px solid #ddd; margin-top: 20px;'>
        <h4>Legend</h4>
        <ul style='list-style-type: none; padding: 0;'>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #419bdf; margin-right: 10px;'></span>Water</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #397d49; margin-right: 10px;'></span>Trees</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #88b053; margin-right: 10px;'></span>Grass</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #7a87c6; margin-right: 10px;'></span>Flooded Vegetation</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #e49635; margin-right: 10px;'></span>Crops</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #dfc35a; margin-right: 10px;'></span>Shrub and Scrub</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #c4281b; margin-right: 10px;'></span>Built</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #a59b8f; margin-right: 10px;'></span>Bare</li>
            <li><span style='display: inline-block; width: 20px; height: 20px; background-color: #b39fe1; margin-right: 10px;'></span>Snow and Ice</li>
        </ul>
    </div>
    """
    quarter_html = """
    <div style='padding: 10px; background-color: #f4f4f4; border: 1px solid #ddd; margin-top: 20px;'>
        <h4>Quarter range</h4>
        <ul style='list-style-type: none; padding: 0;'>
            <li><width: 20px; height: 20px; background-color: #f4f4f4; margin-right: 10px;'></span>Q1: Jan-Mar</li>
            <li><width: 20px; height: 20px; background-color: #f4f4f4; margin-right: 10px;'></span>Q2: Apr-Jun</li>
            <li><width: 20px; height: 20px; background-color: #f4f4f4; margin-right: 10px;'></span>Q3: Jul-Sep</li>
            <li><width: 20px; height: 20px; background-color: #f4f4f4; margin-right: 10px;'></span>Q4: Oct-Dec</li>
        </ul>
    </div>
    """
    # Change background color of sidebar
    st.markdown("""
    <style>
        [data-testid=stSidebar] {
            background-color: #a2ac94;
        }
    </style>
    """, unsafe_allow_html=True)

    # Add legend to sidebar
    st.sidebar.markdown(quarter_html, unsafe_allow_html=True)
    st.sidebar.markdown(legend_html, unsafe_allow_html=True)

    #############################################################################################################################################
    #############################################################################################################################################
    # Information Box
    #############################################################################################################################################
    #############################################################################################################################################

    # Function to format the information lists as bullet points in columns
    def format_info(info_list):
        if len(info_list) == 0:
            return f"No information available."
        info_str = ""
        if len(info_list) > 4:
            half = (len(info_list) +1) // 2
            col1_list = info_list[:half]
            col2_list = info_list[half:]
            info_str += "<div style='display: flex;'>"
            info_str += "<div style='flex: 1;'>"
            for item in col1_list:
                info_str += f"- {item}<br>"
            info_str += "</div><div style='flex: 1;'>"
            for item in col2_list:
                info_str += f"- {item}<br>"
            info_str += "</div></div>"
        else:
            for item in info_list:
                info_str += f"- {item}<br>"
        return info_str

    # Habitat information
    habitat_info = habitat_class[(habitat_class['SITECODE'] == selected_sitecode)]['HABITAT_DESCRIPTION'].unique()
    habitat_info_str = format_info(habitat_info)

    # Species information
    species_info = species[(species['SITECODE'] == selected_sitecode)]['SPECIESGROUP'].unique()
    species_info_str = format_info(species_info)

    # Impact information
    impact_info = impact_management[(impact_management['SITECODE'] == selected_sitecode)]['IMPACT_DESCRIPTION'].unique()
    impact_info_str = format_info(impact_info)

    # Management measures information
    manag_info = impact_management[(impact_management['SITECODE'] == selected_sitecode)]['MANAG_CONSERV_MEASURES'].unique()
    manag_info_str = format_info(manag_info)

    # Display information in collapsible sections
    with st.expander("🌳 Habitat Class Information"):
        st.markdown(habitat_info_str, unsafe_allow_html=True)

    with st.expander("🦜 Species Groups Information"):
        st.markdown(species_info_str, unsafe_allow_html=True)

    with st.expander("🌍 Impact Description Information"):
        st.markdown(impact_info_str, unsafe_allow_html=True)

    with st.expander("🍃 Management and Conservation Measures Information"):
        st.markdown(manag_info_str, unsafe_allow_html=True)

    #############################################################################################################################################
    #############################################################################################################################################
    # AMELIE
    #############################################################################################################################################
    #############################################################################################################################################

    #Define which quartal
    start = date_range_df[(date_range_df['Quartal'] == quarter_dropdown) & (date_range_df['Year'] == selected_year)]['Start_Date'].values[0]
    end = date_range_df[(date_range_df['Quartal'] == quarter_dropdown) & (date_range_df['Year'] == selected_year)]['End_Date'].values[0]

    #############################################################################################################################################
    #############################################################################################################################################
    # Part I
    #############################################################################################################################################
    #############################################################################################################################################

    with st.container():
        st.markdown('<h2 style="font-size:24px;">Part I: Historical Land Cover Proportions</h2>', unsafe_allow_html=True)
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

    df_lc = df.drop(columns=['temperature_quarterly_mean', 'precipitation_quarterly_mean', 'water-vapor-pressure_quarterly_mean', 'cloud-cover_quarterly_mean'])
    df_eco = df[["SITECODE", "quarter_start", "temperature_quarterly_mean", "precipitation_quarterly_mean", "water-vapor-pressure_quarterly_mean", "cloud-cover_quarterly_mean"]].copy()

    # Integration of graph code
    df_lc['quarter_start'] = pd.to_datetime(df_lc['quarter_start'])
    df_eco['quarter_start'] = pd.to_datetime(df_lc['quarter_start'])

    #############################################################################################################################################
    #############################################################################################################################################
    # Part II
    #############################################################################################################################################
    #############################################################################################################################################

    with st.container():
        st.markdown('<h2 style="font-size:24px;">Part II: Predictions of Change in Land Cover Proportions over Time</h2>', unsafe_allow_html=True)
        st.markdown("This section will display the historical evolution and predicted change over the next 10 years.")


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

    plt.rcParams.update({
        'font.size': 10,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial'],
        'axes.titlesize': 12,
        'axes.labelsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })

    def update_plot(quarter_dates, sitecode, quarter):
        fig, ax = plt.subplots(figsize=(16, 8))

        # Set the Seaborn style
        sns.set(style="whitegrid")

        # Get colors for the categories from the color dictionary, falling back to default if not found
        colors = [color_dict.get(col, 'grey') for col in quarter_dates.columns if col not in ['quarter_start', 'SITECODE']]

        quarter_dates.set_index('quarter_start').plot(kind='area', stacked=True, color=colors, alpha=0.8, ax=ax)
        #ax.set_title(f'Land Cover Proportions Over the Years for {sitecode} in {quarter}', fontsize=12)
        ax.set_xlabel('Year', fontsize=16)
        ax.set_ylabel('Proportion', fontsize=16)
        ax.tick_params(axis='x', labelsize=16, rotation=0)
        ax.tick_params(axis='y', labelsize=16)
        #ax.legend(title='Land Cover Category', bbox_to_anchor=(0, -0.15), ncol = 2, loc='upper left', fontsize=16, title_fontsize='18')
        ax.legend().set_visible(False)
        ax.grid(False)

        ax.axvline(pd.to_datetime('2025-01-01'), color='r', linestyle='--')

        # Adjust margins to remove the gap
        ax.margins(x=0, y=0)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.1)

        # Return the Matplotlib figure object
        return fig

    fig = update_plot(quarter_dates, selected_sitecode, quarter_dropdown)

    # Display the plot in Streamlit
    st.pyplot(fig)


    #############################################################################################################################################
    #############################################################################################################################################
    # Part III
    #############################################################################################################################################
    #############################################################################################################################################


    # Additional graphs for temperature, precipitation, water-vapor-pressure, and cloud-cover:
    with st.container():
        st.markdown('<h2 style="font-size:24px;">Part III: Predictions of Change in Ecological Variables over Time</h2>', unsafe_allow_html=True)
        st.markdown("This section will display the change in temperature, precipitation, water pressure and cloud cover from 2015 to 2035.")
        import plotly.graph_objects as go

        # Filter the data for the selected sitecode and quarter
        quarter_data = df_eco[df_eco['SITECODE'] == selected_sitecode]
        quarter_data = quarter_data[quarter_data['quarter_start'].dt.quarter == int(quarter_dropdown[1])]

        # Create the figure
        fig = go.Figure()

        # Add traces for each ecological variable
        fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['temperature_quarterly_mean'], mode='lines', name='Temperature', line=dict(color='red'), textfont=dict(size=25)))
        fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['precipitation_quarterly_mean'], mode='lines', name='Precipitation', line=dict(color='blue'), textfont=dict(size=25)))
        fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['water-vapor-pressure_quarterly_mean'], mode='lines', name='Water Vapor Pressure', line=dict(color='green'), textfont=dict(size=25)))
        fig.add_trace(go.Scatter(x=quarter_data['quarter_start'], y=quarter_data['cloud-cover_quarterly_mean'], mode='lines', name='Cloud Cover', line=dict(color='orange'), textfont=dict(size=25)))

        # Update layout to add hover mode, legend positioning, and figure size
        fig.update_layout(
            hovermode='x', legend=dict(x=0, y=-0.20), xaxis_title='Year', yaxis_title='Value',
            xaxis=dict(
                tickmode='array',
                tickvals=pd.date_range(start=quarter_data['quarter_start'].min(), end=quarter_data['quarter_start'].max(), freq='YS'),
                tickformat="%Y"
            ),
            width=1200,
            height=800
        )

        # Add line in 2025 to mark the start of predicted values
        fig.add_shape(
            type="line",
            x0="2025-01-01",
            y0=0,
            x1="2025-01-01",
            y1=1,
            line=dict(color="red", width=2, dash="dash"),
            xref="x",
            yref="paper",
        )

        # Show the plot
        st.plotly_chart(fig)


    # Add footer
    st.markdown("""
        <div class="footer">
            Created with ❤️ by Amélie, Tim, Flori, and Ali
        </div>
        """, unsafe_allow_html=True)

    #############################################################################################################################################
    #############################################################################################################################################
    # Page 3
    #############################################################################################################################################
    #############################################################################################################################################

# Intro page
def outlook():
    # Change background color of sidebar
    # Title in white color and large size

        # Title in white color and very large size
    st.markdown(
        "<h1 style='color:white; font-size:48px;'>Future Outlook</h1>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <style>
        .st-emotion-cache-12fmjuu {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

    # Bullet points with larger font size
    st.markdown(
        """
        <style>
        .bullet-points {
            color: white;
            font-size: 60px;
        }
        </style>
        <ul class="bullet-points">
            <li><strong>Model Enhancement:</strong> Updating our model with new data and improving its accuracy, could make it a reliable tool for long-term ecological forecasting.</li>
            <li><strong>Policy Planning:</strong> By predicting changes, policymakers can design better conservation strategies and allocate resources more effectively.</li>
            <li><strong>Stakeholder Engagement:</strong> Local communities, conservationists, and other stakeholders can use this tool to make informed decisions and participate in sustainable land management.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    # Set the background image
    background_image = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://3e-news.net/web/files/articles/29740/main_image/thumb_1700x960_thumb-1700x1260-aytos-mountain-2.jpg");
        background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """
    st.markdown(background_image, unsafe_allow_html=True)

# Sidebar navigation
def navigation():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Project Introduction", "Predictions", "Outlook"])

    return page

def run():
    page = navigation()

    if page == "Project Introduction":
        intro()
    elif page == "Predictions":
        main()
    elif page == "Outlook":
        outlook()

if __name__ == "__main__":
    run()
