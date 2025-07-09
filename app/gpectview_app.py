import streamlit as st
from datetime import datetime
from ui import display_file_uploader, display_config_management, display_column_selection, display_visualization_settings, display_save_configuration, display_multi_response_processing
from data_processing import process_comparison_mode, process_stacked_mode, process_cross_analysis
from visualization import create_bar_chart, create_stacked_bar_chart, create_centered_bar_chart, create_pie_chart, export_chart_as_image
from config import validate_config
from constants import PALETTES_DISPONIBLES, CONFIG_DIR
import os
import pandas as pd

st.set_page_config(page_title="Analyse GPECT", layout="wide")


def initialize_session_state():
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


def main():
    initialize_session_state()
    df = display_file_uploader()
    if df is not None:
        df = df.iloc[:, 3:]
        display_config_management(df)
        # Chargement de la configuration si sélectionnée ET pas déjà chargée
        if hasattr(st.session_state, "selected_config_file") and st.session_state.selected_config_file not in [None, "Aucune"]:
            if not st.session_state.get("config_loaded_once", False):
                import json
                config_path = os.path.join(CONFIG_DIR, st.session_state.selected_config_file)
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        loaded_config = json.load(f)
                    compatible = validate_config(loaded_config, df)
                    if compatible:
                        st.sidebar.success(f"Configuration '{st.session_state.selected_config_file}' chargée et valide.")
                        for key, value in loaded_config.items():
                            st.session_state[key] = value
                        # Correction pour hide_zeros : si absent, on le met à False
                        if "hide_zeros" not in loaded_config:
                            st.session_state["hide_zeros"] = False
                        st.session_state.config_loaded_once = True
                    else:
                        if st.session_state.get("advanced_mode", False):
                            st.sidebar.warning(f"⚠️ Configuration '{st.session_state.selected_config_file}' chargée en mode avancé, mais elle est incompatible avec le fichier CSV courant !")
                            for key, value in loaded_config.items():
                                st.session_state[key] = value
                            # Correction pour hide_zeros : si absent, on le met à False
                            if "hide_zeros" not in loaded_config:
                                st.session_state["hide_zeros"] = False
                            st.session_state.config_loaded_once = True
                        else:
                            st.sidebar.error("❌ Configuration incompatible avec le fichier CSV chargé.")
                            loaded_config = {}
        start_row, end_row = display_column_selection(df)
        st.session_state.start_row = start_row
        st.session_state.end_row = end_row
        if not st.session_state.selected_columns:
            return
        selected_df = df[st.session_state.selected_columns]
        # Appliquer la sélection de lignes uniquement pour l'affichage, le traitement et l'export
        selected_df_for_processing = selected_df.iloc[start_row:end_row + 1]
        selected_df_for_processing = selected_df_for_processing.fillna(0)
        st.subheader("📄 Données sélectionnées")
        st.dataframe(selected_df_for_processing, height=300, use_container_width=True)
        st.session_state.selected_df = selected_df_for_processing
        csv_bytes = selected_df_for_processing.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Exporter les données sélectionnées (CSV)",
            data=csv_bytes,
            file_name="donnees_selectionnees.csv",
            mime="text/csv",
            help="Télécharge les données actuellement sélectionnées au format CSV."
        )
        multi_response_df = display_multi_response_processing(selected_df_for_processing)
        st.subheader("⚙️ Paramètres de visualisation")
        settings = display_visualization_settings()
        label_df = None
        if settings["analysis_mode"] == "Comparaison multiple":
            label_df = process_comparison_mode(selected_df_for_processing, settings)
        elif settings["analysis_mode"] == "Empilement":
            label_df = process_stacked_mode(selected_df_for_processing, settings)
        else:
            label_df = process_cross_analysis(selected_df_for_processing, settings)
        # --- NOUVEAU : si multi_response_df existe, on l'utilise pour le graphique ---
        use_multi_response = multi_response_df is not None
        if use_multi_response:
            label_df = multi_response_df
        # --- FIN AJOUT ---
        # Filtrage des valeurs à zéro si demandé
        if label_df is not None and settings.get("hide_zeros", False):
            if "Valeur" in label_df.columns:
                label_df = label_df[label_df["Valeur"] != 0]
        graph_container = st.empty()
        download_container = st.empty()
        if label_df is not None and not label_df.empty:
            fig = None
            try:
                with st.spinner("Génération du graphique..."):
                    show_legend = not use_multi_response
                    if settings["graph_type"] == "Barres":
                        fig = create_bar_chart(
                            label_df, 
                            settings["graph_title"], 
                            settings["x_axis_label"], 
                            settings["y_axis_label"], 
                            settings["display_as_percent"], 
                            settings["invert_axes"],
                            settings["palette"],
                            show_legend=show_legend
                        )
                    elif settings["graph_type"] == "Barres empilées":
                        if "Type" not in label_df.columns or label_df.empty:
                            st.error("❌ Pour générer un graphique à barres empilées à partir de réponses multiples, sélectionnez deux colonnes à croiser dans le module de traitement des réponses multiples.")
                            return
                        fig = create_stacked_bar_chart(
                            label_df, 
                            settings["graph_title"], 
                            settings["x_axis_label"], 
                            settings["y_axis_label"], 
                            settings["display_as_percent"], 
                            settings["invert_axes"], 
                            settings["palette"]
                        )
                    elif settings["graph_type"] == "Barres centre":
                        fig = create_centered_bar_chart(
                            label_df, 
                            settings["graph_title"], 
                            settings["x_axis_label"], 
                            settings["y_axis_label"], 
                            settings["display_as_percent"], 
                            settings["invert_axes"], 
                            settings["palette"],
                            show_legend=show_legend
                        )
                    elif settings["graph_type"] == "Camembert":
                        fig = create_pie_chart(label_df, settings["graph_title"], settings["palette"])
                        fig.update_traces(textinfo='label+percent' if settings["display_as_percent"] else 'label+value')
                graph_container.empty()
                download_container.empty()
                graph_container.plotly_chart(fig, use_container_width=True)
                st.session_state.current_fig = fig
                st.session_state.graph_settings = settings
                if settings["graph_type"] != "Scatter 3D":
                    img_bytes = export_chart_as_image(
                        label_df=label_df,
                        graph_type=settings["graph_type"],
                        graph_title=settings["graph_title"],
                        x_axis_label=settings["x_axis_label"],
                        y_axis_label=settings["y_axis_label"],
                        display_as_percent=settings["display_as_percent"],
                        invert_axes=settings["invert_axes"],
                        palette=settings["palette"],
                        palette_name=settings["palette_name"]
                    )
                    st.download_button(
                        label="📷 Télécharger le graphique (PNG)",
                        data=img_bytes,
                        file_name=f"{st.session_state.config_name}.png",
                        mime="image/png",
                        help="Télécharge le graphique affiché au format PNG."
                    )
            except Exception as e:
                graph_container.error(f"❌ Erreur lors de la création du graphique : {str(e)}")
        display_save_config = True
        config_courant = {
            "selected_columns": st.session_state.selected_columns,
            "start_row": st.session_state.get("start_row", 0),
            "end_row": st.session_state.get("end_row", 9)
        }
        if not validate_config(config_courant, df):
            display_save_config = False
            st.error("❌ La configuration courante est incompatible avec le fichier CSV chargé. Veuillez corriger la sélection avant de sauvegarder.")
        if display_save_config:
            display_save_configuration()
        st.session_state.last_selected_columns = list(selected_df.columns)
    else:
        st.info("📁 Veuillez d'abord charger un fichier CSV pour pouvoir charger une configuration.")


if __name__ == "__main__":
    main()