```python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION DE LA BASE DE DONNÉES ---
DATABASE_NAME = 'candidats.db'

def init_db():
    """Initialise la base de données et crée la table candidats si elle n'existe pas"""
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

# Initialiser la table au démarrage de l'application
init_db()


# --- ROUTES PRINCIPALES ---

@app.route('/')
def index():
    """Affiche la page d'accueil d'inscription Wave"""
    return render_template('index.html')


@app.route('/api/inscription', methods=['POST'])
def inscription():
    """API recevant les inscriptions du frontend et les stockant en BDD"""
    try:
        data = request.get_json()
        
        # Récupération des données du payload JSON
        telephone = data.get('telephone')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not telephone or latitude is None or longitude is None:
            return jsonify({"status": "error", "message": "Champs manquants"}), 400

        # Connexion à la BDD et insertion des données
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO candidats (telephone, latitude, longitude, date_inscription)
            VALUES (?, ?, ?, ?)
        ''', (telephone, latitude, longitude, date_actuelle))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Candidat enregistré avec succès !"})
        
    except Exception as e:
        print(f"Erreur lors de l'inscription : {str(e)}")
        return jsonify({"status": "error", "message": "Erreur interne du serveur"}), 500


# --- ESPACE ADMINISTRATEUR (SECRET) ---

@app.route('/admin')
def admin_panel():
    """
    Tableau de bord administrateur affichant tous les assistants inscrits
    avec un lien direct vers Google Maps pour chacun !
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Récupération de tous les candidats enregistrés
        cursor.execute('SELECT id, telephone, latitude, longitude, date_inscription FROM candidats ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        # Formatage des données pour l'affichage HTML
        candidats = []
        for r in rows:
            candidats.append({
                "id": r[0],
                "telephone": r[1],
                "latitude": r[2],
                "longitude": r[3],
                "date": r[4],
                # Génération dynamique du lien Google Maps
                "map_link": f"https://www.google.com/maps?q={r[2]},{r[3]}"
            })
            
        # Code HTML direct et élégant pour le panneau d'administration
        admin_html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin - Gestion des Assistants Wave</title>
            <style>
                body { font-family: -apple-system, sans-serif; background-color: #f7f9fa; padding: 30px; color: #333; }
                .container { max-width: 1000px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
                h1 { color: #39bcf4; margin-bottom: 5px; font-size: 28px; }
                p.subtitle { color: #666; margin-bottom: 30px; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th, td { padding: 14px; text-align: left; border-bottom: 1px solid #eee; }
                th { background-color: #f1f8ff; color: #333; font-weight: 600; }
                tr:hover { background-color: #fafafa; }
                .btn-map { background-color: #39bcf4; color: white; padding: 8px 15px; text-decoration: none; border-radius: 20px; font-size: 13px; font-weight: 500; display: inline-block; box-shadow: 0 2px 5px rgba(57,188,244,0.3); }
                .btn-map:hover { background-color: #29abe2; }
                .badge { background-color: #e1f5fe; color: #0288d1; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Panneau Administrateur</h1>
                <p class="subtitle">Liste des assistants inscrits et leurs coordonnées de géolocalisation.</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Téléphone</th>
                            <th>Date d'inscription</th>
                            <th>Coordonnées (Lat, Lng)</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if candidats %}
                            {% for c in candidats %}
                            <tr>
                                <td>{{ c.id }}</td>
                                <td><span class="badge">{{ c.telephone }}</span></td>
                                <td>{{ c.date }}</td>
                                <td>{{ c.latitude }}, {{ c.longitude }}</td>
                                <td>
                                    <a href="{{ c.map_link }}" target="_blank" class="btn-map">📍 Voir sur Google Maps</a>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="5" style="text-align: center; color: #999; padding: 30px;">Aucun candidat enregistré pour le moment.</td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # On utilise le moteur de template natif de Flask pour charger la page d'administration
        from flask import render_template_string
        return render_template_string(admin_html, candidats=candidats)
        
    except Exception as e:
        return f"Erreur lors du chargement de l'administration : {str(e)}", 500


if __name__ == '__main__':
    # Lancement du serveur sur le port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

```
