# 📘 Manuel d'utilisation : Application d'analyse GPECT

## 1. 🎯 Mise en place de l'application

### ➤ Lancer l'application
Double-cliquez sur le fichier `GPECTview.vbs` ou `GPECTview.bat` (placé à la **racine** du projet) pour :
- Créer un environnement virtuel local si nécessaire.
- Installer automatiquement les dépendances.
- Lancer l'application Streamlit.

### ➤ Structure du projet recommandée :
```
GPECT/  
├── GPECTview.bat  
└── app/  
    ├── app.py  
    ├── requirements.txt  
    ├── venv/  
    └── configs/  
        ├── Dossier1/  
        │   ├── configA.json  
        │   └── configB.json  
        ├── Dossier2/  
        │   └── configC.json  
        └── configD.json  (non rangé)
```

> 📝 Organisez vos configurations dans des dossiers thématiques sous `configs/` (par client, étude, année, etc.).

## 2. 📦 Distribution / partage

Pour partager l'application :
- Placez tous les fichiers dans un dossier `GPECT`.
- Cliquez droit > **Envoyer vers > Dossier compressé (.zip)**.
- Envoyez le `.zip`.

Le destinataire n'aura qu'à extraire l'archive et double-cliquer sur `GPECTview.bat` pour le premier lancement, après il pourra utiliser `GPECTview.vbs`.

## 3. 📂 Récupérer le jeu de données

Un fichier d'exemple est fournis dans le dossier GPTECTview : `test.csv`

> ✅ **Astuce** : Depuis le Google Sheets du formulaire en ligne, faites **Fichier > Télécharger > Valeurs séparées par des virgules (.csv)**.

### 📌 Format attendu :
La première ligne doit contenir les noms des colonnes :
```
Raison sociale | Adresse postale de l'établissement | Téléphone  | Nombre de salariés
Entreprise A   | Gien                               | 0123456789 | 50
```

## 4. 🧭 Utilisation de l'application

### 1. **Importer un fichier**
Glissez-déposez un fichier `.csv`, ou utilisez le bouton "Parcourir".

> ⚠️ **Nouveau** : Si vous chargez un nouveau fichier CSV, toute la session (paramètres, configurations, sélections) est réinitialisée automatiquement pour éviter les conflits ou incohérences.

### 2. **Visualiser les colonnes**
Deux tableaux s'affichent :
- Liste des colonnes (avec leur nom exact, attention aux accents et espaces)
- Aperçu des données (premières lignes)

### 3. **Sélection des colonnes à analyser**
Sélectionnez directement les colonnes à inclure dans l'analyse via un multiselect. Plus de notion de plages d'indices.

### 4. **Sélection des lignes**
Spécifiez la plage de lignes à analyser (ex : ligne 0 à 2 pour 3 entreprises).

### 5. **Traitement des réponses multiples**
Si une colonne contient des réponses multiples séparées par des virgules, l'application propose de les éclater automatiquement pour une analyse plus fine (ex : "Compétences, Mobilité" → 2 valeurs distinctes).

## 5. ⚙️ Paramètres d'analyse et options de visualisation

### ➤ Types de graphiques disponibles
- **Barres** : Diagramme à barres classique (vertical ou horizontal)
- **Barres centre** : Barres centrées (pyramide des âges, barres partant du centre)
- **Camembert** : Diagramme circulaire (parts)
- **Barres empilées** : Barres superposées pour comparer plusieurs catégories ou valeurs

