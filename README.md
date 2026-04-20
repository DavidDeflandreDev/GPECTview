# 🛠️ GPECTview — Documentation Développeur

**GPECTview** est une application hybride Python/JavaScript permettant de générer des analyses statistiques complexes (Pandas/Plotly) au sein d'un environnement de bureau autonome (Electron).

---

## 🏛️ Architecture Technique

L'application repose sur le socle **Stlite**, une implémentation de Streamlit basée sur **Pyodide** (Python compilé en WebAssembly). Cela permet d'exécuter l'intégralité de la logique de calcul sur le poste client sans serveur Python.

### Structure du projet
*   `app/` : Source Python de l'application.
    *   `gpectview_app.py` : Entrée principale et orchestration.
    *   `components.py` : Bibliothèque de composants UI stylisés (wrapper Streamlit).
    *   `data_processing.py` : Logique métier (agrégations, 3D Crosstab, filtres).
    *   `visualization.py` : Moteur de rendu graphique (Plotly).
    *   `style/` : Fichiers CSS injectés dynamiquement selon les thèmes.
*   `package.json` : Configuration Electron et dépendances Pyodide.
*   `configs/` : Stockage persistant des profils d'analyse utilisateur.
*   `fix_tar.py` / `patch.py` : Scripts de post-installation pour la compatibilité Windows.

---

## 🚀 Développement & Compilation

### Prérequis
*   Node.js (LTS recommandé)
*   Python 3.11+
*   Pip (pour les tests locaux)

### Commandes utiles (Scripts NPM)
| Commande | Action | Cas d'usage |
|---|---|---|
| `npm run serve` | Lancement local | Développement et tests en temps réel. |
| `npm run dump` | Préparation Pyodide | Requis après changement de librairies Python. |
| `npm run dist` | Packaging final | Génère l'exécutable `.exe` dans `dist/`. |

---

## 🎨 Système de Thèmes et Stylisation

L'application utilise un système de thèmes dynamiques défini dans `app/themes.py`.
Les styles sont injectés via `app/style_loader.py` et s'appuient sur des variables CSS (`:root`) pour assurer la cohérence entre les composants Streamlit natifs et les composants personnalisés.

**Fichiers CSS clés :**
*   `main.css` : Mise en page globale, sidebar et popovers.
*   `buttons.css` : Design des boutons et états hover.
*   `inputs.css` : Champs de saisie, selects et radios.
*   `tables.css` : Rendu du DataPreview et des tableaux HTML.

---

## 📂 Gestion des Données
*   **Persistance** : Le dernier fichier ouvert est mémorisé dans `app/last_file.csv`.
*   **Configurations** : Les réglages sont exportés en JSON dans `app/configs/`. Le chargement vérifie la compatibilité des colonnes via `app/config.py`.

---

## 🧪 Tests et Maintenance
Pour tester la logique de données sans l'interface, utilisez les scripts dans le dossier de développement ou lancez Streamlit directement :
`streamlit run app/gpectview_app.py`