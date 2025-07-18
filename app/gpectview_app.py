import streamlit as st
from datetime import datetime
from ui import display_file_uploader, display_config_management, display_column_selection, display_visualization_settings, display_save_configuration, display_multi_response_processing
from data_processing import process_comparison_mode, process_stacked_mode, process_cross_analysis
from visualization import create_bar_chart, create_stacked_bar_chart, create_centered_bar_chart, create_pie_chart, export_chart_as_image
from config import validate_config
from constants import PALETTES_DISPONIBLES, CONFIG_DIR
import os
import pandas as pd
from utils import format_number

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
        st.info("Si l’affichage est trop étroit après un rechargement, ouvrez le menu 'Settings' (⚙️ en haut à droite) et activez le mode 'Wide'.")
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
                    # MIGRATION : suppression de agg_func si présent
                    if "agg_func" in loaded_config:
                        del loaded_config["agg_func"]
                        # Sauvegarde la config mise à jour
                        with open(config_path, "w") as f2:
                            json.dump(loaded_config, f2, indent=4)
                        st.sidebar.info("Configuration ancienne détectée : champ 'Type de calcul' supprimé et config mise à jour.")
                    # Force le type de graphe AVANT l'affichage des paramètres
                    if "graph_type" in loaded_config:
                        st.session_state["graph_type"] = loaded_config["graph_type"]
                    compatible = validate_config(loaded_config, df)
                    if compatible:
                        st.sidebar.success(f"Configuration '{st.session_state.selected_config_file}' chargée et valide.")
                        for key, value in loaded_config.items():
                            st.session_state[key] = value
                        # Correction pour hide_zeros : si absent, on le met à False
                        if "hide_zeros" not in loaded_config:
                            st.session_state["hide_zeros"] = False
                        # Force le type de graphe pour affichage correct
                        if "graph_type" in loaded_config:
                            st.session_state["graph_type"] = loaded_config["graph_type"]
                        # Restaure les colonnes du pivot si présentes
                        for k in ["pivot_col_regroupement", "pivot_col_empilement", "pivot_col_valeur"]:
                            if k in loaded_config:
                                st.session_state[k] = loaded_config[k]
                        st.session_state.config_loaded_once = True
                    else:
                        if st.session_state.get("advanced_mode", False):
                            st.sidebar.warning(f"⚠️ Configuration '{st.session_state.selected_config_file}' chargée en mode avancé, mais elle est incompatible avec le fichier CSV courant !")
                            for key, value in loaded_config.items():
                                st.session_state[key] = value
                            if "hide_zeros" not in loaded_config:
                                st.session_state["hide_zeros"] = False
                            for k in ["pivot_col_regroupement", "pivot_col_empilement", "pivot_col_valeur"]:
                                if k in loaded_config:
                                    st.session_state[k] = loaded_config[k]
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
        # Appliquer fillna(0) uniquement sur les colonnes numériques, et fillna("") sur les colonnes texte
        for col in selected_df_for_processing.columns:
            if pd.api.types.is_numeric_dtype(selected_df_for_processing[col]):
                selected_df_for_processing[col] = selected_df_for_processing[col].fillna(0)
            else:
                selected_df_for_processing[col] = selected_df_for_processing[col].fillna("")
        # Affichage : formater une copie pour l'utilisateur
        display_df = selected_df_for_processing.copy()
        for col in display_df.columns:
            if pd.api.types.is_numeric_dtype(display_df[col]):
                display_df[col] = display_df[col].fillna(0).apply(format_number)
            elif display_df[col].dtype == object:
                display_df[col] = display_df[col].replace([None, float('nan'), 'nan'], '').fillna('')
        st.subheader("📄 Données sélectionnées")
        st.dataframe(display_df, height=300, use_container_width=True)
        st.session_state.selected_df = selected_df_for_processing
        csv_bytes = display_df.to_csv(index=False).encode('utf-8')
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
        # Initialisation de l'affichage de la config
        display_save_config = True

        # Sélection spécifique pour le Graphe de synthèse croisée
        col_regroupement = col_empilement = col_valeur = None
        if settings["graph_type"] == "Graphe de synthèse croisée":
            st.subheader("Paramètres du Graphe de synthèse croisée")
            all_cols = list(selected_df_for_processing.columns)
            # Utilise les variables explicites si présentes, sinon valeur vide
            pivot_regroupement = st.session_state.get("pivot_field_regroupement") or st.session_state.get("pivot_col_regroupement") or ""
            pivot_empilement = st.session_state.get("pivot_field_empilement") or st.session_state.get("pivot_col_empilement") or ""
            pivot_valeur = st.session_state.get("pivot_field_valeur") or st.session_state.get("pivot_col_valeur") or ""
            config_suffix = st.session_state.get("config_name", "default")
            temp_col_regroupement = st.selectbox(
                "Colonne de regroupement (X/barres)", ["-- Sélectionner --"] + all_cols,
                index=all_cols.index(pivot_regroupement) + 1 if pivot_regroupement in all_cols else 0,
                key=f"pivot_temp_col_regroupement_{config_suffix}"
            )
            temp_col_empilement = st.selectbox(
                "Colonne à empiler (catégorie/couleur)", ["-- Sélectionner --"] + all_cols,
                index=all_cols.index(pivot_empilement) + 1 if pivot_empilement in all_cols else 0,
                key=f"pivot_temp_col_empilement_{config_suffix}"
            )
            temp_col_valeur = st.selectbox(
                "Colonne de valeur (somme)", ["-- Sélectionner --"] + all_cols,
                index=all_cols.index(pivot_valeur) + 1 if pivot_valeur in all_cols else 0,
                key=f"pivot_temp_col_valeur_{config_suffix}"
            )
            if st.button("Valider la sélection des colonnes du pivot", key=f"valider_pivot_{config_suffix}"):
                if temp_col_regroupement != "-- Sélectionner --" and temp_col_empilement != "-- Sélectionner --" and temp_col_valeur != "-- Sélectionner --":
                    st.session_state["pivot_col_regroupement"] = temp_col_regroupement
                    st.session_state["pivot_col_empilement"] = temp_col_empilement
                    st.session_state["pivot_col_valeur"] = temp_col_valeur
                    st.session_state["pivot_field_regroupement"] = temp_col_regroupement
                    st.session_state["pivot_field_empilement"] = temp_col_empilement
                    st.session_state["pivot_field_valeur"] = temp_col_valeur
                else:
                    st.warning("Veuillez sélectionner les trois colonnes avant de valider.")
            col_regroupement = st.session_state.get("pivot_field_regroupement") or st.session_state.get("pivot_col_regroupement")
            col_empilement = st.session_state.get("pivot_field_empilement") or st.session_state.get("pivot_col_empilement")
            col_valeur = st.session_state.get("pivot_field_valeur") or st.session_state.get("pivot_col_valeur")
            # Message d'instruction si pas de sélection
            if not col_regroupement or not col_empilement or not col_valeur:
                st.info("Veuillez sélectionner les trois colonnes pour générer le graphe de synthèse croisée.")
        else:
            st.session_state.pop("pivot_col_regroupement", None)
            st.session_state.pop("pivot_col_empilement", None)
            st.session_state.pop("pivot_col_valeur", None)
            st.session_state.pop("pivot_field_regroupement", None)
            st.session_state.pop("pivot_field_empilement", None)
            st.session_state.pop("pivot_field_valeur", None)

        # Génération des données selon le type de graphe
        if settings["graph_type"] == "Graphe de synthèse croisée":
            if col_regroupement and col_empilement and col_valeur:
                temp_df = selected_df_for_processing[[col_regroupement, col_empilement, col_valeur]].copy()
                temp_df[col_valeur] = pd.to_numeric(temp_df[col_valeur], errors="coerce")
                if not isinstance(temp_df[col_valeur], pd.Series):
                    temp_df[col_valeur] = pd.Series([temp_df[col_valeur]])
                temp_df[col_valeur] = temp_df[col_valeur].fillna(0)
                grouped = temp_df.groupby([col_regroupement, col_empilement])[col_valeur].sum().reset_index()
                label_df = grouped.rename(columns={
                    col_regroupement: "Label",
                    col_empilement: "Type",
                    col_valeur: "Valeur"
                })
            else:
                label_df = None
        elif settings["analysis_mode"] == "Comparaison multiple":
            label_df = process_comparison_mode(selected_df_for_processing, settings)
        elif settings["analysis_mode"] == "Empilement":
            label_df = process_stacked_mode(selected_df_for_processing, settings)
        else:
            label_df = process_cross_analysis(selected_df_for_processing, settings)
        # --- NOUVEAU : si multi_response_df existe, on l'utilise pour le graphique ---
        # Correction : n'utiliser le DataFrame multi-réponses que pour les graphes adaptés
        use_multi_response = multi_response_df is not None
        if use_multi_response and settings["graph_type"] in ["Barres empilées", "Camembert"]:
            label_df = multi_response_df
        # --- FIN AJOUT ---
        # Filtrage des valeurs à zéro si demandé
        if label_df is not None and isinstance(label_df, pd.DataFrame) and settings.get("hide_zeros", False):
            if "Valeur" in label_df.columns:
                label_df = label_df[label_df["Valeur"] != 0]
        graph_container = st.empty()
        download_container = st.empty()
        if label_df is not None and isinstance(label_df, pd.DataFrame) and not label_df.empty:
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
                    elif settings["graph_type"] == "Recrutements par métier et par année (barres empilées)":
                        fig = create_stacked_bar_chart(
                            label_df,
                            settings["graph_title"] or "Recrutements par métier et par année (barres empilées)",
                            settings["x_axis_label"] or "Année",
                            settings["y_axis_label"] or "Nombre de recrutements",
                            settings["display_as_percent"],
                            settings["invert_axes"],
                            settings["palette"]
                        )
                    elif settings["graph_type"] == "Graphe de synthèse croisée":
                        # Correction : affichage en pourcentage par colonne (Label)
                        if settings["display_as_percent"] and label_df is not None and "Label" in label_df.columns and "Type" in label_df.columns and "Valeur" in label_df.columns:
                            total_by_label = label_df.groupby("Label")["Valeur"].transform("sum")
                            label_df = label_df.copy()
                            label_df["Valeur"] = label_df["Valeur"] / total_by_label * 100
                        fig = create_stacked_bar_chart(
                            label_df,
                            settings["graph_title"] or "Graphe de synthèse croisée",
                            settings["x_axis_label"] or "Année",
                            settings["y_axis_label"] or "Nombre de recrutements",
                            settings["display_as_percent"],
                            settings["invert_axes"],
                            settings["palette"]
                        )
                graph_container.empty()
                download_container.empty()
                graph_container.plotly_chart(fig, use_container_width=True)
                st.session_state.current_fig = fig
                st.session_state.graph_settings = settings
                if settings["graph_type"] != "Scatter 3D":
                    img_bytes = export_chart_as_image(
                        label_df=label_df,
                        graph_type="Barres empilées" if settings["graph_type"] == "Graphe de synthèse croisée" else settings["graph_type"],
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
                st.error("❌ Cette manipulation semble impossible avec les données ou les paramètres actuels.\nDétail technique : " + str(e))
        # --- Sauvegarde de la configuration ---
        config_courant = {
            "selected_columns": st.session_state.selected_columns,
            "start_row": st.session_state.get("start_row", 0),
            "end_row": st.session_state.get("end_row", 9)
        }
        # Ajout des paramètres spécifiques au graphe de synthèse croisée
        if settings["graph_type"] == "Graphe de synthèse croisée":
            config_courant["pivot_col_regroupement"] = st.session_state.get("pivot_col_regroupement")
            config_courant["pivot_col_empilement"] = st.session_state.get("pivot_col_empilement")
            config_courant["pivot_col_valeur"] = st.session_state.get("pivot_col_valeur")
            # Nouvelles variables explicites pour la config
            config_courant["pivot_field_regroupement"] = st.session_state.get("pivot_col_regroupement")
            config_courant["pivot_field_empilement"] = st.session_state.get("pivot_col_empilement")
            config_courant["pivot_field_valeur"] = st.session_state.get("pivot_col_valeur")
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