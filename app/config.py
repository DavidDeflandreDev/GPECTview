import os
import json
import shutil
import pandas as pd
from datetime import datetime
from constants import CONFIG_DIR

os.makedirs(CONFIG_DIR, exist_ok=True)

def validate_config(config, df):
    """Valide la compatibilité d'une configuration avec le DataFrame chargé (par noms de colonnes)."""
    selected_columns = config.get("selected_columns", [])
    if not all(col in df.columns for col in selected_columns):
        return False
    
    start_row = config.get("start_row")
    if start_row is None: start_row = 0
    end_row = config.get("end_row")
    if end_row is None: end_row = len(df) - 1
    
    if end_row >= len(df):
        end_row = len(df) - 1
        
    if not (0 <= start_row < len(df)) or not (0 <= end_row < len(df)) or start_row > end_row:
        return False
    return True

def save_config(config_name, config_data):
    """Sauvegarde une configuration dans un fichier JSON."""
    forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in config_name for char in forbidden_chars):
        raise ValueError("Le nom contient des caractères interdits: / \\ : * ? \" < > |")
    filename = f"{CONFIG_DIR}/{config_name}.json"
    with open(filename, "w") as f:
        json.dump(config_data, f, indent=4)
    return filename

def list_config_folders_and_files():
    """Retourne un dict dossier -> liste de fichiers de config (parcours récursif de configs/)."""
    folder_dict = {}
    for root, dirs, files in os.walk(CONFIG_DIR):
        rel_folder = os.path.relpath(root, CONFIG_DIR)
        if rel_folder == ".":
            rel_folder = "Sans dossier"
        folder_dict[rel_folder] = [f for f in files if f.endswith(".json") and f != "app_settings.json"]
    return folder_dict

def list_all_folders(base_dir=CONFIG_DIR):
    """Retourne une liste de tous les dossiers (relatifs à CONFIG_DIR), y compris les sous-dossiers, pour un selectbox."""
    folder_list = []
    for root, dirs, files in os.walk(base_dir):
        rel_folder = os.path.relpath(root, base_dir)
        if rel_folder == ".":
            folder_list.append("")  # Racine
        else:
            folder_list.append(rel_folder)
    return sorted(folder_list) 