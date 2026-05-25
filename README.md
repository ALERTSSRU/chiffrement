<div align="center">
  <h1>⚕️ MedVault Pro</h1>
  <p><strong>Plateforme de Stockage Médical Sécurisée — Chiffrement AES côté Serveur</strong></p>
  <br/>
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ecf8e?style=flat-square&logo=supabase" alt="Supabase">
  <img src="https://img.shields.io/badge/Chiffrement-AES--128--CBC%20%2B%20HMAC--SHA256-critical?style=flat-square" alt="Encryption">
  <img src="https://img.shields.io/badge/Encodage-Base64%20(Fernet)-orange?style=flat-square" alt="Base64">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=flat-square" alt="Status">
</div>

---

## 🎯 Description

**MedVault Pro** est une application web de stockage de dossiers médicaux sécurisée. Elle illustre comment un serveur backend peut chiffrer des données sensibles **avant** de les persister en base de données, garantissant qu'un accès direct à Supabase ne révèle aucune information lisible.

> **Contexte pédagogique :** Ce projet démontre les principes fondamentaux du chiffrement symétrique (AES), de l'encodage Base64, et de la sécurisation des données au repos (*data at rest encryption*).

---

## ✨ Fonctionnalités Clés

| Fonctionnalité | Description |
|---|---|
| 🔐 **Chiffrement AES côté serveur** | Le module Python `crypto.py` chiffre titre et contenu via **Fernet** (AES-128-CBC + HMAC-SHA256) avant l'insertion en base |
| 📄 **Encodage Base64** | Les données chiffrées sont stockées au format Base64 URL-safe — un standard d'encodage binaire-vers-texte |
| 🔬 **Inspecteur en temps réel** | L'onglet "Inspecteur" compare côte-à-côte ce que voit Supabase (Base64 chiffré) vs. ce que renvoie l'API (texte clair) |
| 🧪 **Génération de données de test** | Un bouton génère 3 dossiers médicaux réalistes en un clic pour la démonstration |
| ⚡ **Générateur d'ID aléatoire** | Démontre l'utilisation de `crypto.getRandomValues()` du navigateur pour générer des identifiants cryptographiquement sûrs |
| 🏥 **Affichage Dossier Médical** | Les documents déchiffrés s'affichent dans une fiche médicale stylisée avec tampon "TRÈS CONFIDENTIEL" |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NAVIGATEUR WEB                       │
│                   (index.html)                          │
│                                                         │
│  Formulaire → Données en CLAIR → Requête HTTP POST     │
└─────────────────────┬───────────────────────────────────┘
                      │ {title: "...", content: "..."}
                      ▼
┌─────────────────────────────────────────────────────────┐
│              SERVEUR FASTAPI (main.py)                  │
│                                                         │
│  1. Reçoit les données en clair                         │
│  2. Appelle ServerCrypto.encrypt_text() → crypto.py     │
│     ├── Fernet(MASTER_KEY).encrypt(data)                │
│     └── → Base64 URL-safe (ex: gAAAAABh...)             │
│  3. Envoie le texte chiffré à Supabase                  │
└─────────────────────┬───────────────────────────────────┘
                      │ {encrypted_title: "gAAAAABh...",
                      │  encrypted_content: "gAAAAABh..."}
                      ▼
┌─────────────────────────────────────────────────────────┐
│             SUPABASE (PostgreSQL)                       │
│                                                         │
│  Stocke uniquement des chaînes Base64 illisibles       │
│  → Accès direct à la DB = données incompréhensibles    │
└─────────────────────────────────────────────────────────┘
```

### Flux de Déchiffrement

```
Supabase → encrypted_title (Base64) → FastAPI
         → Fernet.decrypt() → texte clair
         → Réponse JSON lisible → Navigateur
```

---

## 🔑 Cryptographie Utilisée

### Fernet (librairie `cryptography`)

Fernet est une **implémentation de chiffrement symétrique authentifié** qui garantit :

- **Confidentialité** : AES-128 en mode CBC
- **Intégrité** : HMAC avec SHA-256 (protection contre l'altération)
- **Encodage** : Base64 URL-safe (pour stockage en base de données texte)

```python
# crypto.py — Exemple simplifié
from cryptography.fernet import Fernet

fernet = Fernet(MASTER_KEY)

# Chiffrement
cipher_b64 = fernet.encrypt(b"Bilan sanguin normal")
# → b'gAAAAABh5v3...longue_chaine_base64...'

# Déchiffrement
plain = fernet.decrypt(cipher_b64)
# → b'Bilan sanguin normal'
```

### Pourquoi Base64 ?

Base64 encode des données binaires (octets aléatoires du chiffrement) en caractères ASCII imprimables. C'est nécessaire pour stocker le résultat d'un algorithme de chiffrement dans une colonne `TEXT` d'une base de données PostgreSQL.

---

## 🚀 Installation

### Prérequis
- Python 3.10+
- Un projet [Supabase](https://supabase.com) actif

### 1. Cloner et installer
```bash
git clone https://github.com/ALERTSSRU/chiffrement.git
cd chiffrement
pip install -r requirements.txt
```

### 2. Configurer l'environnement
Créer un fichier `.env` :
```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=votre-cle-anon
ENCRYPTION_MASTER_KEY=votre-cle-fernet-base64-32-octets
```

> **Générer une clé Fernet :**
> ```python
> python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
> ```

### 3. Initialiser la base de données
Exécuter le fichier `migration.sql` dans le **SQL Editor** de votre projet Supabase.

### 4. Démarrer
```bash
python main.py
```
Ouvrir `http://127.0.0.1:8000` dans votre navigateur.

---

## 📁 Structure du Projet

```
chiffrement/
├── main.py           # API FastAPI (endpoints + logique chiffrement)
├── crypto.py         # Module ServerCrypto (Fernet/AES)
├── config.py         # Chargement et validation des variables d'environnement
├── database.py       # Client Supabase
├── schemas.py        # Schémas Pydantic (validation des données)
├── migration.sql     # Script SQL d'initialisation de la table
├── requirements.txt  # Dépendances Python
├── index.html        # Interface web complète (SPA)
└── .env              # Variables d'environnement (ne pas versionner)
```

---

## 🌐 Endpoints API

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Sert l'interface web |
| `POST` | `/api/documents` | Chiffre et sauvegarde un document |
| `GET` | `/api/documents` | Récupère et déchiffre les documents |
| `GET` | `/api/documents/raw` | **[Pédagogique]** Données brutes chiffrées (Base64) telles que stockées en DB |
| `GET` | `/api/users` | Liste les profils utilisateurs |

> Accéder à la documentation interactive : `http://127.0.0.1:8000/docs`

---

## 🔒 Conformité et Normes

- **AES (Advanced Encryption Standard)** : Standard NIST approuvé pour le chiffrement des données de santé (HIPAA, HDS)
- **HMAC-SHA256** : Assure l'intégrité des données (détection de toute altération)
- **Base64** : Encodage standard RFC 4648

---

## 📄 Licence

MIT — Voir le fichier [LICENSE](LICENSE)

---

<p align="center">
  <i>Projet réalisé dans le cadre d'un cours de cryptographie — ALIM ZATO // ALERTSSRU</i>
</p>
