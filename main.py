# main.py
# Application principale FastAPI pour l'API REST de stockage de documents médicaux chiffrés.
# Met en œuvre l'authentification simulée par dépendance et l'interaction avec le SDK Supabase.

import uuid
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from postgrest.exceptions import APIError
from supabase import Client

from database import get_supabase_client
from schemas import DocumentUploadSchema, DocumentResponseSchema, UserProfileSchema

# Initialisation de l'application FastAPI avec métadonnées complètes pour OpenAPI
app = FastAPI(
    title="Zero-Knowledge Medical Storage API",
    description=(
        "API REST ultra-sécurisée de stockage de documents médicaux avec chiffrement "
        "côté client (Zero-Knowledge). Le serveur ne traite et ne stocke que des chaînes Base64 opaques."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration du middleware CORS pour la production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production réelle (ex: ["https://monapp.com"])
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-Id"],
)

@app.get("/", response_class=FileResponse, summary="Servir la page d'accueil MedVault")
async def read_index():
    """
    Sert le fichier HTML statique 'index.html' directement depuis le serveur FastAPI.
    """
    return FileResponse("index.html")

async def get_current_user_id(
    x_user_id: str = Header(
        default="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",  # UUID de test par défaut
        alias="X-User-Id",
        description="Identifiant unique (UUID V4) de l'utilisateur authentifié (simulé pour intégration JWT future)"
    )
) -> uuid.UUID:
    """
    Dépendance de simulation d'authentification.
    Extrait l'identifiant utilisateur depuis l'en-tête HTTP 'X-User-Id' et valide son format UUID V4.
    Cette dépendance permet de brancher très facilement un décodeur de JWT Supabase par la suite.
    """
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification échouée: L'en-tête 'X-User-Id' est manquant ou n'est pas un UUID V4 valide."
        )

@app.post(
    "/api/documents",
    response_model=DocumentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer un nouveau document médical chiffré",
    description=(
        "Reçoit les charges utiles chiffrées en Base64 depuis le client et les insère dans Supabase. "
        "Le serveur FastAPI agit comme middleware de confiance en forçant l'attribution au 'user_id' authentifié."
    )
)
async def create_medical_document(
    payload: DocumentUploadSchema,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Client = Depends(get_supabase_client)
) -> DocumentResponseSchema:
    """
    Route asynchrone d'insertion de document.
    """
    try:
        # Préparation du payload avec injection forcée de l'ID utilisateur authentifié (Sécurité)
        document_data = {
            "user_id": str(user_id),
            "encrypted_title": payload.encrypted_title,
            "encrypted_content": payload.encrypted_content,
            "encrypted_dek": payload.encrypted_dek
        }
        
        # Requête d'insertion vers Supabase
        response = (
            db.table("medical_documents")
            .insert(document_data)
            .execute()
        )
        
        # Vérification du résultat
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur serveur: La base de données n'a retourné aucun enregistrement."
            )
            
        # Extraction et conversion vers le schéma de réponse validé
        inserted_row = response.data[0]
        return DocumentResponseSchema.model_validate(inserted_row)
        
    except APIError as e:
        # Capture spécifique des erreurs d'API Supabase/PostgREST
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur Supabase DB ({e.code}): {e.message}"
        )
    except Exception as e:
        # Capture de toute autre erreur inattendue
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur interne inattendue est survenue: {str(e)}"
        )

@app.get(
    "/api/documents",
    response_model=List[DocumentResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Récupérer tous les documents chiffrés de l'utilisateur",
    description=(
        "Récupère tous les enregistrements chiffrés pour l'utilisateur authentifié. "
        "En raison de l'utilisation de la clé 'service_role' (qui contourne la RLS), "
        "le filtrage par 'user_id' est explicitement appliqué au niveau de la requête pour garantir une isolation stricte."
    )
)
async def list_medical_documents(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Client = Depends(get_supabase_client)
) -> List[DocumentResponseSchema]:
    """
    Route asynchrone de récupération des documents.
    """
    try:
        # Requête filtrée stricte sur le user_id authentifié
        response = (
            db.table("medical_documents")
            .select("*")
            .eq("user_id", str(user_id))
            .execute()
        )
        
        # Validation et sérialisation automatique via le type de retour
        return [DocumentResponseSchema.model_validate(row) for row in response.data]
        
    except APIError as e:
        # Capture spécifique des erreurs d'API Supabase/PostgREST
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur Supabase DB ({e.code}): {e.message}"
        )
    except Exception as e:
        # Capture de toute autre erreur inattendue
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur interne inattendue est survenue: {str(e)}"
        )

@app.get(
    "/api/users",
    response_model=List[UserProfileSchema],
    status_code=status.HTTP_200_OK,
    summary="Récupérer tous les profils d'utilisateurs disponibles",
    description="Récupère les identifiants et noms des profils dans la table 'profiles' de Supabase."
)
async def list_user_profiles(
    db: Client = Depends(get_supabase_client)
) -> List[UserProfileSchema]:
    """
    Route asynchrone pour lister les profils d'utilisateurs.
    """
    try:
        response = (
            db.table("profiles")
            .select("id, full_name, role")
            .execute()
        )
        return [UserProfileSchema.model_validate(row) for row in response.data]
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur Supabase DB ({e.code}): {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur interne est survenue: {str(e)}"
        )

# Démarrage direct via uvicorn pour faciliter les tests de développement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
