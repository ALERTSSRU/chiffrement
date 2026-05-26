# main.py
# Point d'entrée principal de l'API FastAPI
# Intègre la sélection dynamique de 13 algorithmes de chiffrement (Symmetric, Asymmetric, Hashing)
# Architecture : Hybride/Zéro-Connaissance pour la démonstration académique.

import logging
import time
from uuid import UUID
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import get_supabase_client
from schemas import DocumentUploadSchema, DocumentResponseSchema, UserProfileSchema

# Import du gestionnaire de cryptographie et des hacheurs
from crypto_manager import CryptoManager
from crypto_engines.sha256 import SHA256Engine
from crypto_engines.sha3 import SHA3Engine
from crypto_engines.blake2 import BLAKE2Engine
from crypto_engines.md5 import MD5Engine

# --- Configuration des logs ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Initialisation de l'application FastAPI ---
app = FastAPI(
    title="MedVault Pro - Console Multicryptographique",
    description="Interface de démonstration académique permettant de tester 13 algorithmes cryptographiques.",
    version="2.0.0"
)

# --- Configuration CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── MODÈLES DE REQUÊTES CRYPTOGRAPHIQUES ──────────────────────────────────────────

class EncryptRequest(BaseModel):
    plaintext_title: str = Field(..., description="Le titre du document en clair.")
    plaintext_content: str = Field(..., description="Le contenu du document en clair.")
    master_password: str = Field(..., description="Le mot de passe de dérivation (KEK).")
    algorithm: str = Field(..., description="L'algorithme à utiliser (AES, RSA, ECC, etc.).")

class EncryptResponse(BaseModel):
    encrypted_title: str
    encrypted_content: str
    encrypted_dek: str
    algorithm: str
    logs: list[str]
    duration_ms: float

class DecryptRequest(BaseModel):
    encrypted_title: str
    encrypted_content: str
    encrypted_dek: str
    master_password: str

class DecryptResponse(BaseModel):
    title: str
    content: str
    algorithm: str
    logs: list[str]
    duration_ms: float

class HashRequest(BaseModel):
    data: str = Field(..., description="La chaîne de caractères à hacher.")
    algorithm: str = Field(..., description="L'algorithme de hachage (SHA-256, SHA-3, BLAKE2, MD5).")

class HashResponse(BaseModel):
    hash_value: str
    logs: list[str]

# ─── SERVING DU FRONTEND ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, summary="Affiche l'interface web (index.html)")
async def serve_index():
    """
    Sert le fichier index.html situé à la racine du projet.
    """
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        logger.error("Le fichier index.html est introuvable.")
        raise HTTPException(status_code=404, detail="Interface web introuvable.")

# ─── ENDPOINTS CRYPTOGRAPHIQUES DYNAMIQUES ───────────────────────────────────────

@app.post(
    "/api/crypto/encrypt",
    response_model=EncryptResponse,
    summary="Chiffre dynamiquement un document via les moteurs Python",
    description="Prend le texte en clair et applique l'algorithme choisi parmi les 9 chiffrements."
)
async def api_encrypt_document(req: EncryptRequest):
    logger.info(f"Demande de chiffrement dynamique avec : {req.algorithm}")
    try:
        result = CryptoManager.encrypt_document(
            req.plaintext_title,
            req.plaintext_content,
            req.master_password,
            req.algorithm
        )
        return result
    except Exception as e:
        logger.error(f"Erreur de chiffrement dynamique : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de chiffrement : {str(e)}")

@app.post(
    "/api/crypto/decrypt",
    response_model=DecryptResponse,
    summary="Déchiffre dynamiquement un document via les moteurs Python",
    description="Détecte l'algorithme et applique le bon moteur de déchiffrement."
)
async def api_decrypt_document(req: DecryptRequest):
    logger.info("Demande de déchiffrement dynamique détectée.")
    try:
        result = CryptoManager.decrypt_document(
            req.encrypted_title,
            req.encrypted_content,
            req.encrypted_dek,
            req.master_password
        )
        return result
    except Exception as e:
        logger.error(f"Erreur de déchiffrement : {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Échec du déchiffrement. Clé incorrecte, algorithme non supporté ou paquet altéré."
        )

