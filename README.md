# ⚕️ MedVault Pro

Plateforme de Stockage Médical Zéro-Connaissance — Chiffrement Côté Client

![Zero-Knowledge](https://img.shields.io/badge/Architecture-Z%C3%A9ro--Connaissance-8A2BE2?style=flat-square)
![Encryption](https://img.shields.io/badge/Chiffrement-AES--256--GCM%20(Client)-critical?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ecf8e?style=flat-square&logo=supabase)

---

## 🎯 Description

**MedVault Pro** est une application web de stockage de dossiers médicaux sécurisée implémentant une architecture **Zéro-Connaissance (Zero-Knowledge)**.

Le chiffrement est intégralement réalisé **côté client (dans le navigateur)** avant que les données ne soient transmises au serveur. L'API FastAPI et la base de données Supabase ne voient et ne stockent que des données chiffrées (Base64) et n'ont **absolument aucun moyen** de les déchiffrer.

> **Exigence du Projet :** Ce projet démontre comment concevoir une API REST qui stocke des documents médicaux où le contenu est chiffré côté client, garantissant qu'une compromission du serveur ne fuite aucune donnée patient en clair.

---

## ✨ Fonctionnalités Clés

| Fonctionnalité | Description |
| --- | --- |
| 🔐 **Chiffrement Côté Client (Web Crypto API)** | Le navigateur chiffre localement le titre et le contenu (AES-256-GCM) avant tout envoi réseau |
| 🔑 **Enveloppe Cryptographique (KEK/DEK)** | Utilisation d'une clé de chiffrement de clé (KEK) dérivée du mot de passe via SHA-256, protégeant une clé de données unique (DEK) par document |
| 📄 **Zéro-Connaissance** | L'API REST ne reçoit que des chaînes Base64 et n'a pas accès au mot de passe de l'utilisateur |
| 🔬 **Inspecteur de Déchiffrement Local** | Permet de visualiser le processus de dérivation (KEK), déchiffrement de clé (DEK), et déchiffrement des données localement |
| 🧪 **Générateur de Tests** | Génère automatiquement des clés et chiffre 3 dossiers de démonstration côté client pour remplir la base |

---

## 🏗️ Architecture Cryptographique (Web Crypto API)

```text
┌─────────────────────────────────────────────────────────┐
│               NAVIGATEUR WEB (Client)                   │
│                                                         │
│ 1. Saisie: Mot de passe + Titre + Contenu               │
│ 2. Dérivation KEK = SHA-256(Mot de passe)               │
│ 3. Génération DEK = 256 bits aléatoires                 │
│ 4. Chiffrement Titre/Contenu avec DEK (AES-GCM)         │
│ 5. Chiffrement DEK avec KEK (AES-GCM)                   │
│ 6. Envoi réseau POST /api/documents                     │
└─────────────────────┬───────────────────────────────────┘
                      │ (Données 100% chiffrées en Base64)
                      ▼
┌─────────────────────────────────────────────────────────┐
│              SERVEUR FASTAPI (Passe-plat)               │
│                                                         │
│ Ne fait QUE valider le format et stocker dans la DB.    │
│ Aucune opération cryptographique n'est faite ici.       │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│             SUPABASE (PostgreSQL)                       │
│                                                         │
│ Colonnes: encrypted_title, encrypted_content,           │
│           encrypted_dek                                 │
└─────────────────────────────────────────────────────────┘
```

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

Créer un fichier `.env` à la racine :

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=votre-cle-anon
```

### 3. Initialiser la base de données

Exécuter le fichier `migration.sql` dans le **SQL Editor** de votre projet Supabase.

### 4. Démarrer

```bash
python main.py
```

Ouvrir `http://127.0.0.1:8000` dans votre navigateur.

---

## 📁 Structure du Projet

```text
chiffrement/
├── main.py           # API FastAPI (Zéro-Connaissance, aucun chiffrement)
├── config.py         # Configuration (Variables d'environnement)
├── database.py       # Client Supabase
├── schemas.py        # Schémas Pydantic (validation des données chiffrées)
├── migration.sql     # Script SQL (Table public.medical_documents)
├── requirements.txt  # Dépendances Python
└── index.html        # Interface SPA (Contient toute la logique cryptographique)
```

---

## 🌐 Endpoints API

L'API est conçue pour être "stupide" et sécurisée : elle ne manipule que de la donnée opaque.

| Méthode | Route | Description |
| --- | --- | --- |
| `GET` | `/` | Sert l'interface web |
| `POST` | `/api/documents` | Reçoit et stocke un document chiffré (`encrypted_title`, `encrypted_content`, `encrypted_dek`) |
| `GET` | `/api/documents` | Renvoie la liste des documents chiffrés à l'utilisateur |

---

## 📄 Licence

MIT — Voir le fichier [LICENSE](LICENSE)

---

Projet réalisé dans le cadre d'un cours de cryptographie — ALIM ZATO // ALERTSSRU
