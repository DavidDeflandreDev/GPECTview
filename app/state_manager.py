import streamlit as st
from datetime import datetime

def initialize_session_state():
    """Initialisation globale des variables de session au démarrage."""
    if "selected_columns" not in st.session_state:
        st.session_state.selected_columns = []
    if "confirm_delete_file" not in st.session_state:
        st.session_state.confirm_delete_file = None
    if "config_name" not in st.session_state:
        st.session_state.config_name = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if "show_download" not in st.session_state:
        st.session_state.show_download = False
    if "img_bytes" not in st.session_state:
        st.session_state.img_bytes = None
    if "current_fig" not in st.session_state:
        st.session_state.current_fig = None
    if "graph_settings" not in st.session_state:
        st.session_state.graph_settings = None

def reset_app_state():
    """Réinitialise les variables liées aux données et à la visualisation."""
    st.session_state.selected_columns = []
    st.session_state.start_row = 0
    st.session_state.end_row = 0
    st.session_state.selected_config_file = None
    st.session_state.config_loaded_once = False
    st.session_state.current_fig = None
    st.session_state.img_bytes = None
