import streamlit as st
import pandas as pd
import base64
from typing import List, Optional, Union, Any

def _apply_custom_button_style(key: str, sizeX: Union[str, int], sizeY: Union[str, int], radius: str = "8px", font_size: str = "16px"):
    """
    Injecte le CSS nécessaire pour redimensionner précisément un bouton.
    Sans Wrapper Div pour éviter de bloquer les clics.
    """
    width_map = {"small": "200px", "medium": "400px", "big": "600px"}

    def parse_width(dim: Union[str, int]) -> str:
        if isinstance(dim, int): return f"{dim}px"
        if isinstance(dim, str):
            if dim.isdigit(): return f"{dim}px"
            if any(unit in dim for unit in ["%", "px", "rem", "em", "vh", "vw"]): return dim
        return width_map.get(dim, "100%")

    def parse_height(dim: Union[str, int]) -> str:
        if dim == "auto" or dim == "small" or dim is None: return "auto"
        if isinstance(dim, int): return f"{dim}px"
        if isinstance(dim, str):
            if dim.isdigit(): return f"{dim}px"
            if any(unit in dim for unit in ["%", "px", "rem", "em", "vh", "vw"]): return dim
        return "auto"

    width_css = parse_width(sizeX)
    height_css = parse_height(sizeY)
    
    # On n'applique pas la hauteur !important si elle est "auto" pour laisser le CSS global (main.css) agir
    height_rule = f"height: {height_css} !important;" if height_css != "auto" else ""

    # On utilise selector par défaut ou spécifique si possible. 
    # Pour l'instant on garde une approche globale sécurisée ou on retire si par défaut.
    if width_css == "100%" and height_css == "auto":
        return

    Markdown(f"""
        <style>
        /* On tente de cibler le bouton via son conteneur parent Streamlit si on ne peut pas wrapper */
        /* Note: Sans div wrapper, le ciblage précis par KEY est complexe en CSS pur sans nth-child. */
        /* On applique donc les styles de taille de manière plus réfléchie dans main.css */
        </style>
    """, unsafe_allow_html=True)


def Button(label: str, style: str = "primary", data: Any = None, file_name: str = None, sizeX="100%", sizeY="auto", key=None, **kwargs):
    """
    Bouton universel (Normal ou Download). 
    Si 'data' est fourni, se comporte comme un bouton de téléchargement.
    """
    if not key: 
        prefix = "dl" if data is not None else "btn"
        key = f"{prefix}_{label.replace(' ', '_')}"
    
    # On retire le wrapping div qui bloque les clics (les boutons redeviendront 100% fonctionnels)
    # Le style de taille pour la barre d'action est maintenant géré par main.css via data-testid
    if data is not None:
        return st.download_button(label=label, data=data, file_name=file_name or "file.txt", key=key, type=style, use_container_width=True, **kwargs)
    else:
        return st.button(label, key=key, type=style, use_container_width=True, **kwargs)

def DownloadButton(*args, **kwargs):
    """Alias pour maintenir la compatibilité temporaire si nécessaire (appeler Button à la place)."""
    return Button(*args, **kwargs)


def ThemeSelector(theme_name: str, is_active: bool, **colors):
    safe_name = theme_name.replace(" ", "_").lower()
    key = f"btn_selector_{safe_name}"
    
    circles_html = "".join([
        f'<div style="width: 16px; height: 16px; border-radius: 50%; background-color: {c}; border: 0.5px solid #ccc;"></div>'
        for c in colors.values()
    ])

    Markdown(f"""
        <div style="display: flex; flex-direction: row; gap: 5px; justify-content: center; margin-bottom: 20px;">
            {circles_html}
        </div>
    """, unsafe_allow_html=True)

    btn = Button(label=theme_name, style="primary" if is_active else "secondary", key=key, sizeX="100%")
    st.markdown('<div style="margin-bottom: 30px;"></div>', unsafe_allow_html=True)
    return btn

def Title(text: str, color: str = "var(--text-color)", align: str = "left", size: Union[str, int] = "2.5rem", weight: Union[str, int] = 700, margin: str = "0px 0px 1rem 0px"):
    """
    Titre hautement personnalisable utilisant une balise Div pour éviter les ancres de lien Streamlit.
    """
    style = f"""
        color: {color}; 
        text-align: {align}; 
        font-size: {f"{size}px" if isinstance(size, int) else size};
        font-weight: {weight};
        margin: {margin};
        line-height: 1.2;
        display: block;
    """
    Markdown(f"<div style='{style}'>{text}</div>", unsafe_allow_html=True)

