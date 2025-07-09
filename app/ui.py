import streamlit as st
import pandas as pd
from config import list_config_folders_and_files, list_all_folders
from constants import PALETTE, PALETTES_DISPONIBLES, CONFIG_DIR
import json
import os
import shutil
import zipfile
import io
import json
from visualization import export_chart_as_image, create_bar_chart, create_stacked_bar_chart, create_centered_bar_chart, create_pie_chart
from config import validate_config

def display_file_uploader():
    # ... copier la fonction depuis app.py ...
    st.markdown("""
        <h1 style='text-align: center; color: #6C63FF;'>📊 Application d'analyse GPECT</h1>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📁 Choisissez un fichier CSV", type="csv", help="Le fichier doit contenir au moins une colonne de données.")
    if uploaded_file:
        if "last_uploaded_file" in st.session_state and st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.clear()
            st.rerun()
        try:
            with st.spinner("Chargement du fichier CSV..."):
                df = pd.read_csv(uploaded_file)
            df = df[[col for col in df.columns if 'unnamed' not in col.lower()]]
            if df.shape[1] < 1 or df.shape[0] < 1:
                st.error("❌ Le fichier CSV doit contenir au moins une colonne et une ligne de données.")
                return None
            st.success(f"✅ Fichier chargé avec {df.shape[0]} lignes et {df.shape[1]} colonnes.")
            st.session_state.raw_df = df  # <-- AJOUT ICI
            st.session_state.last_uploaded_file = uploaded_file.name
            return df
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier : {str(e)}")
            return None
    return None

def display_config_management(df=None):
    # ... copier la fonction depuis app.py ...
    st.sidebar.markdown("### 📂 Configurations (dossiers physiques)")
    folder_dict = list_config_folders_and_files()
    all_folders = list_all_folders()
    with st.sidebar.expander("➕ Créer un dossier", expanded=False):
        new_folder_name = st.text_input("Nom du nouveau dossier", key="nouveau_dossier")
        parent_folder = st.selectbox("Dans le dossier", all_folders, key="parent_folder_create")
        if st.button("Créer le dossier", key="btn_creer_dossier"):
            if new_folder_name.strip():
                new_folder_path = os.path.join(CONFIG_DIR, parent_folder, new_folder_name.strip())
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                    st.success(f"Dossier '{new_folder_name}' créé.")
                    st.rerun()
                else:
                    st.warning("Ce dossier existe déjà.")
    for folder in sorted(folder_dict.keys()):
        with st.sidebar.expander(f"📁 {folder}", expanded=True):
            for f in folder_dict[folder]:
                config_path = os.path.join(CONFIG_DIR, folder if folder != "Sans dossier" else "", f)
                try:
                    with open(config_path, "r") as cf:
                        config_data = json.load(cf)
                except Exception:
                    config_data = {}
                compatible = True
                missing_cols = []
                old_format = False
                if df is not None and config_data:
                    if "selected_columns" not in config_data:
                        compatible = False
                        old_format = True
                    else:
                        required_cols = config_data.get("selected_columns", [])
                        missing_cols = [col for col in required_cols if col not in df.columns]
                        compatible = (len(missing_cols) == 0)
                if st.session_state.get("confirm_delete_file") == (folder, f):
                    st.warning(f"⚠️ Êtes-vous sûr de vouloir supprimer le fichier **{f}** dans '{folder}' ?")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("✅ Oui, supprimer", key=f"confirm_delete_yes_{folder}_{f}"):
                            file_path = os.path.join(CONFIG_DIR, folder if folder != "Sans dossier" else "", f)
                            os.remove(file_path)
                            st.success(f"🗑️ Fichier supprimé : {f}")
                            for key in ["selected_columns", "start_row", "end_row", "selected_config_file", "config_loaded_once"]:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.session_state.confirm_delete_file = None
                            st.rerun()
                    with col_c2:
                        if st.button("❌ Annuler", key=f"confirm_delete_no_{folder}_{f}"):
                            st.session_state.confirm_delete_file = None
                            st.rerun()
                    continue
                col1, col2, col3 = st.columns([4, 1, 2])
                with col1:
                    if compatible:
                        if st.button(f"📄 {f}", key=f"load_{folder}_{f}"):
                            st.session_state.selected_config_file = os.path.join(folder, f) if folder != "Sans dossier" else f
                            st.session_state.config_loaded_once = False
                    else:
                        st.markdown(f"<span style='color:gray'>📄 {f}</span>", unsafe_allow_html=True)
                    if old_format:
                        st.caption("Incompatible (ancien format de configuration)")
                    elif missing_cols:
                        st.caption(f"Colonnes manquantes : {', '.join(missing_cols)}")
                    if not compatible and not old_format and df is not None:
                        adapt_key = f"adapt_manual_{folder}_{f}"
                        if st.button("Adapter manuellement", key=adapt_key):
                            st.session_state[f"show_adapt_{folder}_{f}"] = not st.session_state.get(f"show_adapt_{folder}_{f}", False)
                        if st.session_state.get(f"show_adapt_{folder}_{f}", False):
                            st.markdown("<b>Correspondance des colonnes :</b>", unsafe_allow_html=True)
                            config_cols = config_data.get("selected_columns", [])
                            csv_cols = list(df.columns)
                            mapping = {}
                            used_csv_cols = set()
                            for col in config_cols:
                                options = [c for c in csv_cols if c not in used_csv_cols]
                                options = ["Ignorer"] + options
                                default_idx = 0
                                try:
                                    col_int = int(col)
                                    closest = min((c for c in csv_cols if c not in used_csv_cols and c.isdigit()), key=lambda x: abs(int(x)-col_int), default=None)
                                    if closest:
                                        default_idx = options.index(closest)
                                except Exception:
                                    if col in options:
                                        default_idx = options.index(col)
                                mapping[col] = st.selectbox(f"{col} →", options, index=default_idx, key=f"map_{folder}_{f}_{col}")
                            if st.button("Valider l'adaptation", key=f"validate_adapt_{folder}_{f}"):
                                new_cols = [mapping[c] for c in config_cols if mapping[c] != "Ignorer"]
                                if not new_cols:
                                    st.error("Vous devez sélectionner au moins une colonne du CSV.")
                                else:
                                    config_data["selected_columns"] = new_cols
                                    if "value_cols_multiple" in config_data:
                                        config_data["value_cols_multiple"] = [mapping[c] for c in config_data["value_cols_multiple"] if c in mapping and mapping[c] != "Ignorer"]
                                    if "value_cols_stack" in config_data:
                                        config_data["value_cols_stack"] = [mapping[c] for c in config_data["value_cols_stack"] if c in mapping and mapping[c] != "Ignorer"]
                                    if "group_col_stack" in config_data:
                                        val = config_data["group_col_stack"]
                                        config_data["group_col_stack"] = mapping[val] if val in mapping and mapping[val] != "Ignorer" else None
                                    for key in ["col_x", "col_y"]:
                                        if key in config_data:
                                            val = config_data[key]
                                            config_data[key] = mapping[val] if val in mapping and mapping[val] != "Ignorer" else None
                                    try:
                                        with open(config_path, "w") as cf:
                                            json.dump(config_data, cf, indent=4)
                                        st.success(f"Configuration '{f}' adaptée et sauvegardée.")
                                        st.session_state[f"show_adapt_{folder}_{f}"] = False
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur lors de l'adaptation : {str(e)}")
                            if st.button("Annuler", key=f"cancel_adapt_{folder}_{f}"):
                                st.session_state[f"show_adapt_{folder}_{f}"] = False
                with col2:
                    if st.button("🗑️", key=f"ask_delete_{folder}_{f}"):
                        st.session_state.confirm_delete_file = (folder, f)
                        st.rerun()
                with col3:
                    move_key = f"move_{folder}_{f}"
                    if st.button("Déplacer", key=move_key):
                        st.session_state[f"show_move_{folder}_{f}"] = not st.session_state.get(f"show_move_{folder}_{f}", False)
                    if st.session_state.get(f"show_move_{folder}_{f}", False):
                        dest_folder = all_folders = list_all_folders()
                        dest_folder = st.selectbox(
                            "Déplacer vers...",
                            all_folders,
                            index=all_folders.index(folder if folder != "Sans dossier" else ""),
                            key=f"select_dest_{folder}_{f}"
                        )
                        if st.button("Confirmer le déplacement", key=f"confirm_move_{folder}_{f}"):
                            src_path = os.path.join(CONFIG_DIR, folder if folder != "Sans dossier" else "", f)
                            dest_path = os.path.join(CONFIG_DIR, dest_folder, f)
                            if os.path.abspath(src_path) == os.path.abspath(dest_path):
                                st.warning("Déjà dans ce dossier.")
                            elif os.path.exists(dest_path):
                                st.error("Un fichier du même nom existe déjà dans le dossier cible.")
                            else:
                                shutil.move(src_path, dest_path)
                                st.success(f"Configuration déplacée dans '{dest_folder or 'Sans dossier'}'.")
                                for key in ["selected_columns", "start_row", "end_row", "selected_config_file", "config_loaded_once"]:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                st.session_state[f"show_move_{folder}_{f}"] = False
                                st.rerun()
                        if st.button("Annuler", key=f"cancel_move_{folder}_{f}"):
                            st.session_state[f"show_move_{folder}_{f}"] = False

def display_column_selection(df):
    # ... copier la fonction depuis app.py ...
    col_left, col_right = st.columns([3, 1])
    with col_left:
        st.subheader("🔢 Colonnes disponibles")
        filtered_columns = [col for col in df.columns if 'Unamed' not in col]
        st.dataframe(pd.DataFrame({"Nom de colonne": filtered_columns}), height=200, width=1000)
        st.subheader("👁️ Aperçu des données")
        st.dataframe(df[filtered_columns], height=600, width=1000)
    with col_right:
        st.subheader("🎯 Sélection des colonnes à analyser")
        temp_selected_columns = st.multiselect(
            "Colonnes à inclure (choisissez puis validez)",
            options=filtered_columns,
            default=st.session_state.get("selected_columns", [])
        )
        if st.button("Valider la sélection des colonnes", key="valider_colonnes"):
            st.session_state.selected_columns = temp_selected_columns
            # Synchronisation des colonnes d'analyse avec la sélection principale
            for key in ["value_cols_multiple", "value_cols_stack"]:
                if key in st.session_state:
                    st.session_state[key] = [col for col in st.session_state[key] if col in temp_selected_columns]
            for key in ["col_x", "col_y"]:
                if key in st.session_state and st.session_state[key] not in temp_selected_columns:
                    st.session_state[key] = None
        st.markdown("---", unsafe_allow_html=True)
        st.subheader("📄 Sélection des lignes")
        max_row_index = len(df) - 1
        start_row = st.number_input("Ligne début", 0, max_row_index, value=st.session_state.get("start_row", 0))
        end_row = st.number_input("Ligne fin", start_row, max_row_index, value=st.session_state.get("end_row", max_row_index))
        if st.button("❌ Effacer la sélection", key="effacer_colonnes"):
            for key in ["selected_columns", "start_row", "end_row"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    return start_row, end_row

def display_visualization_settings():
    # ... copier la fonction depuis app.py ...
    with st.expander("🔧 Options"):
        graph_type_options = ["Barres", "Barres centre", "Camembert", "Barres empilées"]
        default_graph_type = st.session_state.get("graph_type", "Barres")
        default_graph_index = graph_type_options.index(default_graph_type) if default_graph_type in graph_type_options else 0
        graph_type = st.selectbox(
            "Type de graphique", 
            graph_type_options,
            index=default_graph_index,
            key="graph_type",
            help="Choisissez le type de graphique à afficher."
        )
        if graph_type == "Barres empilées":
            analysis_mode = "Empilement"
            st.markdown("**Mode d'analyse :** Empilement (fixé pour ce type de graphique)")
        else:
            analysis_mode_options = ["Comparaison multiple", "Analyse croisée"]
            default_analysis_mode = st.session_state.get("analysis_mode", "Comparaison multiple")
            default_analysis_index = analysis_mode_options.index(default_analysis_mode) if default_analysis_mode in analysis_mode_options else 0
            analysis_mode = st.radio(
                "Mode d'analyse",
                analysis_mode_options,
                index=default_analysis_index,
                key="analysis_mode",
                help="Comparaison de plusieurs colonnes ou analyse croisée entre deux variables."
            )
        agg_func_options = ["Somme", "Moyenne", "Médiane"]
        default_agg_func = st.session_state.get("agg_func", "Somme")
        default_agg_index = agg_func_options.index(default_agg_func) if default_agg_func in agg_func_options else 0
        agg_func = st.selectbox(
            "Type de calcul",
            options=agg_func_options,
            index=default_agg_index,
            key="agg_func",
            help="Fonction d'agrégation pour les colonnes numériques."
        )
        display_as_percent = st.checkbox(
            "Afficher en pourcentage",
            value=st.session_state.get("display_as_percent", False),
            key="display_as_percent",
            help="Affiche les valeurs en pourcentage plutôt qu'en valeur brute."
        )
        palette_name = st.selectbox(
            "Palette de couleurs",
            list(PALETTES_DISPONIBLES.keys()),
            index=list(PALETTES_DISPONIBLES.keys()).index(st.session_state.get("palette_name", "Plotly")),
            key="palette_name",
            help="Choisissez la palette de couleurs pour les graphiques."
        )
        palette = None if palette_name == "MEPAG" else PALETTES_DISPONIBLES[palette_name]
        x_axis_label = st.text_input(
            "Nom de l'axe horizontal (X)",
            value=st.session_state.get("x_axis_label", "Label"),
            key="x_axis_label",
            help="Nom affiché sous l'axe X du graphique."
        )
        y_axis_label = st.text_input(
            "Nom de l'axe vertical (Y)",
            value=st.session_state.get("y_axis_label", "Valeur"),
            key="y_axis_label",
            help="Nom affiché à gauche de l'axe Y du graphique."
        )
        invert_axes = st.checkbox(
            "Inverser les axes X et Y",
            value=st.session_state.get("invert_axes", False),
            key="invert_axes",
            help="Affiche les barres horizontalement au lieu de verticalement."
        )
        hide_zeros = st.checkbox(
            "Masquer les valeurs à zéro",
            value=st.session_state.get("hide_zeros", False),
            key="hide_zeros",
            help="Si coché, les valeurs à zéro ne seront pas affichées dans le graphique."
        )
    graph_title = st.text_input("Titre du graphe", value=st.session_state.get("graph_title", ""), key="graph_title", help="Titre affiché au-dessus du graphique.")
    return {
        "graph_type": graph_type,
        "analysis_mode": analysis_mode,
        "agg_func": agg_func,
        "display_as_percent": display_as_percent,
        "x_axis_label": x_axis_label,
        "y_axis_label": y_axis_label,
        "invert_axes": invert_axes,
        "graph_title": graph_title,
        "palette": palette,
        "palette_name": palette_name,
        "hide_zeros": hide_zeros
    }

def display_save_configuration():
    # ... copier la fonction depuis app.py ...
    all_folders = list_all_folders()
    col1, col2, col3 = st.columns([3, 1, 2])
    with col1:
        config_name_input = st.text_input(
            "Nom du fichier JSON de configuration (sans extension)",
            value=st.session_state.config_name
        )
        dossier_select = st.selectbox(
            "Dossier de configuration",
            options=all_folders,
            index=0,
            key="config_dossier_select"
        )
    with col2:
        st.write("")
        st.write("")
        if st.button("💾 Sauvegarder cette configuration", key="save_config_btn"):
            config_name_str = str(config_name_input).strip() if config_name_input else ""
            if not config_name_str:
                st.error("Veuillez entrer un nom valide pour la configuration")
            else:
                try:
                    config_to_save = {
                        "selected_columns": st.session_state.selected_columns,
                        "start_row": st.session_state.get("start_row", 0),
                        "end_row": st.session_state.get("end_row", 9),
                        "analysis_mode": st.session_state.get("analysis_mode", "Comparaison multiple"),
                        "graph_type": st.session_state.get("graph_type", "Barres"),
                        "agg_func": st.session_state.get("agg_func", "Somme"),
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
                        "hide_zeros": st.session_state.get("hide_zeros", False)
                    }
                    dossier_path = os.path.join(CONFIG_DIR, dossier_select)
                    if not os.path.exists(dossier_path):
                        os.makedirs(dossier_path)
                    file_path = os.path.join(dossier_path, f"{config_name_str}.json")
                    with open(file_path, "w") as f:
                        json.dump(config_to_save, f, indent=4)
                    st.success(f"✅ Configuration sauvegardée dans: {file_path}")
                    st.session_state.config_name = config_name_str
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
    with col3:
        st.markdown("<div style='height: 1.5em'></div>", unsafe_allow_html=True)
        if hasattr(st.session_state, "selected_config_file") and st.session_state.selected_config_file not in [None, "Aucune"]:
            if st.button("💾 Sauvegarder la configuration chargée", key="save_loaded_config_btn"):
                try:
                    config_to_save = {
                        "selected_columns": st.session_state.selected_columns,
                        "start_row": st.session_state.get("start_row", 0),
                        "end_row": st.session_state.get("end_row", 9),
                        "analysis_mode": st.session_state.get("analysis_mode", "Comparaison multiple"),
                        "graph_type": st.session_state.get("graph_type", "Barres"),
                        "agg_func": st.session_state.get("agg_func", "Somme"),
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
                        "hide_zeros": st.session_state.get("hide_zeros", False)
                    }
                    selected_file = st.session_state.selected_config_file
                    if os.sep in selected_file:
                        dossier, file_name = os.path.split(selected_file)
                        dossier_path = os.path.join(CONFIG_DIR, dossier)
                        file_path = os.path.join(dossier_path, file_name)
                    else:
                        file_path = os.path.join(CONFIG_DIR, selected_file)
                    with open(file_path, "w") as f:
                        json.dump(config_to_save, f, indent=4)
                    st.success(f"✅ Configuration existante écrasée : {file_path}")
                    st.session_state.config_name = os.path.splitext(os.path.basename(file_path))[0]
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
    # --- AJOUT : bouton de téléchargement PNG pour chaque dossier ---
    with st.sidebar:
        st.markdown("---")
        # Suppression de toute la logique d'export groupé automatique
        # (plus d'expander, plus de bouton de téléchargement zip, plus d'appels backend)

def display_multi_response_processing(selected_df):
    # Détection des colonnes à réponses multiples (texte) et numériques
    text_cols = [col for col in selected_df.columns if selected_df[col].dropna().astype(str).str.contains(",").any()]
    num_cols = [col for col in selected_df.columns if pd.api.types.is_numeric_dtype(selected_df[col])]

    if not text_cols or not num_cols:
        st.info("Il faut au moins une colonne à réponses multiples (texte) et une colonne numérique pour ce traitement.")
        return None

    st.subheader("🧪 Traitement des réponses multiples (catégorie + valeurs numériques)")
    col_categorie = st.selectbox(
        "Colonne de catégorie à exploser (ex: secteur d'activité)",
        options=text_cols,
        key="multi_categorie"
    )
    cols_numeriques = st.multiselect(
        "Colonnes numériques à sommer (ex: Nombre de CDI, Nombre de CDD)",
        options=num_cols,
        default=num_cols,
        key="multi_numeriques"
    )

    if not col_categorie or not cols_numeriques:
        return None

    # Explosion de la colonne catégorie avec répartition équitable
    exploded = selected_df[[col_categorie] + cols_numeriques].dropna(subset=[col_categorie])
    exploded[col_categorie] = exploded[col_categorie].astype(str)
    exploded["modalites"] = exploded[col_categorie].str.split(",")
    exploded["nb_modalites"] = exploded["modalites"].apply(len)
    for col in cols_numeriques:
        exploded[col] = exploded[col] / exploded["nb_modalites"]
    exploded = exploded.explode("modalites")
    exploded["modalites"] = exploded["modalites"].str.strip()
    AUTRE_VALUES = ["autre", "autres", "pas dans la liste..."]
    exploded = exploded[~exploded["modalites"].str.lower().isin(AUTRE_VALUES)]

    # Agrégation par modalité et colonne numérique
    melted = exploded.melt(id_vars=["modalites"], value_vars=cols_numeriques, var_name="Type", value_name="Valeur")
    melted = melted.dropna(subset=["Valeur"])
    melted["Valeur"] = pd.to_numeric(melted["Valeur"], errors="coerce")
    melted["Valeur"] = melted["Valeur"].fillna(0)
    label_df = melted.groupby(["modalites", "Type"], as_index=False)["Valeur"].sum()
    label_df = label_df.rename(columns={"modalites": "Label"})
    palette_len = len(PALETTE)
    label_df["Couleur"] = [PALETTE[i % palette_len] for i in range(len(label_df))]
    # Normalisation en pourcentage selon le type de graphique
    graph_type = st.session_state.get("graph_type", "Barres")
    if st.session_state.get("display_as_percent", False):
        if graph_type == "Barres empilées":
            label_df["Valeur"] = label_df.groupby("Label")["Valeur"].transform(lambda x: 100 * x / x.sum() if x.sum() else 0)
        else:
            total = label_df["Valeur"].sum()
            if total:
                label_df["Valeur"] = 100 * label_df["Valeur"] / total
            else:
                label_df["Valeur"] = 0
    st.markdown("✅ Agrégation effectuée. Prêt pour un graphique à barres empilées ou autre.")
    st.write(label_df)  # Pour debug, voir le DataFrame généré
    return label_df 