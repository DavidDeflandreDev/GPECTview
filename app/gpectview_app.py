import streamlit as st
import components as c
from style_loader import load_global_styles
from datetime import datetime
from composants.FileUploader import display_file_uploader
from composants.ConfigManager import display_config_management
from composants.AvailableColumns import display_column_selection
from composants.DataPreview import display_data_preview
from composants.ChartSettings import display_visualization_settings
from composants.SaveConfiguration import display_save_configuration
from composants.Visualization import display_multi_response_processing
from composants.ThemeDisplay import display_theme_selection
from state_manager import initialize_session_state, reset_app_state

from data_processing import process_comparison_mode, process_stacked_mode, process_cross_analysis, process_3d_stacked
from visualization import create_bar_chart, create_stacked_bar_chart, create_centered_bar_chart, create_pie_chart, export_chart_as_image
from config import validate_config
from constants import CONFIG_DIR
import os
import pandas as pd

st.set_page_config(page_title="Analyse GPECT", layout="wide")


def main():
    load_global_styles()
    initialize_session_state()

    col_logo, col_gear = c.Columns([11, 1])
    with col_logo:
        c.Title("GPECTview", color="var(--primary-color)", align="center", size=70)
    with col_gear:
        with c.Popover("⚙️"):
            from themes import THEMES
            c.Title("Thèmes", align="center", margin="0px 0px 10px 0px")
            df = display_file_uploader()
            display_theme_selection()

    if df is not None:
        df = df.iloc[:, 3:] if df.shape[1] > 3 else df
        
        # Gestion des configurations (Sidebar)
        display_config_management(df)
        
        # Chargement de la configuration si sélectionnée ET pas déjà chargée
        if hasattr(st.session_state, "selected_config_file") and st.session_state.selected_config_file not in [None, "Aucune"]:
            if not st.session_state.get("config_loaded_once", False):
                import json
                config_path = os.path.join(CONFIG_DIR, st.session_state.selected_config_file)
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        loaded_config = json.load(f)
                    if "agg_func" in loaded_config:
                        del loaded_config["agg_func"]
                        with open(config_path, "w") as f2:
                            json.dump(loaded_config, f2, indent=4)
                    if "graph_type" in loaded_config:
                        st.session_state["graph_type"] = loaded_config["graph_type"]
                    compatible = validate_config(loaded_config, df)
                    if compatible:
                        with c.Sidebar():
                            c.Success(f"Configuration chargée.")
                        for key, value in loaded_config.items():
                            st.session_state[key] = value
                        for k in ["pivot_col_regroupement", "pivot_col_empilement", "pivot_col_valeur"]:
                            if k in loaded_config:
                                st.session_state[k] = loaded_config[k]
                        st.session_state.config_loaded_once = True
                        st.rerun() # On force le rerun pour appliquer les settings
                    else:
                        with c.Sidebar():
                            c.Error("❌ Configuration incompatible avec le fichier CSV chargé.")
                        loaded_config = {}

        # --- Barre d'actions (Popovers & Download) ---
        has_graph = st.session_state.get("current_fig") is not None
        
        col_act1, col_act2, col_act3, col_act4 = c.Columns([1, 1, 1, 1])
        
        with col_act1:
            with c.Popover("⚙️ Paramètres graphique"):
                settings = display_visualization_settings()
        
        with col_act2:
            with c.Popover("💾 Sauvegarder"):
                config_courant = {
                    "selected_columns": st.session_state.get("selected_columns", []), 
                    "start_row": st.session_state.get("start_row", 0), 
                    "end_row": st.session_state.get("end_row", 9)
                }
                if settings.get("graph_type") == "Graphe de synthèse croisée":
                    for k in ["pivot_col_regroupement", "pivot_col_empilement", "pivot_col_valeur"]:
                        config_courant[k] = st.session_state.get(k)
                if validate_config(config_courant, df):
                    display_save_configuration()
                else:
                    c.Warning("Sélectionnez les colonnes d'abord.")

        with col_act4:
            download_placeholder = st.empty()

        # --- Section de Configuration (Colonnes) & Aperçu ---
        with c.Expander("",expanded=not has_graph):
            col_pre, col_cfg = c.Columns([3, 1])
            with col_cfg:
                start_row, end_row = display_column_selection(df)
            with col_pre:
                selected_df_for_processing = display_data_preview(df, start_row, end_row)
            
        if selected_df_for_processing is None:
            return

        multi_response_df = display_multi_response_processing(selected_df_for_processing)
        
        # Le reste de la visualisation
        analysis_settings_container = c.Container()
        c.Subheader("📊 Visualisation")
        graph_container = c.Empty()
        
        label_df = None
        display_save_config = True

        with analysis_settings_container:
            if settings["graph_type"] == "Répartition croisée":
                df_ref = selected_df_for_processing
                all_cols = list(df_ref.columns)

                # --- Clés de session pour mémoriser les sélections ---
                saved_x     = st.session_state.get("rc_col_x")
                saved_color = st.session_state.get("rc_col_color")
                saved_val   = st.session_state.get("rc_col_value")

                # --- Classification des colonnes ---
                def is_year_like(series):
                    """True si toutes les valeurs non-nulles sont des entiers (pure digits)."""
                    s = series.dropna().astype(str).str.strip()
                    return s.str.fullmatch(r'\d+').all() and not s.empty

                num_cols  = df_ref.select_dtypes(include="number").columns.tolist()
                cat_cols  = df_ref.select_dtypes(include=["object", "category"]).columns.tolist()
                year_cols = [c_name for c_name in all_cols if is_year_like(df_ref[c_name])]

                # --- Exclure les colonnes déjà sélectionnées ---
                others_for_x     = {saved_color, saved_val} - {None}
                others_for_color = {saved_x, saved_val} - {None}
                others_for_val   = {saved_x, saved_color} - {None}

                x_opts     = [col for col in year_cols if col not in others_for_x]
                color_opts = [col for col in cat_cols  if col not in others_for_color]
                val_opts   = [col for col in num_cols  if col not in others_for_val]

                def safe_idx(lst, saved):
                    return (lst.index(saved) + 1) if saved in lst else 0

                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    sel_x = c.SelectBox(
                        "📅 Axe X — Année / Date",
                        ["-- Sélectionner --"] + x_opts,
                        index=safe_idx(x_opts, saved_x),
                        key="rc_col_x"
                    )
                with col_s2:
                    sel_color = c.SelectBox(
                        "🎨 Couleur / empilement",
                        ["-- Sélectionner --"] + color_opts,
                        index=safe_idx(color_opts, saved_color),
                        key="rc_col_color"
                    )
                with col_s3:
                    sel_val = c.SelectBox(
                        "🔢 Valeur numérique à sommer",
                        ["-- Sélectionner --"] + val_opts,
                        index=safe_idx(val_opts, saved_val),
                        key="rc_col_value"
                    )

                col_x_ok    = None if sel_x     == "-- Sélectionner --" else sel_x
                col_color_ok = None if sel_color == "-- Sélectionner --" else sel_color
                col_val_ok  = None if sel_val    == "-- Sélectionner --" else sel_val

                if col_x_ok and col_color_ok and col_val_ok:
                    label_df = process_3d_stacked(
                        df_ref, col_x_ok, col_color_ok, col_val_ok,
                        settings["display_as_percent"]
                    )
                else:
                    c.Info("📊 Sélectionnez les 3 colonnes pour générer le graphe.")

            elif settings["analysis_mode"] == "Comparaison multiple":
                label_df = process_comparison_mode(selected_df_for_processing, settings)
            elif settings["analysis_mode"] == "Empilement":
                label_df = process_stacked_mode(selected_df_for_processing, settings)
            else:
                label_df = process_cross_analysis(selected_df_for_processing, settings)

        use_multi_response = multi_response_df is not None
        if use_multi_response and settings["graph_type"] in ["Barres empilées", "Camembert"]:
            label_df = multi_response_df
            
        if label_df is not None and isinstance(label_df, pd.DataFrame) and settings.get("hide_zeros", False):
            if "Valeur" in label_df.columns:
                label_df = label_df[label_df["Valeur"] != 0]
                
        # Draw into the graphic container assigned above!
        if label_df is not None and isinstance(label_df, pd.DataFrame) and not label_df.empty:
            fig = None
            try:
                with c.Spinner("Génération..."):
                    show_legend = not use_multi_response
                    if settings["graph_type"] == "Barres":
                        fig = create_bar_chart(label_df, settings["graph_title"], settings["x_axis_label"], settings["y_axis_label"], settings["display_as_percent"], settings["invert_axes"], settings["palette"], show_legend=show_legend)
                    elif settings["graph_type"] == "Barres empilées":
                        if "Type" not in label_df.columns or label_df.empty:
                            with graph_container:
                                c.Error("❌ Barres empilées invalides avec les données choisies.")
                        else:
                            fig = create_stacked_bar_chart(label_df, settings["graph_title"], settings["x_axis_label"], settings["y_axis_label"], settings["display_as_percent"], settings["invert_axes"], settings["palette"])
                    elif settings["graph_type"] == "Barres centre":
                        fig = create_centered_bar_chart(label_df, settings["graph_title"], settings["x_axis_label"], settings["y_axis_label"], settings["display_as_percent"], settings["invert_axes"], settings["palette"], show_legend=show_legend)
                    elif settings["graph_type"] == "Camembert":
                        fig = create_pie_chart(label_df, settings["graph_title"], settings["palette"])
                        fig.update_traces(textinfo='label+percent' if settings["display_as_percent"] else 'label+value')
                    elif settings["graph_type"] == "Répartition croisée":
                        fig = create_stacked_bar_chart(label_df, settings["graph_title"], settings["x_axis_label"], settings["y_axis_label"], settings["display_as_percent"], settings["invert_axes"], settings["palette"])
                
                if fig is not None:
                    with graph_container:
                        c.PlotlyChart(fig, use_container_width=True)
                    st.session_state.current_fig = fig
                    st.session_state.graph_settings = settings
                    if settings["graph_type"] != "Scatter 3D":
                        img_bytes = export_chart_as_image(label_df=label_df, graph_type=settings["graph_type"], graph_title=settings["graph_title"], x_axis_label=settings["x_axis_label"], y_axis_label=settings["y_axis_label"], display_as_percent=settings["display_as_percent"], invert_axes=settings["invert_axes"], palette=settings["palette"], palette_name=settings["palette_name"])
                        if img_bytes:
                            st.session_state.img_bytes = img_bytes
                            with download_placeholder:
                                c.Button(label="📷 Télcharger l'image", data=img_bytes, file_name="graphique.png", mime="image/png")
            except Exception as e:
                with graph_container:
                    c.Error("❌ Paramètres actuels incompatibles avec le graphe : " + str(e))
                

        st.session_state.last_selected_columns = list(st.session_state.selected_columns)
    else:
        c.Info("👈 Veuillez uploader ou vérifier la page de paramètres pour charger un fichier de départ.")
if __name__ == '__main__':
    main()
