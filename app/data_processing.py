import pandas as pd
import streamlit as st
from constants import PALETTE

# --- AJOUT : fonction utilitaire pour filtrer les valeurs "autre", "autres", "pas dans la liste..." ---
import numpy as np

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
    if st.button("Valider la sélection des colonnes"):
        st.session_state.value_cols_multiple = temp_value
    value_cols_multiple = st.session_state.get("value_cols_multiple", [])
    if not value_cols_multiple:
        return None
    if len(value_cols_multiple) == 1:
        return process_single_column(selected_df, value_cols_multiple[0], settings["display_as_percent"])
    return process_multiple_columns(selected_df, value_cols_multiple, settings["agg_func"], settings["display_as_percent"])

def process_single_column(df, col_name, display_as_percent):
    df = filter_autre_values(df)  # AJOUT FILTRAGE
    col_series = df[col_name].dropna().astype(str).str.strip()
    if col_series.str.contains(",").any():
        col_series = col_series.str.split(",").explode().str.strip()
    vc = col_series.value_counts().reset_index()
    vc.columns = ["Label", "Valeur"]
    if display_as_percent:
        total = vc["Valeur"].sum()
        if total:
            vc["Valeur"] = vc["Valeur"] / total * 100
    vc["Couleur"] = PALETTE[:len(vc)]
    return vc

def process_multiple_columns(df, columns, agg_func, display_as_percent):
    df = filter_autre_values(df)  # AJOUT FILTRAGE
    agg_map = {
        "Somme": lambda x: x.sum(),
        "Moyenne": lambda x: x.mean(),
        "Médiane": lambda x: x.median(),
    }
    func = agg_map.get(agg_func, lambda x: x.sum())
    vals = []
    labels = []
    couleurs = []
    for i, col in enumerate(columns):
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            if isinstance(numeric_series, pd.Series):
                numeric_series = numeric_series.fillna(0)
            else:
                numeric_series = pd.Series([numeric_series]).fillna(0)
            val = func(numeric_series)
            vals.append(val)
            labels.append(col)
            couleurs.append(PALETTE[i % len(PALETTE)])
        else:
            vals.append(None)
            labels.append(col)
            couleurs.append(PALETTE[i % len(PALETTE)])
    total_val = sum(v for v in vals if v is not None)
    label_df_list = []
    for i, val in enumerate(vals):
        col = labels[i]
        couleur = couleurs[i]
        if val is not None:
            v = val
            if display_as_percent and total_val:
                v = val / total_val * 100
            label_df_list.append({"Label": col, "Valeur": v, "Couleur": couleur})
        else:
            col_series = df[col].dropna().astype(str).str.strip()
            if col_series.str.contains(",").any():
                col_series = col_series.str.split(",").explode().str.strip()
            vc = col_series.value_counts().reset_index()
            vc.columns = ["Label", "Valeur"]
            if display_as_percent:
                total = vc["Valeur"].sum()
                if total:
                    vc["Valeur"] = vc["Valeur"] / total * 100
            vc["Couleur"] = [couleur] * len(vc)
            label_df_list.append(vc)
    df_parts = []
    for item in label_df_list:
        if isinstance(item, dict):
            df_parts.append(pd.DataFrame([item]))
        else:
            df_parts.append(item)
    return pd.concat(df_parts, ignore_index=True) if df_parts else None

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
    if st.button("Valider la sélection des colonnes à empiler"):
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

    if settings["display_as_percent"]:
        df_melt = df_melt.groupby(col_group_stack).apply(
            lambda grp: grp.assign(Valeur=grp["Valeur"] / grp["Valeur"].sum() * 100)
        ).reset_index(drop=True)
    label_df = df_melt.rename(columns={col_group_stack: "Label"})
    label_df["Couleur"] = pd.Series(PALETTE).sample(n=len(label_df), replace=True).values
    unique_vals = selected_df[col_group_stack].dropna().unique()
    if len(unique_vals) == 1:
        st.error("Le graphique ne peut pas être généré car la colonne de regroupement ne contient qu'une seule valeur unique.")
        return None
    return label_df

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
    return grouped 

def process_comparison_mode_backend(selected_df, value_cols_multiple, agg_func, display_as_percent):
    selected_df = filter_autre_values(selected_df)
    if not value_cols_multiple:
        return None
    if len(value_cols_multiple) == 1:
        return process_single_column(selected_df, value_cols_multiple[0], display_as_percent)
    return process_multiple_columns(selected_df, value_cols_multiple, agg_func, display_as_percent)

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