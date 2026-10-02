import streamlit as st

# Page configuration
st.set_page_config(
    page_title="PriceWise",
    page_icon="📊",
    layout="wide",
)

# Import pages so Streamlit registers them under pages/ directory.
# Navigation is handled by Streamlit's pages mechanism.

# Optional: hide default Streamlit menu/header for a cleaner student demo
# Uncomment if you prefer.
# hide = """
# <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style>
# """
# st.markdown(hide, unsafe_allow_html=True)
