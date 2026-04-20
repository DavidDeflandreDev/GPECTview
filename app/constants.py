from plotly.colors import qualitative, sequential
import os

PALETTE = qualitative.Plotly

PALETTES_DISPONIBLES = {
    "Plotly": qualitative.Plotly,
    "Viridis": sequential.Viridis,
    "Cividis": sequential.Cividis,
    "Dark24": qualitative.Dark24,
    # La clé 'MEPAG' sera traitée dynamiquement
    "MEPAG": None
}

import sys
import shutil

ORIGINAL_CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'configs'))

if sys.platform == 'emscripten':
    CONFIG_DIR = "/mnt/configs"
    os.makedirs(CONFIG_DIR, exist_ok=True)
    # Si le cache IndexedDB est vide (premier lancement), on y copie les modèles initiaux
    if not os.listdir(CONFIG_DIR) and os.path.exists(ORIGINAL_CONFIG_DIR):
        for item in os.listdir(ORIGINAL_CONFIG_DIR):
            s = os.path.join(ORIGINAL_CONFIG_DIR, item)
            d = os.path.join(CONFIG_DIR, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
else:
    CONFIG_DIR = ORIGINAL_CONFIG_DIR

APP_SETTINGS_FILE = os.path.join(CONFIG_DIR, "app_settings.json")


def get_mepag_palette(n):
    """Répartit n couleurs entre bleu, blanc, rouge, en commençant par les plus vives/foncées, puis vers le clair."""
    bleus = ["#0055A4", "#003366", "#6699CC", "#B3CCE6", "#E6F0FA"]  # vif/foncé -> clair
    blancs = ["#FFFFFF", "#D3D3D3", "#A9A9A9"]  # blanc pur -> gris
    rouges = ["#E2001A", "#B22234", "#F08080", "#F9D6D5", "#7A1C21"]  # vif/foncé -> clair
    familles = [bleus, blancs, rouges]
    n_fam = len(familles)
    base = n // n_fam
    reste = n % n_fam
    counts = [base] * n_fam
    for i in range(reste):
        counts[i] += 1
    palette = []
    for fam, count in zip(familles, counts):
        palette += fam[:count] if count <= len(fam) else fam + fam[:count-len(fam)]
    return palette[:n]

def get_palette(palette, n, palette_name=None):
    """
    Retourne une liste de n couleurs à partir d'une palette de base.
    - Pour MEPAG, utilise get_mepag_palette.
    - Pour les autres, cycle la palette si besoin.
    """
    if palette_name == "MEPAG" or palette is None:
        return get_mepag_palette(n)
    else:
        from itertools import cycle
        return [c for _, c in zip(range(n), cycle(palette))] 