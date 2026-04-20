import streamlit as st
import pandas as pd
from constants import PALETTE

def display_multi_response_processing(selected_df):
    text_cols = [col for col in selected_df.columns if selected_df[col].dropna().astype(str).str.contains(",").any()]
    num_cols = [col for col in selected_df.columns if pd.api.types.is_numeric_dtype(selected_df[col])]
    if not text_cols or not num_cols:
        return None
    col_categorie = text_cols[0]
    cols_numeriques = num_cols
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
    melted = exploded.melt(id_vars=["modalites"], value_vars=cols_numeriques, var_name="Type", value_name="Valeur")
    melted = melted.dropna(subset=["Valeur"])
    melted["Valeur"] = pd.to_numeric(melted["Valeur"], errors="coerce")
    melted["Valeur"] = melted["Valeur"].fillna(0)
    label_df = melted.groupby(["modalites", "Type"], as_index=False)["Valeur"].sum()
    label_df = label_df.rename(columns={"modalites": "Label"})
    palette_len = len(PALETTE)
    label_df["Couleur"] = [PALETTE[i % palette_len] for i in range(len(label_df))]
    
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
    return label_df
