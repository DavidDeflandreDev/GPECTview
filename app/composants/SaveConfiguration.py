import streamlit as st
import components as c
import os
import json
from config import list_all_folders
from constants import CONFIG_DIR

def get_current_configuration():
    return {
        "selected_columns": st.session_state.selected_columns,
        "start_row": st.session_state.get("start_row", 0),
        "end_row": st.session_state.get("end_row", 9),
        "analysis_mode": st.session_state.get("analysis_mode", "Comparaison multiple"),
        "graph_type": st.session_state.get("graph_type", "Barres"),
        "display_as_percent": st.session_state.get("display_as_percent", False),
        "graph_title": st.session_state.get("graph_title", ""),
        "value_cols_multiple": st.session_state.get("value_cols_multiple", []),
        "value_cols_stack": st.session_state.get("value_cols_stack", []),
        "group_col_stack": st.session_state.get("group_col_stack", None),
        "col_x": st.session_state.get("col_x", None),
        "col_y": st.session_state.get("col_y", None),
        "x_axis_label": st.session_state.get("x_axis_label", "Label"),
        "y_axis_label": st.session_state.get("y_axis_label", "Valeur"),
        "invert_axes": st.session_state.get("invert_axes", False),
        "palette_name": st.session_state.get("palette_name", "Plotly"),
        "hide_zeros": st.session_state.get("hide_zeros", False),
        "pivot_field_regroupement": st.session_state.get("pivot_field_regroupement"),
        "pivot_field_empilement": st.session_state.get("pivot_field_empilement"),
        "pivot_field_valeur": st.session_state.get("pivot_field_valeur"),
        # Champs pour le type "Répartition croisée" (analyse 3D)
        "rc_col_x": st.session_state.get("rc_col_x"),
        "rc_col_color": st.session_state.get("rc_col_color"),
        "rc_col_value": st.session_state.get("rc_col_value"),
    }


def display_save_configuration():
    all_folders = list_all_folders()
    col1, col2, col3 = c.Columns([3, 2, 2])
    with col1:
        config_name_input = c.TextInput(
            "Nom du fichier JSON de configuration (sans extension)",
            value=st.session_state.config_name
        )
        dossier_select = c.SelectBox(
            "Dossier de configuration",
            options=all_folders,
            index=0,
            key="config_dossier_select"
        )
    with col2:
        c.Markdown("<div style='height: 2em'></div>", unsafe_allow_html=True)
        if c.Button("💾 Sauvegarder cette configuration", key="save_config_btn"):
            config_name_str = str(config_name_input).strip() if config_name_input else ""
            if not config_name_str:
                c.Error("Veuillez entrer un nom valide pour la configuration")
            else:
                try:
                    config_to_save = get_current_configuration()
                    dossier_path = os.path.join(CONFIG_DIR, dossier_select)
                    if not os.path.exists(dossier_path):
                        os.makedirs(dossier_path)
                    file_path = os.path.join(dossier_path, f"{config_name_str}.json")
                    with open(file_path, "w") as f:
                        json.dump(config_to_save, f, indent=4)
                    c.Success(f"Configuration sauvegardée dans : {file_path}")
                    st.session_state.config_name = config_name_str
                    c.Rerun()
                except Exception as e:
                    c.Error(f"Erreur lors de la sauvegarde : {str(e)}")
    with col3:
        c.Markdown("<div style='height: 2em'></div>", unsafe_allow_html=True)
        if hasattr(st.session_state, "selected_config_file") and st.session_state.selected_config_file not in [None, "Aucune"]:
            if c.Button("💾 Sauvegarder la configuration chargée", key="save_loaded_config_btn"):
                try:
                    config_to_save = get_current_configuration()
                    selected_file = st.session_state.selected_config_file
                    if os.sep in selected_file:
                        dossier, file_name = os.path.split(selected_file)
                        dossier_path = os.path.join(CONFIG_DIR, dossier)
                        file_path = os.path.join(dossier_path, file_name)
                    else:
                        file_path = os.path.join(CONFIG_DIR, selected_file)
                    with open(file_path, "w") as f:
                        json.dump(config_to_save, f, indent=4)
                    c.Success(f"Configuration existante écrasée : {file_path}")
                    st.session_state.config_name = os.path.splitext(os.path.basename(file_path))[0]
                    c.Rerun()
                except Exception as e:
                    c.Error(f"Erreur lors de la sauvegarde : {str(e)}")
    with c.Sidebar():
        c.Markdown("---")
