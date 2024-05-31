import streamlit as st
import os

# Page configuration
st.set_page_config(page_title="Land Cover Changes Predictor", page_icon="🔍", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: black;
        text-align: center;
        margin-bottom: 20px;
        line-height: 2.5; /* Adjust line height */
    }
    .subtitle {
        font-size: 1.5rem;
        color: black;
        text-align: center;
        margin-bottom: 20px;
        line-height: 2.5; /* Adjust line height */
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(232, 234, 235, 0.8);
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #333;
    }
    .success {
        color: green;
    }
    .error {
        color: red;
    }
    .stButton button {
        background-color: #4A90E2;
        color: white;
    }
    .centered-button {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and subtitle
st.markdown('<div class="main-title">Land Cover Changes Predictor 🔍</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Check Land Cover Status Between 2015 and 2024</div>', unsafe_allow_html=True)

# Sample list of existing IDs
existing_ids = ["40A0", "91D0", "91E0", "91F0", "91U0", "1130", "1140", "1210", "6240", "6170"]

# Text input for ID search
user_input = st.text_input("Enter the protected area's ID and press Enter:")

# Check if the input ID is in the list
if user_input:
    if user_input in existing_ids:
        st.markdown(f"<span class='success'>ID {user_input} found!</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='error'>Error: ID {user_input} not found.</span>", unsafe_allow_html=True)

# Year selection slider
year = st.slider("Select Year", 2015, 2024, 2015)

# Display map for the selected ID and year if the ID is valid
if user_input and user_input in existing_ids:
    # Assuming you have map images stored in a folder named 'maps'
    # with filenames formatted as 'ID_Year.png' (e.g., '40A0_2015.png')
    map_filename = f"maps/{user_input}_{year}.png"

    if os.path.exists(map_filename):
        st.image(map_filename, caption=f"Land Cover Map for {user_input} in {year}", use_column_width=True)
    else:
        st.markdown(f"<span class='error'>Map not found for ID {user_input} in {year}.</span>", unsafe_allow_html=True)

st.markdown('<div class="subtitle">Predict The Status of The Land Cover in The Future</div>', unsafe_allow_html=True)

# Form for year, temperature, and precipitation inputs
with st.form(key='prediction_form'):
    st.markdown('<div class="subtitle">Enter Prediction Parameters</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        pred_year = st.text_input("Year")
    with col2:
        temperature = st.text_input("Temperature (°C)")
    with col3:
        precipitation = st.text_input("Precipitation (mm)")

    # Center the submit button
    st.markdown('<div class="centered-button">', unsafe_allow_html=True)
    submit_button = st.form_submit_button(label='Submit')
    st.markdown('</div>', unsafe_allow_html=True)

# Display prediction result after form submission
if submit_button:
    if pred_year and temperature and precipitation:
        st.markdown(f"### Here is the predicted status of land cover in {pred_year} with the given temperature ({temperature}°C) and precipitation ({precipitation} mm).")
    else:
        st.markdown(f"<span class='error'>Please fill in all the fields.</span>", unsafe_allow_html=True)

# Add footer
st.markdown("""
    <div class="footer">
        Created with ❤️ by Amélie, Tim, Florentine, and Ali
    </div>
    """, unsafe_allow_html=True)