def Subheader(text: str, color: str = "var(--text-color)", align: str = "left", size: Union[str, int] = "1.5rem", margin: str = "0px 0px 1rem 0px"):
    """
    Sous-titre stylisé (équivalent h3) sans ancres Streamlit.
    """
    style = f"""
        color: {color}; 
        text-align: {align}; 
        font-size: {f"{size}px" if isinstance(size, int) else size};
        font-weight: 600;
        margin: {margin};
        display: block;
    """
    Markdown(f"<div style='{style}'>{text}</div>", unsafe_allow_html=True)

def Caption(text: str):
    """Texte de légende discret."""
    Markdown(f"<span style='color: var(--text-muted); font-size: 0.85em;'>{text}</span>", unsafe_allow_html=True)

def Markdown(text: str, unsafe_allow_html: bool = False):
    """Wrapper pour st.markdown."""
    st.markdown(text, unsafe_allow_html=unsafe_allow_html)

def DataFrame(df: pd.DataFrame, height: Optional[int] = None, css_class: str = "gpec-table", row_min_height: int = 40):
    """Affiche un DataFrame Pandas sous forme de table HTML stylisée."""
    html_table = df.to_html(classes=css_class, index=False)
    row_style = f"""
    <style>
        .{css_class} td, .{css_class} th {{
            min-height: {row_min_height}px !important;
            height: {row_min_height}px;
            padding: 0 0.75rem !important;
            vertical-align: middle !important;
            white-space: nowrap;
        }}
    </style>
    """
    Markdown(
        f"<div class='table-container' style='height: {height}px; overflow-y: auto;'>{row_style}{html_table}</div>",
        unsafe_allow_html=True
    )

