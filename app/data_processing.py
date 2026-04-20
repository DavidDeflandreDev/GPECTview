import pandas as pd
import streamlit as st
from constants import PALETTE
import numpy as np


def process_3d_stacked(df, col_x, col_color, col_value, display_as_percent):
    """
    Analyse 3D pour barres empilées :
    - col_x     : colonne de regroupement axe X (ex: Année, numérique ou texte)
    - col_color : colonne de la dimension couleur/empilement (ex: Métier, catégoriel)
    - col_value : colonne numérique dont on somme les valeurs
    Retourne un DataFrame Label/Type/Valeur pour create_stacked_bar_chart.
    """
    df = filter_autre_values(df)
    for col in [col_x, col_color, col_value]:
        if col not in df.columns:
            st.error(f"Colonne introuvable : '{col}'")
            return None
    if not pd.api.types.is_numeric_dtype(df[col_value]):
        st.error(f"La colonne '{col_value}' doit être numérique.")
        return None

    work = df[[col_x, col_color, col_value]].copy()
    work[col_value] = pd.to_numeric(work[col_value], errors="coerce").fillna(0)
    work[col_x] = work[col_x].astype(str).str.strip()
    work[col_color] = work[col_color].astype(str).str.strip()
    work = work[(work[col_x] != "") & (work[col_color] != "")]

    grouped = work.groupby([col_x, col_color])[col_value].sum().reset_index()
    grouped.columns = ["Label", "Type", "Valeur"]

    if display_as_percent:
        totals = grouped.groupby("Label")["Valeur"].transform("sum")
        grouped["Valeur"] = (grouped["Valeur"] / totals * 100).where(totals > 0, 0)

    return grouped[["Label", "Type", "Valeur"]]

def filter_autre_values(df):
    AUTRE_VALUES = ["autre", "autres", "pas dans la liste..."]
    def is_autre(val):
        if isinstance(val, str):
            return val.strip().lower() in AUTRE_VALUES
        return False
    df_filtered = df.copy()
    for col in df_filtered.columns:
        if pd.api.types.is_numeric_dtype(df_filtered[col]):
            # Si la colonne est numérique, remplacer les valeurs texte "autre"... par 0
            df_filtered[col] = df_filtered[col].apply(lambda x: 0 if is_autre(x) else x)
        else:
            # Si la colonne est texte, retirer les lignes où la valeur (après passage en minuscules) est "autre"... (on retire toute la ligne si une colonne contient la valeur)
            mask = ~df_filtered[col].astype(str).str.strip().str.lower().isin(AUTRE_VALUES)
            df_filtered = df_filtered[mask]
    return df_filtered.reset_index(drop=True)

# --- FIN AJOUT ---

def process_comparison_mode(selected_df, settings):
    selected_df = filter_autre_values(selected_df)  # AJOUT FILTRAGE
    options = list(selected_df.columns)
    value_cols_multiple = st.session_state.get("value_cols_multiple", [])
    temp_value = st.multiselect(
        "Colonnes à analyser",
        options,
        default=value_cols_multiple
    )
    if st.button("Valider la sélection des colonnes", key="valider_colonnes_comparaison"):
        st.session_state.value_cols_multiple = temp_value
    value_cols_multiple = st.session_state.get("value_cols_multiple", [])
    if not value_cols_multiple:
        return None
    if len(value_cols_multiple) == 1:
        return process_single_column(selected_df, value_cols_multiple[0], settings["display_as_percent"])
    return process_multiple_columns(selected_df, value_cols_multiple, settings["display_as_percent"])

def process_single_column(df, col_name, display_as_percent):
    df = filter_autre_values(df)  # AJOUT FILTRAGE
    col_series = df[col_name].dropna().astype(str).str.strip()
    col_series = col_series[col_series != ""]  # Filtrer les vides
    if col_series.str.contains(",").any():
        col_series = col_series.str.split(",").explode().str.strip()
        col_series = col_series[col_series != ""]  # Filtrer les vides après explosion
    vc = col_series.value_counts().reset_index()
    vc.columns = ["Label", "Valeur"]
    if display_as_percent:
        total = vc["Valeur"].sum()
        if total:
            vc["Valeur"] = vc["Valeur"] / total * 100
    vc["Couleur"] = PALETTE[:len(vc)]
    return vc

