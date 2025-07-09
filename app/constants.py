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

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'configs'))

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