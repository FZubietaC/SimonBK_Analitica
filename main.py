# imports functions base
import streamlit as st
# imports custom functions
from st_pages import Page, show_pages

st.set_page_config(
    page_title="Inicio",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config',
        'Report a bug': "https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config",
        'About': "# This is an app made by DataPro"
    }
)

show_pages([
    Page("main.py", "Menú de inicio"),
    Page("pages/module_1.py","Histórico de navegación"),
])