def process_multiple_columns(df, columns, display_as_percent):
    import streamlit as st
    from itertools import cycle
    df = filter_autre_values(df)
    label_df_list = []
    numeric_items = []  # On stocke les items numériques pour calculer le % global après

    for i, col in enumerate(columns):
        if col not in df.columns:
            st.warning(f"Colonne '{col}' absente du DataFrame, ignorée.")
            continue
        couleur = PALETTE[i % len(PALETTE)]
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            if not isinstance(numeric_series, pd.Series):
                numeric_series = pd.Series([numeric_series])
            numeric_series = numeric_series.fillna(0)
            if numeric_series.empty:
                st.warning(f"Colonne numérique '{col}' vide, ignorée.")
                continue
            val = numeric_series.sum()
            # On stocke la valeur brute, le % sera calculé après avec le total global
            numeric_items.append({"Label": col, "Valeur": val, "Couleur": couleur})
        else:
            col_series = df[col].dropna().astype(str).str.strip()
            col_series = col_series[col_series != ""]
            if col_series.empty:
                st.warning(f"Colonne texte '{col}' vide, ignorée.")
                continue
            if col_series.str.contains(",").any():
                col_series = col_series.str.split(",").explode().str.strip()
                col_series = col_series[col_series != ""]
            vc = col_series.value_counts().reset_index()
            vc.columns = ["Label", "Valeur"]
            if display_as_percent:
                # Pour les colonnes texte, le % est relatif aux occurrences de cette colonne
                total = vc["Valeur"].sum()
                if total:
                    vc["Valeur"] = vc["Valeur"] / total * 100
            n_modalites = len(vc)
            if n_modalites > len(PALETTE):
                st.error(f"Erreur : pas assez de couleurs dans la palette ({len(PALETTE)}) pour toutes les valeurs à afficher ({n_modalites}). Veuillez choisir une palette plus grande ou réduire le nombre de modalités.")
                continue
            vc["Couleur"] = [PALETTE[j % len(PALETTE)] for j in range(n_modalites)]
            if not vc.empty:
                label_df_list.append(vc)

    # Calcul du pourcentage pour les colonnes numériques (relatif au total global)
    if numeric_items:
        if display_as_percent:
            grand_total = sum(item["Valeur"] for item in numeric_items)
            for item in numeric_items:
                item["Valeur"] = (item["Valeur"] / grand_total * 100) if grand_total else 0
        label_df_list.extend([pd.DataFrame([item]) for item in numeric_items])

    if not label_df_list:
        st.error("Aucune donnée exploitable pour la comparaison multiple (toutes les colonnes sont vides ou invalides).")
        return None
    try:
        result = pd.concat(label_df_list, ignore_index=True)
        if result.empty:
            st.error("Le DataFrame final de comparaison multiple est vide.")
            return None
        return result
    except Exception as e:
        st.error(f"Erreur lors de la concaténation des résultats : {e}")
        return None

def process_stacked_mode(selected_df, settings):
    selected_df = filter_autre_values(selected_df)  # AJOUT FILTRAGE
    cat_options = selected_df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_options:
        st.warning("Aucune colonne catégorielle disponible pour le regroupement.")
        return None
    default_group = st.session_state.get("group_col_stack")
    col_group_stack = st.selectbox(
        "Colonne de regroupement (catégories)", 
        cat_options, 
        index=cat_options.index(default_group) if default_group in cat_options else 0,
        key="group_col_stack"
    )
    num_options = selected_df.select_dtypes(include=["number"]).columns.tolist()
    value_cols_stack = st.session_state.get("value_cols_stack", [])
    temp_value_stack = st.multiselect(
        "Colonnes numériques à empiler", 
        num_options, 
        default=value_cols_stack
    )
    if st.button("Valider la sélection des colonnes à empiler", key="valider_colonnes_empilement"):
        st.session_state.value_cols_stack = temp_value_stack
    value_cols_stack = st.session_state.get("value_cols_stack", [])
    if not col_group_stack or not value_cols_stack:
        return None
    df_plot = selected_df[[col_group_stack] + value_cols_stack].dropna()
    df_melt = df_plot.melt(
        id_vars=col_group_stack,
        value_vars=value_cols_stack,
        var_name="Type",
        value_name="Valeur"
    )
    df_melt["Valeur"] = pd.to_numeric(df_melt["Valeur"], errors="coerce")
    df_melt = df_melt.dropna(subset=["Valeur"])

    # Agrégation par regroupement + type
    df_melt = df_melt.groupby([col_group_stack, "Type"], as_index=False)["Valeur"].sum()
    df_melt = df_melt.rename(columns={col_group_stack: "Label"})
    # Normalisation à 100% si affichage en pourcentage
    if settings.get("display_as_percent", False):
        df_melt["Valeur"] = df_melt.groupby("Label")["Valeur"].transform(lambda x: 100 * x / x.sum() if x.sum() else 0)
    df_melt["Couleur"] = pd.Series(PALETTE).sample(n=len(df_melt), replace=True).values
    unique_vals = selected_df[col_group_stack].dropna().unique()
    if len(unique_vals) == 1:
        st.error("Le graphique ne peut pas être généré car la colonne de regroupement ne contient qu'une seule valeur unique.")
        return None
    return df_melt