### ➤ Modes d'analyse
- **Comparaison multiple** : Compare plusieurs colonnes ou catégories entre elles (ex : répartition par tranches d'âge, par type de contrat, etc.)
- **Analyse croisée** : Croise deux variables (ex : répartition d'un type de contrat par secteur d'activité)
- **Empilement** : Pour les barres empilées, permet de visualiser la répartition de plusieurs valeurs numériques au sein de chaque catégorie

### ➤ Options de visualisation
- **Type de calcul** :
  - Somme (additionne les valeurs)
  - Moyenne
  - Médiane
- **Afficher en pourcentage** : Affiche les valeurs en % plutôt qu'en valeur brute
- **Inverser les axes X et Y** : Affiche les barres horizontalement (utile pour les pyramides ou longues légendes)
- **Palette de couleurs** : Choisissez parmi plusieurs palettes (Plotly, Viridis, Cividis, Dark24)
- **Gestion des valeurs manquantes (NaN)** :
  - Supprimer les lignes avec NaN
  - Remplacer les NaN par 0
- **Personnalisation des axes et du titre** :
  - Nom de l'axe X
  - Nom de l'axe Y
  - Titre du graphique

### ➤ Exemples concrets
- **Pyramide des âges** :
  - Type : Barres centre
  - Mode : Comparaison multiple
  - Axes inversés, affichage en %
  - Colonnes : tranches d'âge
- **Répartition des contrats par secteur** :
  - Type : Barres
  - Mode : Analyse croisée
  - Axe X : secteur, Axe Y : type de contrat
- **Répartition multi-contrats** :
  - Type : Barres empilées
  - Mode : Empilement
  - Catégorie : secteur, valeurs : différents types de contrats

## 6. 💾 Gestion des configurations (sauvegarde, import, adaptation)

### ➤ Organisation par dossiers
- Les configurations sont stockées dans des fichiers `.json` dans le dossier `configs/`.
- Vous pouvez créer des sous-dossiers pour organiser vos configurations par thème, client, année, etc.
- L'interface permet de créer, supprimer, déplacer des configurations et des dossiers.

### ➤ Exporter / sauvegarder une configuration
- Cliquez sur **Sauvegarder cette configuration** pour enregistrer vos réglages actuels dans un fichier `.json` dans le dossier de votre choix.
- Vous pouvez écraser une configuration existante ou en créer une nouvelle.

### ➤ Importer une configuration
- Cliquez sur le nom d'une configuration dans la sidebar pour la charger.
- Seules les configurations compatibles avec le CSV courant sont chargeables.

### ➤ Adapter une configuration incompatible
- Si une configuration n'est pas compatible avec le CSV (colonnes manquantes), un bouton **Adapter manuellement** apparaît.
- Cliquez dessus pour faire correspondre chaque colonne attendue à une colonne du CSV courant (ou choisir "Ignorer").
- La configuration sera alors adaptée et sauvegardée, y compris pour tous les champs dépendant des colonnes (analyses multiples, empilements, etc.).
- Cette fonctionnalité est idéale pour gérer les évolutions d'années ou de catégories dans vos jeux de données.

### ➤ Conseils sur la maintenance des configurations
- Si vos colonnes changent régulièrement (ex : années), utilisez l'adaptation manuelle pour mettre à jour vos configurations sans tout refaire.
- Organisez vos configurations dans des dossiers pour retrouver facilement vos analyses par projet ou par période.
- Supprimez les configurations obsolètes pour garder une interface claire.

### ➤ Suppression et déplacement
- Vous pouvez supprimer ou déplacer une configuration ou un dossier directement depuis la sidebar (icônes 🗑️ et Déplacer).
- Toute suppression ou déplacement réinitialise la sélection courante pour éviter les incohérences.

### ⚠️ Gestion des incompatibilités
- Si une configuration est incompatible (colonnes manquantes), elle est grisée et annotée dans la sidebar.
- Utilisez l'adaptation manuelle pour la rendre compatible avec le nouveau CSV.

### 📝 Astuce sur les intitulés et accents
- Les intitulés de colonnes dans les configurations doivent correspondre **exactement** à ceux du CSV (y compris accents, espaces, retours à la ligne cachés).
- Pour éviter les erreurs, copiez-collez les intitulés directement depuis le CSV ou utilisez un éditeur qui affiche les caractères cachés.

## 7. 📊 Génération et téléchargement des résultats

Vous pouvez ensuite **télécharger** :
- 📷 Un **fichier PNG** du graphique
- 📥 Un **fichier CSV** avec les données sélectionnées

## 8. 🔍 Exemple d'utilisation

- **Fichier** : `Questionnaire-V2.csv`  
- **Colonnes** : Tranches d'âge (ex : 2029, 2030, 2031)  
- **Lignes** : 0 à 1  
- **Mode** : Comparaison multiple  
- **Graphique** : Camembert  
- **Pourcentage** : ✅  
- **Titre** : *Répartition des profils sur le territoire*

## 9. 🛠 Dépendances techniques

Elles sont automatiquement installées via le fichier `.bat`.

Pour les installer manuellement :
```bash
pip install streamlit pandas plotly xlsxwriter
```

## 10. 🖥 Contenu du fichier GPECTview.bat

```
@echo off
cd /d %~dp0

:: Libérer le port 8501 si occupé
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8501" ^| find "LISTENING"') do (
    echo Port 8501 utilise par le PID %%a, tentative de fermeture...
    taskkill /PID %%a /F >nul 2>&1
)

:: Vérifie que python est installé
where python >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.x et l'ajouter au PATH.
    pause
    exit /b
)

:: Crée un environnement virtuel si besoin
if not exist "venv\Scripts\activate.bat" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

:: Active l'environnement virtuel
call venv\Scripts\activate.bat

:: Upgrade pip et installe les dependances
echo Installation des dependances...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

:: Lance l'application Streamlit
python -m streamlit run app.py

pause
```