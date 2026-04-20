import streamlit as st
import components as c
from constants import PALETTES_DISPONIBLES

def display_visualization_settings():
    # --- Type de graphique : hors de l'expander, visible directement ---
    graph_type_options = [
        "Barres", "Barres centre", "Camembert", "Barres empilées", "Répartition croisée"
    ]
    default_graph_type = st.session_state.get("graph_type", "Barres")
    if default_graph_type not in graph_type_options:
        st.session_state["graph_type"] = "Barres"
        default_graph_type = "Barres"
    default_graph_index = graph_type_options.index(default_graph_type)
    graph_type = c.SelectBox(
        "Type de graphique",
        graph_type_options,
        index=default_graph_index,
        key="graph_type"
    )

    # --- Mode d'analyse (dépend du type) ---
    if graph_type == "Barres empilées":
        analysis_mode = "Empilement"
    elif graph_type in ("Camembert", "Répartition croisée"):
        analysis_mode = "Comparaison multiple"
    else:
        analysis_mode_options = ["Comparaison multiple", "Analyse croisée simple"]
        default_analysis_mode = st.session_state.get("analysis_mode", "Comparaison multiple")
        # Nettoyer la session si la valeur stockée ne correspond plus aux options actuelles
        if default_analysis_mode not in analysis_mode_options:
            st.session_state["analysis_mode"] = "Comparaison multiple"
            default_analysis_mode = "Comparaison multiple"
        default_analysis_index = analysis_mode_options.index(default_analysis_mode)
        analysis_mode = c.Radio("Mode d'analyse", analysis_mode_options, index=default_analysis_index, key="analysis_mode")

    # --- Autres options dans l'expander ---
    with c.Expander("🔧 Options de visualisation"):
        display_as_percent = c.Checkbox("Afficher en pourcentage", value=st.session_state.get("display_as_percent", False), key="display_as_percent")

        palette_name = c.SelectBox(
            "Palette de couleurs",
            list(PALETTES_DISPONIBLES.keys()),
            index=list(PALETTES_DISPONIBLES.keys()).index(st.session_state.get("palette_name", "Plotly")) if st.session_state.get("palette_name", "Plotly") in PALETTES_DISPONIBLES else 0,
            key="palette_name"
        )
        palette = PALETTES_DISPONIBLES.get(palette_name)

        is_pie = graph_type == "Camembert"

        if not is_pie:
            x_axis_label = c.TextInput("Axe horizontal (X)", value=st.session_state.get("x_axis_label", "Label"), key="x_axis_label")
            y_axis_label = c.TextInput("Axe vertical (Y)", value=st.session_state.get("y_axis_label", "Valeur"), key="y_axis_label")
            invert_axes = c.Checkbox("Inverser les axes X et Y", value=st.session_state.get("invert_axes", False), key="invert_axes")
        else:
            x_axis_label = st.session_state.get("x_axis_label", "Label")
            y_axis_label = st.session_state.get("y_axis_label", "Valeur")
            invert_axes = False

        hide_zeros = c.Checkbox("Masquer les valeurs à zéro", value=st.session_state.get("hide_zeros", False), key="hide_zeros")

    graph_title = c.TextInput("Titre du graphe", value=st.session_state.get("graph_title", ""), key="graph_title")
    return {
        "graph_type": graph_type, "analysis_mode": analysis_mode, "display_as_percent": display_as_percent,
        "x_axis_label": x_axis_label, "y_axis_label": y_axis_label, "invert_axes": invert_axes,
        "graph_title": graph_title, "palette": palette, "palette_name": palette_name,
        "hide_zeros": hide_zeros,
        "pivot_field_regroupement": None, "pivot_field_empilement": None, "pivot_field_valeur": None
    }
