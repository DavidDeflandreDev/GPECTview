import os
import pandas as pd
import streamlit as st
import components as c
from state_manager import reset_app_state

def display_file_uploader():
    last_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "last_file.csv")
    test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test.csv")
    
    c.Subheader("Charger les données")
    uploaded_file = c.FileUploader("Veuillez sélectionner un fichier CSV", type="csv")
    
    df = None
    if uploaded_file:
        try:
            # Détection de changement de fichier pour réinitialiser l'état proprement
            if st.session_state.get("last_uploaded_file_name") != uploaded_file.name:
                reset_app_state()
                st.session_state.last_uploaded_file_name = uploaded_file.name

            with c.Spinner("Chargement et sauvegarde du fichier CSV..."):
                file_bytes = uploaded_file.getvalue()
                with open(last_file_path, "wb") as f:
                    f.write(file_bytes)
                df = pd.read_csv(last_file_path)
            st.session_state.last_uploaded_file = uploaded_file.name
            c.Toast("Fichier sauvegardé et chargé (sera ouvert par défaut)!", icon="💾")
        except Exception as e:
            c.Error(f"Erreur lors du chargement : {str(e)}")
            return None
    else:
        # Load local persist
        if os.path.exists(last_file_path):
            df = pd.read_csv(last_file_path)
            st.session_state.last_uploaded_file = "last_file.csv"
        elif os.path.exists(test_file_path):
            try:
                df = pd.read_csv(test_file_path)
                st.session_state.last_uploaded_file = "test.csv"
            except:
                pass
                
    if df is not None:
        df = df[[col for col in df.columns if 'unnamed' not in col.lower()]]
        if df.shape[1] < 1 or df.shape[0] < 1:
            c.Error("Le fichier CSV fourni est vide ou invalide.")
            return None
        st.session_state.raw_df = df
        return df
    return None
