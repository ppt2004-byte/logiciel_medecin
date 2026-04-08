import sqlite3
import os
import sys
from datetime import datetime, timedelta

def get_data_dir():
    # Détermine le dossier de données de l'application selon l'OS
    if sys.platform == 'darwin':
        # macOS
        base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    elif sys.platform == 'win32':
        # Windows
        base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        # Linux / autres
        base_dir = os.path.join(os.path.expanduser('~'), '.local', 'share')
        
    app_dir = os.path.join(base_dir, 'LogcielMedecin')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return app_dir

class Database:
    def __init__(self, db_name="patients.db", archive_db_name="patients_archive.db"):
        data_dir = get_data_dir()
        db_path = os.path.join(data_dir, db_name)
        archive_db_path = os.path.join(data_dir, archive_db_name)
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        self.archive_conn = sqlite3.connect(archive_db_path)
        self.archive_conn.row_factory = sqlite3.Row
        self.archive_cursor = self.archive_conn.cursor()
        
        self.create_table()
        self.create_archive_table()

    def create_archive_table(self):
        self.archive_cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_id INTEGER,
                nom TEXT,
                prenom TEXT,
                type_patient TEXT,
                moyen_paiement TEXT,
                date_enregistrement TEXT,
                action TEXT NOT NULL,
                annotation TEXT,
                date_action TEXT NOT NULL
            )
        ''')
        # Ajouter la colonne annotation si elle n'existe pas déjà (migration)
        self.archive_cursor.execute("PRAGMA table_info(patients_archive)")
        columns = [column[1] for column in self.archive_cursor.fetchall()]
        if 'annotation' not in columns:
            self.archive_cursor.execute("ALTER TABLE patients_archive ADD COLUMN annotation TEXT DEFAULT ''")
        self.archive_conn.commit()

    def _log_archive(self, original_id, nom, prenom, type_patient, moyen_paiement, date_enregistrement, action, annotation=""):
        date_action = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.archive_cursor.execute(
            "INSERT INTO patients_archive (original_id, nom, prenom, type_patient, moyen_paiement, date_enregistrement, action, annotation, date_action) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (original_id, nom, prenom, type_patient, moyen_paiement, date_enregistrement, action, annotation, date_action)
        )
        self.archive_conn.commit()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                type_patient TEXT NOT NULL,
                date_enregistrement TEXT NOT NULL
            )
        ''')
        self.cursor.execute("PRAGMA table_info(patients)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'moyen_paiement' not in columns:
            self.cursor.execute("ALTER TABLE patients ADD COLUMN moyen_paiement TEXT DEFAULT 'Non renseigné'")
        self.conn.commit()

    def add_patient(self, nom, prenom, type_patient, moyen_paiement):
        date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO patients (nom, prenom, type_patient, moyen_paiement, date_enregistrement) VALUES (?, ?, ?, ?, ?)",
            (nom, prenom, type_patient, moyen_paiement, date_actuelle)
        )
        self.conn.commit()
        patient_id = self.cursor.lastrowid
        self._log_archive(patient_id, nom, prenom, type_patient, moyen_paiement, date_actuelle, "AJOUT", "Dossier créé initialement")

    def update_patient(self, patient_id, nom, prenom, type_patient, moyen_paiement):
        self.cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        row = self.cursor.fetchone()
        
        if row:
            date_enregistrement = row['date_enregistrement']
            # Optionnel : On peut aussi logger l'état avant la modification
            self._log_archive(patient_id, row['nom'], row['prenom'], row['type_patient'], row['moyen_paiement'], date_enregistrement, "AVANT_MODIF", "Ancienne valeur avant modification")
        else:
            date_enregistrement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            "UPDATE patients SET nom=?, prenom=?, type_patient=?, moyen_paiement=? WHERE id=?",
            (nom, prenom, type_patient, moyen_paiement, patient_id)
        )
        self.conn.commit()
        self._log_archive(patient_id, nom, prenom, type_patient, moyen_paiement, date_enregistrement, "MODIFICATION", "Données modifiées dans la base initiale")

    def delete_patient(self, patient_id):
        self.cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        row = self.cursor.fetchone()
        if row:
            self._log_archive(patient_id, row['nom'], row['prenom'], row['type_patient'], row['moyen_paiement'], row['date_enregistrement'], "SUPPRESSION", "Dossier définitivement supprimé de la base initiale")

        self.cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        self.conn.commit()

    def _get_date_filter(self, filter_type):
        now = datetime.now()
        if filter_type == "Aujourd'hui":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif filter_type == "Cette Semaine":
            start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif filter_type == "Ce Mois":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif filter_type == "Cette Année":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return None
        return start.strftime("%Y-%m-%d %H:%M:%S")

    def get_patients(self, filter_type="Tout"):
        start_date_str = self._get_date_filter(filter_type)
        if start_date_str:
            self.cursor.execute("SELECT * FROM patients WHERE date_enregistrement >= ? ORDER BY date_enregistrement DESC", (start_date_str,))
        else:
            self.cursor.execute("SELECT * FROM patients ORDER BY date_enregistrement DESC")
            
        patients = []
        for row in self.cursor.fetchall():
            p = dict(row)
            p["date_enregistrement"] = datetime.strptime(p["date_enregistrement"], "%Y-%m-%d %H:%M:%S")
            patients.append(p)
        return patients

    def get_stats(self, filter_type="Tout"):
        start_date_str = self._get_date_filter(filter_type)
        
        if start_date_str:
            self.cursor.execute("SELECT COUNT(*) FROM patients WHERE date_enregistrement >= ?", (start_date_str,))
            total = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT type_patient as _id, COUNT(*) as count FROM patients WHERE date_enregistrement >= ? GROUP BY type_patient", (start_date_str,))
            stats_type = [dict(row) for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT moyen_paiement as _id, COUNT(*) as count FROM patients WHERE date_enregistrement >= ? GROUP BY moyen_paiement", (start_date_str,))
            stats_paiement = [dict(row) for row in self.cursor.fetchall()]
        else:
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            total = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT type_patient as _id, COUNT(*) as count FROM patients GROUP BY type_patient")
            stats_type = [dict(row) for row in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT moyen_paiement as _id, COUNT(*) as count FROM patients GROUP BY moyen_paiement")
            stats_paiement = [dict(row) for row in self.cursor.fetchall()]
            
        return total, stats_type, stats_paiement

    def get_paiement_details(self, filter_type="Tout"):
        start_date_str = self._get_date_filter(filter_type)
        if start_date_str:
            self.cursor.execute("SELECT moyen_paiement, type_patient, COUNT(*) as count FROM patients WHERE date_enregistrement >= ? GROUP BY moyen_paiement, type_patient", (start_date_str,))
        else:
            self.cursor.execute("SELECT moyen_paiement, type_patient, COUNT(*) as count FROM patients GROUP BY moyen_paiement, type_patient")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_raw_patients(self):
        self.cursor.execute("SELECT * FROM patients ORDER BY id ASC")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_raw_archive(self):
        self.archive_cursor.execute("SELECT * FROM patients_archive ORDER BY id ASC")
        return [dict(row) for row in self.archive_cursor.fetchall()]