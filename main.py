# main.py
# Point d'entrée principal de l'API FastAPI
# Architecture : Zero-Knowledge. L'API reçoit et stocke des données DÉJÀ CHIFFRÉES.

import logging
from uuid import UUID
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from config import settings
from database import get_supabase_client
from schemas import DocumentUploadSchema, DocumentResponseSchema, UserProfileSchema

# --- Configuration des logs ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Initialisation de l'application FastAPI ---
app = FastAPI(
    title="API de Stockage Médical Zéro-Connaissance",
    description="Stocke des documents chiffrés côté client sans jamais connaître leur contenu en clair.",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ─── ENDPOINTS DE L'API ─────────────────────────────────────────────────────────

@app.post(
    "/api/documents",
    response_model=DocumentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Sauvegarde un document chiffré",
    description="Reçoit un document déjà chiffré par le client et le stocke en base de données."
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
    """
    Stocke un nouveau document médical chiffré dans Supabase.
    L'API n'a pas la clé pour lire le contenu.
    """
    logger.info(f"Création d'un document pour l'utilisateur: {x_user_id}")

    # Préparation du payload pour Supabase
    db_payload = {
        "user_id": str(x_user_id),
        "encrypted_title": document.encrypted_title,
        "encrypted_content": document.encrypted_content,
        "encrypted_dek": document.encrypted_dek
    }

    try:
        # Insertion dans Supabase
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
    """
    Récupère tous les documents associés à un user_id spécifique.
    L'API renvoie les données chiffrées (Base64). Le client devra les déchiffrer.
    """
    logger.info(f"Récupération des documents pour l'utilisateur: {x_user_id}")
    
    try:
        # Requête Supabase
        response = supabase.table("medical_documents") \
            .select("*") \
            .eq("user_id", str(x_user_id)) \
            .order("created_at", desc=True) \
            .execute()
        
        logger.info(f"{len(response.data)} document(s) trouvé(s).")
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
    """
    Renvoie la liste des profils patients/médecins pour la sélection dans le formulaire.
    """
    logger.info("Récupération des profils utilisateurs.")
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

# Montage d'un dossier static si besoin (pour l'instant, on n'a que index.html)
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Le reload automatique est activé
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
