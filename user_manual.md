# Manuel d'Utilisation - API REST Zero-Knowledge MedVault

Ce manuel présente l'architecture de sécurité, la procédure d'installation et le guide d'utilisation de l'API de stockage médical sécurisée avec chiffrement côté client (Zero-Knowledge).

---

## 1. Architecture de Sécurité (Zero-Knowledge)

La conception applique le principe du moindre privilège et de la sécurité à divulgation nulle de connaissance (Zero-Knowledge). Le serveur FastAPI (middleware de confiance) et la base de données Supabase ne manipulent et ne stockent que des données hautement confidentielles chiffrées en Base64. Ils n'ont jamais accès aux clés de chiffrement en clair (DEK) ni aux données cliniques textuelles.

### Modèle de Chiffrement Enveloppe (Envelope Encryption)

1. Génération de la DEK (Document Encryption Key) : Pour chaque nouveau document médical, le client génère localement dans son navigateur une clé symétrique cryptographique forte AES-GCM de 256 bits unique.

2. Chiffrement du Document : Le titre et le contenu du document médical sont chiffrés localement à l'aide de cette DEK en mode AES-GCM (avec un vecteur d'initialisation IV aléatoire de 12 octets). Le résultat est encodé en Base64.

3. Chiffrement de la DEK (Key Wrapping) : La DEK (exportée en octets bruts) est chiffrée par la clé maîtresse (KEK - Key Encryption Key) de l'utilisateur (dérivée localement via SHA-256 à partir de son mot de passe secret) en mode AES-GCM. Le résultat est encodé en Base64.

4. Transmission Opaque : Seuls les payloads Base64 (encrypted_title, encrypted_content, encrypted_dek) sont transmis au serveur FastAPI via une requête POST.

---

## 2. Installation et Configuration

### Prérequis

* Python 3.10 ou version supérieure installé.
* Une instance de base de données active sur Supabase.

### Étape 1 : Cloner ou copier les fichiers dans le dossier projet

Assurez-vous que les fichiers suivants sont présents dans votre espace de travail :

* config.py : Module de validation de la configuration Pydantic V2.
* database.py : Module d'initialisation du client SDK Supabase.
* schemas.py : Schémas de validation Pydantic V2.
* crypto.py : Module cryptographique complet (hachage, chiffrement).
* main.py : Fichier de démarrage de l'application FastAPI.
* migration.sql : Script d'initialisation PostgreSQL.
* requirements.txt : Liste des dépendances.
* index.html : Interface visuelle client.

### Étape 2 : Installer les dépendances

Exécutez la commande suivante dans le terminal pour installer les paquets requis :

```powershell
python -m pip install -r requirements.txt
```

### Étape 3 : Configurer l'environnement (.env)

Créez un fichier nommé .env à la racine du projet (c:\chiffrement\.env) et configurez vos variables d'accès Supabase :

```text
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_SERVICE_ROLE_KEY=votre-cle-service-role-ultra-secrete
```

Attention : N'utilisez JAMAIS la clé publique anon dans ce fichier de configuration. L'API FastAPI agissant en tant que middleware de confiance, elle a besoin de la clé service_role pour insérer et récupérer les données pour le compte des utilisateurs authentifiés (en appliquant ses propres filtres applicatifs stricts).

---

## 3. Initialisation et Déploiement

### Étape 1 : Exécuter la migration PostgreSQL

1. Connectez-vous à votre console Supabase.
2. Allez dans le SQL Editor.
3. Copiez et collez le contenu du fichier migration.sql.
4. Cliquez sur Run pour créer la table, l'index, la fonction de déclenchement (Trigger), et activer la sécurité RLS.

### Étape 2 : Lancer le serveur FastAPI

Pour démarrer le serveur de développement avec rechargement automatique, exécutez la commande suivante :

```powershell
python main.py
```

Le serveur sera disponible sur http://127.0.0.1:8000. La documentation interactive Swagger UI sera automatiquement accessible sur http://127.0.0.1:8000/docs.

### Étape 3 : Ouvrir l'Interface Client

Double-cliquez simplement sur le fichier index.html pour l'ouvrir dans n'importe quel navigateur web moderne. Vous pouvez également le servir localement si vous le souhaitez.

---

## 4. Manuel d'Utilisation de l'Interface Client

L'interface web index.html fournit une expérience utilisateur intuitive et interactive pour tester le chiffrement Zero-Knowledge.

### Procédure d'utilisation pas-à-pas

1. Saisie de la Clé Principale : Saisissez un mot de passe dans le champ "Clé Principale" (en haut à gauche). Ce mot de passe restera exclusivement dans la mémoire de votre navigateur.

2. Saisie de l'ID Utilisateur : Par défaut, un UUID de test est pré-rempli. Vous pouvez le conserver ou le remplacer par un UUID d'utilisateur réel provenant de votre table auth.users Supabase.

3. Création d'un Document : Saisissez un titre et un contenu médical dans les champs prévus à cet effet.

