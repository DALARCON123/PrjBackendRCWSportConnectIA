# 🌱 Seeder - Mock Data SportConnectIA

Ce dossier contient tous les scripts et données mockées pour initialiser la base de données de l'application **SportConnectIA**.

## 📁 Structure

```
seed/
├── seeder.py                    # Script principal de seeding
├── users_data.py               # Données des utilisateurs (Auth Service)
├── notifications_data.py       # Données des notifications (Auth Service)
├── coach_users_data.py         # Utilisateurs du coach IA (Chatbot Service)
├── interactions_data.py        # Historique interactions coach (Chatbot Service)
├── meal_plans_data.py          # Plans alimentaires (Chatbot Service)
├── meal_logs_data.py           # Journaux alimentaires (Chatbot Service)
├── tracking_data.py            # Mesures corporelles (MongoDB)
├── mongodb_data.py             # Profils et recommandations (MongoDB)
└── README.md                   # Cette documentation
```

## 🚀 Utilisation

### Prérequis

1. **PostgreSQL** doit être en cours d'exécution (obligatoire pour Auth et Chatbot)
2. **MongoDB** doit être en cours d'exécution (obligatoire pour Tracking/Métriques et Recommandations)
3. Les variables d'environnement doivent être configurées dans `.env`
4. Les dépendances Python doivent être installées: `pip install -r requirements.txt`

### Commandes disponibles

#### Popule toutes les bases de données

```powershell
python seed/seeder.py --all
```

#### Popule uniquement Auth Service (PostgreSQL)

```powershell
python seed/seeder.py --auth
```

#### Popule uniquement Chatbot Service (PostgreSQL)

```powershell
python seed/seeder.py --chatbot
```

#### Popule uniquement Tracking/Métriques (MongoDB)

```powershell
python seed/seeder.py --tracking
```

#### Popule uniquement MongoDB

```powershell
python seed/seeder.py --mongodb
```

#### Supprime les données existantes avant seeding

```powershell
python seed/seeder.py --all --clear
```

## 👥 Utilisateurs de test

### Auth Service

| ID  | Nom            | Email                      | Mot de passe  | Rôle           |
| --- | -------------- | -------------------------- | ------------- | -------------- |
| 1   | Marie Dubois   | marie.dubois@example.com   | `password123` | Admin          |
| 2   | Jean Martin    | jean.martin@example.com    | `sport2024`   | User           |
| 3   | Sophie Laurent | sophie.laurent@example.com | `fitness123`  | User           |
| 4   | Pierre Dupont  | pierre.dupont@example.com  | `running2024` | User           |
| 5   | Julie Bertrand | julie.bertrand@example.com | `yoga2024`    | User           |
| 6   | Lucas Silva    | lucas.silva@example.com    | `admin123`    | Admin          |
| 7   | Emma Wilson    | emma.wilson@example.com    | `wellness123` | User (inactif) |
| 8   | Thomas Bernard | thomas.bernard@example.com | `strength123` | User           |

**Note:** Tous les mots de passe sont hashés avec bcrypt. Les mots de passe en clair sont indiqués en commentaire dans `users_data.py`.

## 📊 Données incluses

### Auth Service (PostgreSQL)

- **8 utilisateurs** avec profils variés
- **7 notifications** pour tester le système de notifications
- 2 admins pour tester les permissions

### Chatbot Service (PostgreSQL)

- **5 utilisateurs coach** avec profils détaillés (JSON)
- **6 interactions** avec historique questions/réponses
- **3 plans alimentaires** hebdomadaires personnalisés
- **13 logs alimentaires** sur plusieurs jours

### Tracking/Métriques Service (MongoDB)

- **18 mesures corporelles** pour 5 utilisateurs
- Suivi sur plusieurs semaines montrant l'évolution
- Données des capteurs et métriques de santé

### MongoDB (Users et Recommandations)

- **6 profils utilisateurs** avec objectifs fitness
- **3 recommandations IA** historiques complètes
- Données prêtes pour le système de recommandations

**Note:** Les données de tracking sont également dans MongoDB (collection `health_metrics`)

## 🔧 Personnalisation

Pour ajouter vos propres données mockées:

1. Ouvrez le fichier correspondant (ex: `users_data.py`)
2. Ajoutez vos données en suivant la structure existante
3. Exécutez le seeder avec l'option appropriée

### Exemple - Ajouter un utilisateur

```python
# Dans seed/users_data.py
{
    "id": 9,
    "name": "Nouveau User",
    "email": "nouveau@example.com",
    "password_hash": "$2b$12$...",  # Mot de passe: monmotdepasse
    "is_active": True,
    "is_admin": False,
    "created_at": datetime(2024, 12, 1, 10, 0, 0)
}
```

## 🔐 Génération de hash bcrypt

Pour générer un nouveau hash bcrypt pour un mot de passe:

```python
import bcrypt

password = "monmotdepasse"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
```

## ⚠️ Avertissements

- **IMPORTANT:** N'utilisez jamais ces données en production!
- Les mots de passe sont mockés et ne doivent servir qu'au développement
- Utilisez `--clear` avec précaution: cela supprime toutes les données existantes
- Assurez-vous que les services sont arrêtés avant de faire un seeding avec `--clear`

## 🐛 Dépannage

### Erreur: `ModuleNotFoundError: No module named 'dotenv'`

**Solution:** Installez les dépendances nécessaires:

```powershell
pip install python-dotenv sqlalchemy psycopg2 pymongo
```

Ou installez toutes les dépendances du projet:

```powershell
pip install -r requirements.txt
```

### Erreur: `ModuleNotFoundError: No module named 'services'`

**Solution:** Exécutez le script depuis la racine du projet:

```powershell
python seed/seeder.py --all
```

### Erreur: `psycopg2.OperationalError: could not connect`

**Solution:** Vérifiez que PostgreSQL est lancé et que les credentials dans `.env` sont corrects.

### Avertissement: `MongoDB n'est pas accessible`

**Important!** MongoDB est obligatoire pour le projet.

**Solutions:**

- Démarrez MongoDB avec la commande appropriée pour votre système
- Vérifiez que `MONGODB_URI` est correctement configuré dans `.env`
- Si vous voulez uniquement tester Auth et Chatbot: `python seed/seeder.py --auth --chatbot`

### Erreur: Tables déjà existantes avec données

**Solution:** Utilisez l'option `--clear`:

```powershell
python seed/seeder.py --all --clear
```

## 📝 Notes de développement

- Les dates sont en format `datetime` Python
- Les profils coach sont stockés en JSON string dans PostgreSQL
- MongoDB stocke les dates en format UTC
- MongoDB utilise des collections: `users`, `recommendations`, `health_metrics`
- Les IDs PostgreSQL sont auto-incrémentés
- Les IDs MongoDB utilisent `_id` personnalisé ou ObjectId

## 🔄 Mise à jour des données

Pour mettre à jour les données existantes:

1. Exécutez avec `--clear` pour supprimer les anciennes données
2. Modifiez les fichiers de données
3. Relancez le seeder

```powershell
python seed/seeder.py --all --clear
```

## 📞 Support

Pour toute question ou problème avec le seeding, contactez l'équipe de développement.

---

**Version:** 1.0.0  
**Dernière mise à jour:** Novembre 2024
