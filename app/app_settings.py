import json
import os
from constants import APP_SETTINGS_FILE

def load_settings():
    """Charge les paramètres de l'application depuis le fichier JSON."""
    if os.path.exists(APP_SETTINGS_FILE):
        try:
            with open(APP_SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    """Sauvegarde les paramètres de l'application dans le fichier JSON."""
    try:
        with open(APP_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des paramètres: {e}")

def get_setting(key, default=None):
    """Récupère une valeur spécifique des paramètres."""
    settings = load_settings()
    return settings.get(key, default)

def update_setting(key, value):
    """Met à jour une valeur spécifique des paramètres."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
