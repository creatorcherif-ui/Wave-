python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION DE LA BASE DE DONNÉES ---
DATABASE_NAME = 'candidats.db'

def init_db():
    """Initialise la base de données SQLite au démarrage de l'application"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telephone TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            date_inscription TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialiser la table au démarrage
init_db()


# --- ROUTES PRINCIPALES ---

@app.route('/')
def index():
    """Affiche la page d'accueil d'inscription Wave (index.html)"""
    return render_template('index.html')


@app.route('/api/inscription', methods=['POST'])
def inscription():
    """API recevant les inscriptions et coordonnées GPS du frontend"""
    try:
        data = request.get_json()
        
        telephone = data.get('telephone')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Validation des données reçues
        if not telephone or latitude is None or longitude is None:
            return jsonify({"status": "error", "message": "Données manquantes"}), 400

        # Insertion sécurisée en base de données
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO candidats (telephone, latitude, longitude, date_inscription)
            VALUES (?, ?, ?, ?)
        ''', (telephone, latitude, longitude, date_actuelle))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Données enregistrées !"})
        
    except Exception as e:
        print(f"Erreur d'inscription : {str(e)}")
        return jsonify({"status": "error", "message": "Erreur interne"}), 500


# --- ESPACE ADMINISTRATEUR ---

@app.route('/admin')
def admin_panel():
    """
    Tableau de bord de l'administrateur.
    Récupère les informations en BDD et affiche le fichier templates/admin.html
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Récupération de tous les candidats (du plus récent au plus ancien)
        cursor.execute('SELECT id, telephone, latitude, longitude, date_inscription FROM candidats ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        # Préparation des données pour l'affichage
        candidats = []
        for r in rows:
            # Lien d'itinéraire dynamique pour ouvrir directement l'application Google Maps
            link_gps = f"https://www.google.com/maps/dir/?api=1&destination={r[2]},{r[3]}"
            
            candidats.append({
                "id": r[0],
                "telephone": r[1],
                "latitude": r[2],
                "longitude": r[3],
                "date": r[4],
                "map_link": link_gps
            })
            
        # Chargement de l'interface graphique admin.html depuis le dossier templates
        return render_template('admin.html', candidats=candidats)
        
    except Exception as e:
        return f"Erreur lors de l'accès à l'administration : {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


