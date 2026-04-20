import streamlit as st
import components as c
import pandas as pd
from utils import format_number

def display_data_preview(df, start_row, end_row):
    if not st.session_state.selected_columns:
        c.Info("Sélectionnez les données avant de les visualiser.")
        return None
    
    selected_df = df[st.session_state.selected_columns]
    selected_df_for_processing = selected_df.iloc[start_row:end_row + 1]
    
    # Fill NA before display/processing
    for col in selected_df_for_processing.columns:
        if pd.api.types.is_numeric_dtype(selected_df_for_processing[col]):
            selected_df_for_processing[col] = selected_df_for_processing[col].fillna(0)
        else:
            selected_df_for_processing[col] = selected_df_for_processing[col].fillna("")
            
    display_df = selected_df_for_processing.copy()
    for col in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].fillna(0).apply(format_number)
        elif display_df[col].dtype == object:
            display_df[col] = display_df[col].replace([None, float('nan'), 'nan'], '').fillna('')
            
    c.Subheader("👁️ Data Preview")
    c.DataFrame(display_df, height=700)
    
    csv_bytes = display_df.to_csv(index=False).encode('utf-8')
    c.Button(
        label="💾 Exporter ces lignes",
        data=csv_bytes,
        file_name="donnees_selectionnees.csv",
        mime="text/csv",
        help="Télécharge les données actuellement sélectionnées au format CSV."
    )
    return selected_df_for_processing