def process_cross_analysis(selected_df, settings):
    selected_df = filter_autre_values(selected_df)  # AJOUT FILTRAGE
    col_x_val = st.session_state.get("col_x")
    if col_x_val not in selected_df.columns:
        col_x_val = selected_df.columns[0]
    col_y_val = st.session_state.get("col_y")
    if col_y_val not in selected_df.columns or col_y_val == col_x_val:
        possible_cols = [col for col in selected_df.columns if col != col_x_val]
        col_y_val = possible_cols[0] if possible_cols else col_x_val
    col_x = st.selectbox(
        "Catégories", 
        selected_df.columns, 
        index=selected_df.columns.get_loc(col_x_val),
        key="col_x"
    )
    cols_for_col_y = [col for col in selected_df.columns if col != col_x]
    col_y = st.selectbox(
        "Valeurs", 
        cols_for_col_y, 
        index=cols_for_col_y.index(col_y_val) if col_y_val in cols_for_col_y else 0,
        key="col_y"
    )
    if not col_x or not col_y:
        return None
    label_df = selected_df[[col_x, col_y]].copy()
    label_df[col_y] = pd.to_numeric(label_df[col_y], errors="coerce")
    label_df = label_df.dropna(subset=[col_y])
    if label_df.empty:
        st.warning(f"Aucune donnée exploitable dans '{col_x}' et '{col_y}' pour l'analyse croisée.")
        return None
    grouped = label_df.groupby(col_x)[col_y].sum().reset_index()
    if settings["display_as_percent"]:
        total = grouped[col_y].sum()
        if total:
            grouped[col_y] = grouped[col_y] / total * 100
    grouped.columns = ["Label", "Valeur"]
    # Suppression du filtrage des barres à 0 : on affiche toutes les catégories
    return grouped 

def process_comparison_mode_backend(selected_df, value_cols_multiple, display_as_percent):
    selected_df = filter_autre_values(selected_df)
    if not value_cols_multiple:
        return None
    if len(value_cols_multiple) == 1:
        return process_single_column(selected_df, value_cols_multiple[0], display_as_percent)
    return process_multiple_columns(selected_df, value_cols_multiple, display_as_percent)

def process_stacked_mode_backend(selected_df, group_col_stack, value_cols_stack, display_as_percent):
    selected_df = filter_autre_values(selected_df)
    if not group_col_stack or not value_cols_stack:
        return None
    if group_col_stack not in selected_df.columns:
        return None
    for col in value_cols_stack:
        if col not in selected_df.columns:
            return None
    df = selected_df.copy()
    # --- Traitement avancé des réponses multiples (répartition équitable) ---
    if df[group_col_stack].astype(str).str.contains(',').any():
        df[group_col_stack] = df[group_col_stack].astype(str)
        df["modalites"] = df[group_col_stack].str.split(',')
        df["nb_modalites"] = df["modalites"].apply(len)
        for col in value_cols_stack:
            df[col] = df[col] / df["nb_modalites"]
        df = df.explode("modalites")
        df["modalites"] = df["modalites"].str.strip()
        group_col = "modalites"
    else:
        group_col = group_col_stack
    df_plot = df[[group_col] + value_cols_stack].dropna()
    df_melt = df_plot.melt(
        id_vars=group_col,
        value_vars=value_cols_stack,
        var_name="Type",
        value_name="Valeur"
    )
    df_melt["Valeur"] = pd.to_numeric(df_melt["Valeur"], errors="coerce")
    df_melt = df_melt.dropna(subset=["Valeur"])
    # Agrégation par regroupement + type
    df_melt = df_melt.groupby([group_col, "Type"], as_index=False)["Valeur"].sum()
    if display_as_percent:
        df_melt = df_melt.groupby(group_col).apply(
            lambda grp: grp.assign(Valeur=grp["Valeur"] / grp["Valeur"].sum() * 100)
        ).reset_index(drop=True)
    label_df = df_melt.rename(columns={group_col: "Label"})
    label_df["Couleur"] = PALETTE[:len(label_df)]
    return label_df

def process_cross_analysis_backend(selected_df, col_x, col_y, display_as_percent):
    selected_df = filter_autre_values(selected_df)
    if col_x not in selected_df.columns or col_y not in selected_df.columns or col_x == col_y:
        return None
    label_df = selected_df[[col_x, col_y]].copy()
    label_df[col_y] = pd.to_numeric(label_df[col_y], errors="coerce")
    label_df = label_df.dropna(subset=[col_y])
    if label_df.empty:
        return None
    grouped = label_df.groupby(col_x)[col_y].sum().reset_index()
    if display_as_percent:
        total = grouped[col_y].sum()
        if total:
            grouped[col_y] = grouped[col_y] / total * 100
    grouped.columns = ["Label", "Valeur"]
    grouped["Couleur"] = PALETTE[:len(grouped)]
    return grouped 