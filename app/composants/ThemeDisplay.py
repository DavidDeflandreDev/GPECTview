import streamlit as st
import components as c
from state_manager import reset_app_state
from themes import THEMES
from app_settings import update_setting

def display_theme_selection():
    from themes import DEFAULT_THEME
    
    light_themes = {k: v for k, v in THEMES.items() if "Dark" not in k and "Night" not in k and "Midnight" not in k and "Deep" not in k}
    dark_themes = {k: v for k, v in THEMES.items() if k not in light_themes}

    def render_theme_list(theme_dict):
        from themes import DEFAULT_THEME
        cols = c.Columns([1, 1])
        for i, (theme_name, theme_data) in enumerate(theme_dict.items()):
            is_active = st.session_state.get("app_theme", DEFAULT_THEME) == theme_name
            with cols[i % 2]:
                if c.ThemeSelector(
                    theme_name=theme_name,
                    is_active=is_active,
                    bg_color=theme_data["--bg-color"],
                    surface_color=theme_data["--surface-color"],
                    primary_color=theme_data["--primary-color"],
                    primary_hover=theme_data["--primary-hover"],
                    primary_text_color=theme_data["--primary-text-color"],
                    secondary_color=theme_data["--secondary-color"],
                    secondary_hover=theme_data["--secondary-hover"],
                    text_color=theme_data["--text-color"],
                    text_muted=theme_data["--text-muted"]
                ):
                    st.session_state.app_theme = theme_name
                    update_setting("active_theme", theme_name)
                    reset_app_state()
                    c.Rerun()

    
    c.Subheader("☀️ Modes Clairs", size="1.2rem", margin="0px 0px 20px 0px")
    render_theme_list(light_themes)
    
    c.Bar()
    c.Subheader("🌙 Modes Sombres", size="1.2rem", margin="0px 0px 20px 0px")
    render_theme_list(dark_themes)