@app.post(
    "/api/crypto/hash",
    response_model=HashResponse,
    summary="Hache une chaîne via les 4 moteurs de hachage",
    description="Permet de tester SHA-256, SHA-3, BLAKE2 et MD5 dans le bac à sable de l'UI."
)
async def api_hash_data(req: HashRequest):
    logger.info(f"Demande de hachage dynamique avec : {req.algorithm}")
    logs = []
    t_start = time.perf_counter()
    data_bytes = req.data.encode('utf-8')
    hash_val = ""
    
    logs.append(f"[HASH] Entrée : '{req.data}' ({len(data_bytes)} octets)")
    logs.append(f"[HASH] Utilisation de l'algorithme : {req.algorithm}")
    
    try:
        if req.algorithm == "SHA-256":
            hash_val = SHA256Engine.hash(data_bytes)
            logs.append("[SHA-256] Calcul de l'empreinte sécurisée standard NIST...")
        elif req.algorithm == "SHA-3":
            hash_val = SHA3Engine.hash(data_bytes)
            logs.append("[SHA-3] Calcul de l'empreinte Keccak moderne...")
        elif req.algorithm == "BLAKE2":
            hash_val = BLAKE2Engine.hash(data_bytes)
            logs.append("[BLAKE2b] Calcul de l'empreinte ultra-rapide BLAKE2b...")
        elif req.algorithm == "MD5":
            hash_val = MD5Engine.hash(data_bytes)
            logs.append("[MD5] ALERTE : Algorithme MD5 cassé. Utilisation pédagogique uniquement.")
        else:
            raise ValueError(f"Algorithme de hachage inconnu : {req.algorithm}")
            
        duration = (time.perf_counter() - t_start) * 1000
        logs.append(f"[EXEC] Résultat (hex) : {hash_val}")
        logs.append(f"[FIN] Temps d'exécution : {duration:.4f} ms")
        
        return {"hash_value": hash_val, "logs": logs}
    except Exception as e:
        logger.error(f"Erreur de hachage : {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ─── ENDPOINTS DE STOCKAGE STANDARD (Supabase) ─────────────────────────────────

@app.post(
    "/api/documents",
    response_model=DocumentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Sauvegarde un document chiffré",
    description="Stocke le paquet cryptographique chiffré dans Supabase."
)
async def create_document(
    document: DocumentUploadSchema,
    x_user_id: UUID = Header(
        ...,
        description="L'UUID de l'utilisateur qui soumet le document.",
        alias="X-User-Id"
    ),
    supabase=Depends(get_supabase_client)
):
    logger.info(f"Sauvegarde du document dans Supabase pour l'utilisateur: {x_user_id}")

    db_payload = {
        "user_id": str(x_user_id),
        "encrypted_title": document.encrypted_title,
        "encrypted_content": document.encrypted_content,
        "encrypted_dek": document.encrypted_dek
    }

    try:
        response = supabase.table("medical_documents").insert(db_payload).execute()
        
        if not response.data:
            logger.error("Supabase n'a renvoyé aucune donnée après l'insertion.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de l'enregistrement en base de données."
            )

        logger.info(f"Document créé avec succès (ID: {response.data[0]['id']}).")
        return response.data[0]

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion dans Supabase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}"
        )


@app.get(
    "/api/documents",
    response_model=list[DocumentResponseSchema],
    summary="Récupère les documents chiffrés",
    description="Renvoie la liste de tous les documents chiffrés appartenant à l'utilisateur."
)
async def get_documents(
    x_user_id: UUID = Header(
        ...,
        description="L'UUID de l'utilisateur dont on veut récupérer les documents.",
        alias="X-User-Id"
    ),
    supabase=Depends(get_supabase_client)
):
    logger.info(f"Récupération des documents pour l'utilisateur: {x_user_id}")
    
    try:
        response = supabase.table("medical_documents") \
            .select("*") \
            .eq("user_id", str(x_user_id)) \
            .order("created_at", desc=True) \
            .execute()
        
        logger.info(f"{len(response.data)} document(s) chiffré(s) trouvé(s).")
        return response.data
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération depuis Supabase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données : {str(e)}"
        )

@app.get(
    "/api/users",
    response_model=list[UserProfileSchema],
    summary="Récupère les profils utilisateurs",
    description="Renvoie la liste des utilisateurs de démonstration."
)
async def get_users():
    return [
        {"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "full_name": "Alim ZATO",       "role": "Patient"},
        {"id": "b1ffcd88-8d1c-4fa9-ac7e-7cc0ce491b22", "full_name": "Jean DUPONT",      "role": "Médecin"},
        {"id": "c2aaef77-7e2b-4ab8-bd8f-8dd1df582c33", "full_name": "Marie MARTIN",     "role": "Patient"},
        {"id": "d3bbfe66-6f3c-4bc7-ae9e-9ee2ef693d44", "full_name": "Pierre BERNARD",   "role": "Patient"},
        {"id": "e4ccad55-5a4d-4cd6-bf0f-0ff3fa7a4e55", "full_name": "Sophie LEFEBVRE",  "role": "Infirmière"},
        {"id": "f5ddbe44-4b5e-4de5-aa1a-1aa4ab8b5f66", "full_name": "Mohamed DIALLO",   "role": "Patient"},
        {"id": "a6eecf33-3c6f-4ef4-bb2b-2bb5bc9c6a77", "full_name": "Camille ROUSSEAU", "role": "Patient"},
        {"id": "b7fada22-2d7a-4fa3-ac3c-3cc6cd0d7b88", "full_name": "Thomas MOREAU",    "role": "Médecin"},
        {"id": "c8abeb11-1e8b-4ab2-bd4d-4dd7de1e8c99", "full_name": "Fatima BENALI",    "role": "Patient"},
        {"id": "d9bcfc00-0f9c-4bc1-ae5e-5ee8ef2f9d00", "full_name": "Lucas SIMON",      "role": "Patient"},
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
