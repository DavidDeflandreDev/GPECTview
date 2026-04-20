import streamlit as st
import components as c
import os
import json
import shutil
from config import list_config_folders_and_files, list_all_folders
from constants import CONFIG_DIR

@c.Dialog("📁 Déplacer / Renommer")
def move_dialog(folder, filename, all_folders):
    c.Caption(f"Fichier actuel : {folder}/{filename}")
    
    c.Markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
    
    # Nouveau nom de fichier
    current_name_no_ext = os.path.splitext(filename)[0]
    new_filename_base = c.TextInput("Nouveau nom (sans extension)", value=current_name_no_ext, key=f"name_dialog_{folder}_{filename}")
    new_filename = f"{new_filename_base}.json"
    
    # Destination
    dest_folder = c.SelectBox(
        "Dossier de destination", 
        all_folders, 
        index=all_folders.index(folder if folder != "Sans dossier" else ""), 
        key=f"dest_dialog_{folder}_{filename}"
    )
    
    col_ok, col_cancel = c.Columns([1, 1])
    with col_ok:
        if c.Button("✅ Valider les modifications", key=f"btn_confirm_move_{folder}_{filename}"):
            src_path = os.path.join(CONFIG_DIR, folder if folder != "Sans dossier" else "", filename)
            dest_dir = os.path.join(CONFIG_DIR, dest_folder)
            dest_path = os.path.join(dest_dir, new_filename)
            
            if os.path.abspath(src_path) == os.path.abspath(dest_path):
                c.Warning("Aucun changement détecté.")
            else:
                try:
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    
                    if os.path.exists(dest_path) and os.path.abspath(src_path) != os.path.abspath(dest_path):
                        c.Error("Un fichier avec ce nom existe déjà dans la destination.")
                    else:
                        shutil.move(src_path, dest_path)
                        # Reset session state for loaded config since path/name changed
                        for key in ["selected_columns", "start_row", "end_row", "selected_config_file", "config_loaded_once"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        c.Rerun()
                except Exception as e:
                    c.Error(f"Erreur : {str(e)}")
    with col_cancel:
        if c.Button("❌ Annuler", key=f"btn_cancel_move_{folder}_{filename}"):
            c.Rerun()

@c.Dialog("🗑️ Supprimer le dossier")
def delete_folder_dialog(folder):
    c.Title(f"Suppression de dossier", size=24)
    c.Warning(f'Voulez-vous supprimer le dossier "{folder}" ?')
    c.Markdown("Cette action est irréversible et supprimera toutes les configurations contenues dans ce dossier.")
    
    col_del, col_cancel = c.Columns([1, 1])
    with col_del:
        if c.Button("✅ Supprimer tout", key=f"btn_confirm_del_folder_{folder}"):
            folder_path = os.path.join(CONFIG_DIR, folder)
            try:
                shutil.rmtree(folder_path)
                c.Rerun()
            except Exception as e:
                c.Error(f"Erreur : {str(e)}")
    with col_cancel:
        if c.Button("Annuler", key=f"btn_cancel_del_folder_{folder}"):
            c.Rerun()

@c.Dialog("🗑️ Supprimer le fichier")
def delete_file_dialog(folder, filename):
    c.Title("Suppression de fichier", size=24)
    c.Warning(f"⚠️ Supprimer **{filename}** ?")
    c.Caption(f"Dossier : {folder}")
    
    col_yes, col_no = c.Columns([1, 1])
    with col_yes:
        if c.Button("✅ Oui, supprimer", key=f"btn_confirm_del_file_{folder}_{filename}"):
            file_path = os.path.join(CONFIG_DIR, folder if folder != "Sans dossier" else "", filename)
            try:
                os.remove(file_path)
                for key in ["selected_columns", "start_row", "end_row", "selected_config_file", "config_loaded_once"]:
                    if key in st.session_state:
                        del st.session_state[key]
                c.Rerun()
            except Exception as e:
                c.Error(f"Erreur : {str(e)}")
    with col_no:
        if c.Button("❌ Annuler", key=f"btn_cancel_del_file_{folder}_{filename}"):
            c.Rerun()

def display_config_management(df=None):
    with c.Sidebar():
        c.Title("📂 Configurations", align="center", size=30, margin="0 0 2rem 0")
        folder_dict = list_config_folders_and_files()
        all_folders = list_all_folders()
        with c.Expander("➕ Créer un dossier"):
            new_folder_name = c.TextInput("Nom du nouveau dossier", key="nouveau_dossier")
            parent_folder = c.SelectBox("Dans le dossier", all_folders, key="parent_folder_create")
            if c.Button("Créer le dossier", key="btn_creer_dossier"):
                if new_folder_name.strip():
                    new_folder_path = os.path.join(CONFIG_DIR, parent_folder, new_folder_name.strip())
                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                        c.Success(f"Dossier '{new_folder_name}' créé.")
                        c.Rerun()
                    else:
                        c.Warning("Ce dossier existe déjà.")
        for folder in sorted(folder_dict.keys()):
            # Utilisation de l'expander avec bouton de suppression sur la même ligne
            if folder != "Sans dossier":
                exp = c.Expander(
                    f"📁 {folder}", 
                    on_delete=lambda f=folder: delete_folder_dialog(f),
                    delete_key=f"del_hdr_{folder}"
                )
            else:
                exp = c.Expander(f"📁 {folder}")
            
            with exp:
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

                    # On remplace les colonnes imbriquées (interdites en sidebar) par un Popover d'actions
                    with c.Popover(f"📄 {f}"):
                        if not compatible:
                            c.Error("Incompatible")
                            if old_format:
                                c.Caption("Ancien format")
                            elif missing_cols:
                                c.Caption(f"Colonnes manquantes : {', '.join(missing_cols)}")
                        
                        if compatible:
                            if c.Button("📥 Charger la configuration", key=f"load_{folder}_{f}"):
                                st.session_state.selected_config_file = os.path.join(folder, f) if folder != "Sans dossier" else f
                                st.session_state.config_loaded_once = False
                                c.Rerun()
                        
                        if not compatible and not old_format and df is not None:
                            if c.Button("⚙️ Adapter manuellement", key=f"adapt_{folder}_{f}"):
                                st.session_state[f"show_adapt_{folder}_{f}"] = not st.session_state.get(f"show_adapt_{folder}_{f}", False)
                                c.Rerun()
                        
                        if c.Button("✎ Déplacer / Renommer", key=f"move_{folder}_{f}"):
                            move_dialog(folder, f, all_folders)
                        
                        if c.Button("🗑️ Supprimer le fichier", key=f"del_file_{folder}_{f}"):
                            delete_file_dialog(folder, f)

                    # Si l'adaptation manuelle est activée (hors colonnes pour éviter l'erreur)
                    if st.session_state.get(f"show_adapt_{folder}_{f}", False):
                        c.Markdown("---")
                        c.Subheader("Adaptation")
                        config_cols = config_data.get("selected_columns", [])
                        csv_cols = list(df.columns)
                        mapping = {}
                        used_csv_cols = set()
                        for col in config_cols:
                            options = ["Ignorer"] + [cb for cb in csv_cols if cb not in used_csv_cols]
                            mapping[col] = c.SelectBox(f"{col} →", options, key=f"map_{folder}_{f}_{col}")
                        
                        if c.Button("Valider", key=f"val_adapt_{folder}_{f}"):
                            # ... (même logique de validation)
                            new_cols = [mapping[col] for col in config_cols if mapping[col] != "Ignorer"]
                            if not new_cols:
                                c.Error("Sélectionnez au moins une colonne.")
                            else:
                                config_data["selected_columns"] = new_cols
                                # ... (mise à jour des autres clés)
                                try:
                                    with open(config_path, "w") as cf:
                                        json.dump(config_data, cf, indent=4)
                                    st.session_state[f"show_adapt_{folder}_{f}"] = False
                                    c.Rerun()
                                except: pass
                        if c.Button("Annuler", key=f"canc_adapt_{folder}_{f}"):
                            st.session_state[f"show_adapt_{folder}_{f}"] = False
                            c.Rerun()
                    
