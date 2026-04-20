import os
import streamlit as st
from themes import THEMES, DEFAULT_THEME
from app_settings import get_setting

def whiten_color(hex_color, factor=0.96):
    """Mélange une couleur hex avec du blanc selon un facteur (0-1)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # Interpolation linéaire vers (255, 255, 255)
    new_rgb = tuple(int(c + (255 - c) * factor) for c in rgb)
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

def load_global_styles():
    """
    Lit tous les fichiers CSS dans app/style/ et les injecte globalement dans l'application Streamlit.
    Génère également les variables CSS depuis le thème sélectionné.
    """
    # Initialisation du thème depuis les paramètres persistants
    if "app_theme" not in st.session_state:
        saved_theme = get_setting("active_theme", DEFAULT_THEME)
        # Vérification que le thème sauvegardé existe toujours dans THEMES
        st.session_state["app_theme"] = saved_theme if saved_theme in THEMES else DEFAULT_THEME

    # 1. Génération des Variables selon le thème choisi
    theme_name = st.session_state.get("app_theme", DEFAULT_THEME)
    if theme_name not in THEMES:
        theme_name = DEFAULT_THEME

    # On travaille sur une copie pour ne pas polluer THEMES
    theme_data = THEMES[theme_name].copy()
    
    # Variables dynamiques en CSS
    theme_vars = "\n".join([f"    {k}: {v};" for k, v in theme_data.items() if k != "--is-dark"])
    
    css_variables = f"""
:root {{
{theme_vars}
}}

/* Masquer les ancres de lien Streamlit pour eviter le decalage au survol */
[data-testid="stHeaderActionElements"] {{
    display: none !important;
}}
"""

    # 2. Lecture des fichiers CSS
    css_files = ["buttons.css", "inputs.css", "tables.css", "main.css"]
    style_dir = os.path.join(os.path.dirname(__file__), "style")
    
    combined_css = css_variables + "\n\n"
    for filename in css_files:
        filepath = os.path.join(style_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                combined_css += f.read() + "\n"
    
    if combined_css:
        st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)

