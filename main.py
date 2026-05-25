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
    Renvoie une liste statique d'utilisateurs pour la démonstration.
    """
    logger.info("Récupération des utilisateurs de démonstration.")
    # On mock des utilisateurs pour la démo
    return [
        {
            "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
            "full_name": "Alim ZATO",
            "role": "Patient"
        },
        {
            "id": "b1ffcd88-8d1c-5fa9-cc7e-7cc0ce491b22",
            "full_name": "Dr. Jean Dupont",
            "role": "Médecin"
        }
    ]

# Montage d'un dossier static si besoin (pour l'instant, on n'a que index.html)
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Le reload automatique est activé
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