4. Envoi au Serveur : Cliquez sur le bouton "Chiffrer & Transmettre". La console affiche les étapes de génération de la DEK, le chiffrement AES-GCM des champs, et le wrapping de la DEK.

5. Vérification de l'isolation : Les documents insérés s'affichent sous forme de cartes dans la section "Documents Stockés". Vous pouvez observer que les valeurs affichées sont les chaînes Base64 brutes stockées sur le serveur (texte chiffré incompréhensible).

6. Déchiffrement local : Cliquez sur le bouton "Déchiffrer" d'une carte. Le navigateur déchiffre la DEK locale à l'aide de la clé maîtresse, puis déchiffre le titre et le contenu pour les afficher en clair. Si vous modifiez la clé maîtresse et cliquez sur déchiffre, le décryptage échouera, prouvant la robustesse cryptographique.

---

## 5. Cryptographie et Sécurité des Données en Base de Données

Le module crypto.py fournit une suite complète de primitives cryptographiques pour sécuriser les données sensibles stockées ou transmises.

### 5.1 Hachage (Hash)

Le hachage convertit une chaîne de toute taille en une empreinte unique et irréversible. Utilisé pour les mots de passe, les HMAC, et la vérification d'intégrité.

Algorithmes disponibles :

| Algorithme | Vitesse | Sécurité | Sortie | Usage | Statut |
|-----------|---------|---------|--------|-------|--------|
| SHA-256 | Très rapide | Très sécurisé | 256 bits | Hachage standard, dérivation de clés | Production |
| SHA-3 | Rapide | Très sécurisé | 256 bits | Alternative plus sécurisée à SHA-2 | Production |
| BLAKE2b | Extrêmement rapide | Très sécurisé | 512 bits | Performance extrême + sécurité | Production |
| MD5 | Extrêmement rapide | Non sécurisé | 128 bits | Déprécié (collisions connues) | Ne pas utiliser |

Exemple d'utilisation en Python :

```python
from crypto import HashAlgorithm

# Hachage d'un mot de passe avec SHA-256
password = "mon_mot_de_passe_sécurisé"
hashed = HashAlgorithm.sha256(password.encode())
print(hashed)

# HMAC pour l'authentification de message
key = b"secret_key"
message = b"message_important"
signature = HashAlgorithm.hmac_sha256(key, message)
```

### 5.2 Chiffrement Symétrique

Le chiffrement symétrique utilise la même clé pour chiffrer et déchiffrer. Idéal pour chiffrer des données volumineuses.

AES-256-GCM (Authenticated Encryption with Associated Data)

- Clé : 256 bits (32 octets)
- Mode : GCM (Galois/Counter Mode)
- Nonce : 96 bits (12 octets) aléatoire par chiffrement
- Authentification : Tag 128 bits vérifiant l'intégrité

```python
from crypto import SymmetricEncryption

# Génération d'une clé aléatoire
key = SymmetricEncryption.generate_key(256)

# Chiffrement
plaintext = b"Données médicales hautement confidentielles"
ciphertext_b64, nonce_b64 = SymmetricEncryption.encrypt_aes_gcm(plaintext, key)

# Déchiffrement
decrypted = SymmetricEncryption.decrypt_aes_gcm(ciphertext_b64, nonce_b64, key)
assert decrypted == plaintext
```

### 5.3 Chiffrement Asymétrique

Le chiffrement asymétrique utilise une paire de clés (publique/privée). La clé publique chiffre, la clé privée déchiffre.

RSA-2048 avec OAEP

- Clé privée : Reste secrète, stockée de manière sécurisée
- Clé publique : Peut être partagée librement
- Padding : OAEP + SHA-256 (sécurisation contre les attaques)

```python
from crypto import AsymmetricEncryption

# Génération de la paire de clés
private_key_pem, public_key_pem = AsymmetricEncryption.generate_rsa_keypair(2048)

# Chiffrement avec la clé publique
plaintext = b"Secret message"
ciphertext_b64 = AsymmetricEncryption.rsa_encrypt(plaintext, public_key_pem)

# Déchiffrement avec la clé privée
decrypted = AsymmetricEncryption.rsa_decrypt(ciphertext_b64, private_key_pem)
assert decrypted == plaintext
```

### 5.4 Tableau Comparatif Complet (Performance/Sécurité)

```python
from crypto import CryptoBenchmark

# Afficher le tableau complet
comparison = CryptoBenchmark.get_comparison_table()

# Structure de la comparaison :
# - hash_algorithms : SHA-256, SHA-3, BLAKE2b, MD5
# - symmetric_encryption : AES-256-GCM
# - asymmetric_encryption : RSA-2048, RSA-4096

# Benchmark les performances
benchmark_results = CryptoBenchmark.benchmark_hash_algorithms()
for algo, result in benchmark_results.items():
    print(f"{algo}: {result}")
```

Résumé du tableau :

