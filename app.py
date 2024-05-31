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

#Drop 'Unnamed: 0' column if it exists (as I haad this problem before)
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

df_lc = df.drop(columns=['temperature_quarterly_mean', 'precipitation_quarterly_mean', 'water-vapor-pressure_quarterly_mean', 'cloud-cover_quarterly_mean'])
df_eco = df[["SITECODE", "quarter_start", "temperature_quarterly_mean", "precipitation_quarterly_mean", "water-vapor-pressure_quarterly_mean", "cloud-cover_quarterly_mean"]].copy()


# if 'Unnamed: 0' in df_eco.columns:
#     df = df_eco.drop(columns=['Unnamed: 0'])

# if 'temperature_quarterly_mean' in df.columns:
#     df = df.drop(columns=['temperature_quarterly_mean'])

# if 'precipitation_quarterly_mean' in df.columns:
#     df = df.drop(columns=['precipitation_quarterly_mean'])

# if 'water-vapor-pressure_quarterly_mean' in df.columns:
#     df = df.drop(columns=['water-vapor-pressure_quarterly_mean'])

# if 'cloud-cover_quarterly_mean' in df.columns:
#     df = df.drop(columns=['cloud-cover_quarterly_mean'])

# Integration of graph code
df_lc['quarter_start'] = pd.to_datetime(df_lc['quarter_start'])
df_eco['quarter_start'] = pd.to_datetime(df_lc['quarter_start'])

with st.container():
    st.markdown('<h2 style="font-size:24px;">Part I: Land Cover Proportion by Quarter</h2>', unsafe_allow_html=True)
    st.markdown("This section will display the change in land cover over time using images.")


with st.container():
    st.markdown('<h2 style="font-size:24px;">Part II: Predictions of Change in Land Cover Proportions over time</h2>', unsafe_allow_html=True)
    st.markdown("This section will display the predicted change over the next 10 years.")

    # Define available quarters
    quarters = {'Q1': '01-01', 'Q2': '04-01', 'Q3': '07-01', 'Q4': '10-01'}

    # Create dropdown for SITECODEs
    sitecodes = df_lc['SITECODE'].unique()
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

def update_df(sitecode, quarter):
    filtered_pa_data = df_lc[df_lc['SITECODE'] == sitecode]
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
    #colors = [color_dict.get(col, 'grey') for col in quarter_dates.columns if col not in ['quarter_start', 'SITECODE', 'temperature_quarterly_mean', 'precipitation_quarterly_mean', 'water-vapor-pressure_quarterly_mean', 'cloud-cover_quarterly_mean']]

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

# Additional graphs for temperature, precipitation, water-vapor-pressure, and cloud-cover
with st.container():
    st.markdown('<h2 style="font-size:24px;">Part III: Change Over Time for Ecological Variables</h2>', unsafe_allow_html=True)


    # Additional variables to plot
    additional_variables = ['temperature_quarterly_mean', 'precipitation_quarterly_mean', 'water-vapor-pressure_quarterly_mean', 'cloud-cover_quarterly_mean']

    # Loop over additional variables and create individual plots
# Loop over additional variables and create individual plots
    for variable in additional_variables:
        fig_variable, ax_variable = plt.subplots(figsize=(16, 8))

        # Filter the data for the selected sitecode
        sitecode_data = df_eco[df_eco['SITECODE'] == selected_sitecode]

        # Filter the data for the selected quarter
        quarter_data = sitecode_data[sitecode_data['quarter_start'].dt.quarter == int(quarter_dropdown[1])]

        # Plot the data for the selected variable, sitecode, and quarter
        quarter_data.plot(x='quarter_start', y=variable, ax=ax_variable, marker='o', linestyle='-')

        ax_variable.set_title(f'{variable.replace("_", " ").title()} Over Time for Quarter {quarter_dropdown}', fontsize=14)
        ax_variable.set_xlabel('Year', fontsize=12)
        ax_variable.set_ylabel('Value', fontsize=12)
        ax_variable.tick_params(axis='x', labelsize=12)
        ax_variable.tick_params(axis='y', labelsize=12)

        st.pyplot(fig_variable)


# Add footer
st.markdown("""
    <div class="footer">
        Created with ❤️ by Amélie, Tim, Flori, and Ali
    </div>
    """, unsafe_allow_html=True)