def _AlertBox(text: str, bg_color: str, border_color: str, text_color: str, icon: str):
    """Interne : Boîte de notification stylisée."""
    from themes import THEMES, DEFAULT_THEME
    theme_name = st.session_state.get("app_theme", DEFAULT_THEME)
    is_dark = THEMES.get(theme_name, {}).get("--is-dark", False)
    
    # Si on est en mode sombre, on s'assure que le texte sur fond clair (hardcodé) reste lisible
    # en forçant une couleur sombre, car le global CSS force var(--text-color) !important.
    actual_text_color = "#1a1a1a" if is_dark else text_color

    Markdown(f"""
        <div class="custom-alert" style="
            background-color: {bg_color};
            border-left: 5px solid {border_color};
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        ">
            <span style="margin-right: 10px;">{icon}</span>
            <div style="color: {actual_text_color} !important; font-weight: 500;">{text}</div>
        </div>
        <style>
        .custom-alert div, .custom-alert p {{
            color: {actual_text_color} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def Info(text: str):
    _AlertBox(text, "#e1f5fe", "#0288d1", "#01579b", "ℹ️")

def Success(text: str):
    _AlertBox(text, "#e8f5e9", "#43a047", "#1b5e20", "✅")

def Warning(text: str):
    _AlertBox(text, "#fff3e0", "#fb8c00", "#e65100", "⚠️")

def Error(text: str):
    _AlertBox(text, "#ffebee", "#e53935", "#b71c1c", "🚨")

def Expander(label: str, expanded: bool = True, on_delete=None, delete_key: str = None):
    """
    Wrapper pour st.expander. 
    Affiche un bouton de suppression à côté de l'expander en utilisant des colonnes.
    """
    if on_delete and delete_key:
        col_exp, col_del = st.columns([0.9, 0.1], vertical_alignment="top", gap="small")
        with col_del:
            if st.button("🗑️", key=delete_key, help=f"Supprimer {label}"):
                on_delete()
        with col_exp:
            return st.expander(label, expanded=expanded)
    return st.expander(label, expanded=expanded)

def Columns(ratios: List[float]):
    """Wrapper pour st.columns."""
    return st.columns(ratios)

def Sidebar():
    """Accès direct à la barre latérale."""
    return st.sidebar

def TextInput(label: str, value: str = "", placeholder: str = "", key: str = None, on_change=None, args=None, help: str = None, disabled: bool = False):
    """Input texte stylisé."""
    return st.text_input(label=label, value=value, key=key, placeholder=placeholder, help=help, on_change=on_change, args=args or (), disabled=disabled)

def NumberInput(label: str, min_value=None, max_value=None, value=None, key: str = None, on_change=None, args=None, help: str = None):
    """Input numérique stylisé."""
    return st.number_input(label=label, min_value=min_value, max_value=max_value, value=value, key=key, help=help, on_change=on_change, args=args or ())

def SelectBox(label: str, options: list, index: int = 0, key: str = None, on_change=None, args=None, help: str = None, disabled: bool = False, placeholder: str = "Sélectionnez une option"):
    """Menu déroulant stylisé."""
    return st.selectbox(label=label, options=options, index=index, key=key, help=help, on_change=on_change, args=args or (), disabled=disabled)

def MultiSelect(label: str, options: list, default=None, key: str = None, on_change=None, args=None, help: str = None, disabled: bool = False):
    """Multisélection stylisée."""
    return st.multiselect(label=label, options=options, default=default, key=key, help=help, on_change=on_change, args=args or (), disabled=disabled)

def Radio(label: str, options: list, index: int = 0, key: str = None, on_change=None, args=None, help: str = None):
    """Boutons radio stylisés."""
    return st.radio(label=label, options=options, index=index, key=key, help=help, on_change=on_change, args=args or ())

def Checkbox(label: str, value: bool = False, key: str = None, on_change=None, args=None, help: str = None):
    """Case à cocher stylisée."""
    return st.checkbox(label=label, value=value, key=key, help=help, on_change=on_change, args=args or ())

def SectionHeader(title: str, subtitle: str = None):
    """En-tête de section avec titre et sous-titre optionnel."""
    if subtitle:
        Markdown(f"### {title}\n<span style='color: var(--text-muted); font-size: 0.9em;'>{subtitle}</span>", unsafe_allow_html=True)
    else:
        Subheader(title)


def FileUploader(label: str, type=None, help: str = None):
    """Wrapper pour le chargement de fichiers."""
    return st.file_uploader(label=label, type=type, help=help)


def Rerun():
    """Redémarre l'application (st.rerun)."""
    st.rerun()

def Empty():
    """Slot vide (st.empty)."""
    return st.empty()

def Container():
    """Conteneur (st.container)."""
    return st.container()

def ScrollContainer(height: int):
    """Conteneur avec barre de défilement (st.container avec height)."""
    return st.container(height=height)

def Popover(label: str, sizeX="100%", sizeY="auto", key=None):
    """Popover stylisé utilisant le même système que les boutons."""
    if not key: key = f"pop_{label.replace(' ', '_')}"
    
    if hasattr(st, "popover"):
        return st.popover(label, use_container_width=True)
    else:
        return st.expander(label)

def Dialog(title: str):
    """
    Décorateur pour créer une boîte de dialogue (modal).
    Usage:
    @c.Dialog("Mon Titre")
    def ma_fonc():
        st.write("Hello")
    """
    if hasattr(st, "dialog"):
        return st.dialog(title)
    
    # Fallback si st.dialog n'est pas disponible (versions < 1.34.0)
    def decorator(func):
        def wrapper(*args, **kwargs):
            with st.expander(title, expanded=True):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def PlotlyChart(fig, use_container_width: bool = True):
    """Affiche un graphique Plotly."""
    return st.plotly_chart(fig, use_container_width=use_container_width)

def Toast(text: str, icon: str = None):
    """Notification toast ephémère."""
    st.toast(text, icon=icon)

def Spinner(text: str):
    """Indicateur de chargement."""
    return st.spinner(text)

def Card(padding: str = "1rem", radius: str = "10px", background: str = "transparent", border: str = "1px solid var(--secondary-color)", margin: str = "10px 0px", align: str = "left", flex_direction: str = "column", justify_content: str = "center", align_items: str = "center", gap: str = "10px", children: str = ""):
    """Conteneur Div stylisé générique."""
    style = f"""
        display: flex;
        flex-direction: {flex_direction};
        justify-content: {justify_content};
        align-items: {align_items};
        gap: {gap};
        background-color: {background};
        border: {border};
        border-radius: {radius};
        padding: {padding};
        margin: {margin};
        text-align: {align};
        color: var(--text-color);
    """
    Markdown(f"<div style='{style}'>{children}</div>", unsafe_allow_html=True)

def Bar():
    Markdown("---", unsafe_allow_html=True)