- Hash : BLAKE2b est plus rapide que SHA-256 et SHA-3, tout en maintenant une sécurité maximale
- Symétrique : AES-256-GCM offre le meilleur rapport vitesse/sécurité pour les gros volumes
- Asymétrique : RSA-2048 suffisant pour la plupart des cas; RSA-4096 pour ultra-sécurité

---

## 6. Guide d'Utilisation des Endpoints de l'API (cURL)

### 6.1 Enregistrer un Document Chiffré

URL : POST /api/documents
En-têtes HTTP requis :
   - Content-Type: application/json
   - X-User-Id: <UUID_V4_UTILISATEUR>

Exemple de requête cURL :

```bash
curl -X POST "http://127.0.0.1:8000/api/documents" \
     -H "Content-Type: application/json" \
     -H "X-User-Id: a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11" \
     -d '{
           "encrypted_title": "Q2FyZGlvbG9neSBSZXBvcnQgMjAyNg==",
           "encrypted_content": "SGVhcnQgcmF0ZSBhbmQgRUNHIHNob3dlZCBub3JtYWwgc2ludXMgcmh5dGhtLiBObyBhYm5vcm1hbGl0aWVzIGRldGVjdGVkLg==",
           "encrypted_dek": "bXktc3VwZXItc2VjdXJlLWRlay1lbmNyeXB0ZWQtd2l0aC11c2VyLW1hc3Rlci1rZXk="
         }'
```

Réponse HTTP (201 Created) :

```json
{
  "encrypted_title": "Q2FyZGlvbG9neSBSZXBvcnQgMjAyNg==",
  "encrypted_content": "SGVhcnQgcmF0ZSBhbmQgRUNHIHNob3dlZCBub3JtYWwgc2ludXMgcmh5dGhtLiBObyBhYm5vcm1hbGl0aWVzIGRldGVjdGVkLg==",
  "encrypted_dek": "bXktc3VwZXItc2VjdXJlLWRlay1lbmNyeXB0ZWQtd2l0aC11c2VyLW1hc3Rlci1rZXk=",
  "id": "e43b185b-80a9-4672-9112-9cbb87864ffc",
  "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "created_at": "2026-05-18T12:50:00.123456Z",
  "updated_at": "2026-05-18T12:50:00.123456Z"
}
```

### 6.2 Récupérer les Documents de l'Utilisateur Authentifié

URL : GET /api/documents
En-têtes HTTP requis :
   - X-User-Id: <UUID_V4_UTILISATEUR>

Exemple de requête cURL :

```bash
curl -X GET "http://127.0.0.1:8000/api/documents" \
     -H "X-User-Id: a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
```

Réponse HTTP (200 OK) :

```json
[
  {
    "encrypted_title": "Q2FyZGlvbG9neSBSZXBvcnQgMjAyNg==",
    "encrypted_content": "SGVhcnQgcmF0ZSBhbmQgRUNHIHNob3dlZCBub3JtYWwgc2ludXMgcmh5dGhtLiBObyBhYm5vcm1hbGl0aWVzIGRldGVjdGVkLg==",
    "encrypted_dek": "bXktc3VwZXItc2VjdXJlLWRlay1lbmNyeXB0ZWQtd2l0aC11c2VyLW1hc3Rlci1rZXk=",
    "id": "e43b185b-80a9-4672-9112-9cbb87864ffc",
    "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "created_at": "2026-05-18T12:50:00.123456Z",
    "updated_at": "2026-05-18T12:50:00.123456Z"
  }
]
```

### 6.3 Gestion des Erreurs et Statuts Retournés

- 401 Unauthorized : Retourné si l'en-tête X-User-Id est manquant ou n'est pas un UUID V4 valide.
- 400 Bad Request : Retourné si le payload JSON est mal formé ou si la validation de Base64 dans les schémas Pydantic échoue.
- 500 Internal Server Error : Retourné en cas d'erreur inattendue au niveau du serveur ou de connexion avec Supabase.

---

## 7. Fichiers du Projet

| Fichier | Description |
|---------|-------------|
| main.py | Application FastAPI principale |
| database.py | Initialisation client Supabase |
| config.py | Validation configuration Pydantic V2 |
| schemas.py | Schémas de validation Pydantic V2 |
| crypto.py | Module cryptographique (hachage, chiffrement) |
| migration.sql | Script d'initialisation PostgreSQL |
| index.html | Interface client web |
| requirements.txt | Dépendances Python |
| user_manual.md | Ce fichier |

---

## 8. Spécifications Techniques

### Sécurité des Données

- Toutes les données sont chiffrées côté client avant transmission
- Le serveur stocke uniquement des données chiffrées en Base64
- Les clés de chiffrement ne transitent jamais par le réseau
- Utilisation de HTTPS recommandée en production

### Performance

- Chiffrement AES-256 : Performance optimale
- Déchiffrement en temps réel dans le navigateur
- Pas de goulot d'étranglement côté serveur

### Conformité

- Compatible avec les normes de confidentialité médicale
- Architecture Zero-Knowledge conforme RGPD
- Isolation des données par utilisateur garantie

---

Version : 1.0
Date : 2026-05-18
Status : Production
