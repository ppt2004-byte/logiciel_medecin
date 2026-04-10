# Logiciel Médical - Suivi Patient Pro

Application de gestion locale pour les cabinets médicaux, permettant la gestion des dossiers patients, la visualisation avec un tableau de bord et l'exportation vers Excel.

## 🛠 Prérequis et Base de Données
Ce projet **n'utilise aucun serveur de base de données externe** (ni MySQL ni MongoDB).
L'application s'appuie directement sur **SQLite** (intégré par défaut avec Python). 

Lors de l'exécution, les fichiers de la base de données (`patients.db` et `patients_archive.db`) seront créés ou lus automatiquement dans le répertoire `data/` local du projet. **Ainsi, pour faire fonctionner la base de données, vous n'avez absolument rien à installer de plus !**

> ⚠️ Attention : Les données médicales sont sensibles. Par défaut, si vous partagez le projet via GitHub, il est fortement conseillé de ne pas intégrer les fichiers `.db`.
> Assurez-vous d'ajouter `*.db` et `data/` dans un fichier `.gitignore`.

## 🚀 Comment démarrer l'application (Tutoriel complet)

### 1. Installation de Python et Tkinter
L'interface graphique s'appuie sur `Tkinter`. Assurez-vous que votre installation Python le supporte.
*(Sur Mac, si vous utilisez Homebrew, veillez à installer l'extension : `brew install python-tk@3.13` en l'adaptant à votre version).*

### 2. Configuration locale

Ouvrez un terminal, placez-vous dans le dossier de ce projet et créez un environnement virtuel afin d'installer les dépendances propement :
```bash
# 1. Création de l'environnement virtuel "venv"
python3 -m venv venv

# 2. Activation de l'environnement
# Sur macOS / Linux :
source venv/bin/activate
# Sur Windows :
# venv\Scripts\activate

# 3. Installation des dépendances (PyMongo n'est plus requis)
pip install -r requirements.txt
```

### 3. Lancement

Une fois l'environnement activé et les paquets installés, exécutez le point d'entrée principal :
```bash
python main.py
```

L'application va se lancer et se connectera automatiquement à un fichier `.db` local placé dans un dossier `/data`. Vos patients seront tous enregistrés là.
