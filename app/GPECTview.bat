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
python -m pip install -r ../requirements.txt

:: Lance l'application Streamlit (version modulaire)
python -m streamlit run main.py

pause