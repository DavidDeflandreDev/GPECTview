import streamlit as st
import components as c
import pandas as pd

def display_column_selection(df):
    c.Subheader("🎯 Configuration")
    
    filtered_columns = [col for col in df.columns if 'Unnamed' not in col and 'Unamed' not in col]
    
    c.Caption("Sélectionnez les colonnes à inclure")
    
    # Barre de recherche pour les colonnes
    search_query = c.TextInput("🔍 Rechercher une colonne", key="col_search").lower()
    
    # Conteneur scrollable pour les cases à cocher avec auto-update
    # Nettoyage des colonnes sélectionnées (si elles n'existent plus dans le nouveau fichier)
    if "selected_columns" not in st.session_state:
        st.session_state.selected_columns = []
    
    st.session_state.selected_columns = [col for col in st.session_state.selected_columns if col in filtered_columns]
    current_sel = st.session_state.selected_columns
    current_sel_set = set(current_sel)
    
    # Filtrage des colonnes selon la recherche
    visible_columns = [col for col in sorted(filtered_columns) if search_query in col.lower()]
    
    with c.ScrollContainer(300):
        # On ne boucle que sur les colonnes visibles
        for col in visible_columns:
            is_checked = col in current_sel_set
            # Utilisation de on_change pour une mise à jour immédiate et propre
            def on_chk_change(c_name=col):
                if f"chk_{c_name}" in st.session_state:
                    val = st.session_state[f"chk_{c_name}"]
                    curr = st.session_state.get("selected_columns", [])
                    if val and c_name not in curr:
                        st.session_state.selected_columns.append(c_name)
                    elif not val and c_name in curr:
                        st.session_state.selected_columns.remove(c_name)
                    # Cleanup after change
                    for key in ["value_cols_multiple", "value_cols_stack"]:
                        if key in st.session_state:
                            st.session_state[key] = [c_n for c_n in st.session_state[key] if c_n in st.session_state.selected_columns]
                    for key in ["col_x", "col_y", "pivot_col_regroupement", "pivot_col_empilement", "pivot_col_valeur"]:
                        if key in st.session_state and st.session_state[key] not in st.session_state.selected_columns:
                            st.session_state[key] = None

            c.Checkbox(col, value=is_checked, key=f"chk_{col}", on_change=on_chk_change)
    
    # Information sur le nombre de colonnes sélectionnées (hors vue si filtré)
    total_sel = len(current_sel)
    if search_query and total_sel > 0:
        c.Caption(f"💡 {total_sel} colonne(s) sélectionnée(s) au total")

    # Boutons rapides
    col_b1, col_b2 = c.Columns([1, 1])
    with col_b1:
        if c.Button("✨ Tout", key="tout_selectionner", style="secondary", sizeX="100%"):
            # Si recherche active, on ajoute seulement les colonnes visibles
            current = set(st.session_state.get("selected_columns", []))
            for c_name in visible_columns:
                current.add(c_name)
            st.session_state.selected_columns = list(current)
            c.Rerun()
    with col_b2:
        if c.Button("❌ Aucun", key="effacer_colonnes", style="secondary", sizeX="100%"):
            # Si recherche active, on retire seulement les colonnes visibles
            current = set(st.session_state.get("selected_columns", []))
            for c_name in visible_columns:
                if c_name in current:
                    current.remove(c_name)
            st.session_state.selected_columns = list(current)
            c.Rerun()

    c.Bar()
    # Section Sélection des Lignes
    c.Markdown("##### 📄 Plage de données")
    max_row_index = max(0, len(df) - 1)
    
    # Sécurisation des valeurs pour éviter le crash StreamlitValueAboveMaxError
    # On s'assure que les valeurs en session state ne dépassent pas le nouveau max_row_index
    current_start = st.session_state.get("start_row", 0)
    current_end = st.session_state.get("end_row", max_row_index)
    
    if current_start > max_row_index:
        current_start = 0
    if current_end > max_row_index:
        current_end = max_row_index
    if current_start > current_end:
        current_start = 0

    # Forcer la mise à jour des clés des widgets pour éviter l'erreur de décalage
    st.session_state["start_row_input"] = current_start
    st.session_state["end_row_input"] = current_end

    col_r1, col_r2 = c.Columns([1, 1])
    with col_r1:
        start_row = c.NumberInput("Début", 0, max_row_index, value=current_start, key="start_row_input")
    with col_r2:
        end_row = c.NumberInput("Fin", start_row, max_row_index, value=current_end, key="end_row_input")
    
    st.session_state.start_row = start_row
    st.session_state.end_row = end_row

    return start_row, end_row
