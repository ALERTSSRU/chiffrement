# main.py
# Application principale FastAPI pour l'API REST de stockage de documents médicaux chiffrés côté serveur.

import uuid
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from postgrest.exceptions import APIError
from supabase import Client

from database import get_supabase_client
from schemas import DocumentUploadSchema, DocumentResponseSchema, UserProfileSchema
from crypto import ServerCrypto

app = FastAPI(
    title="Server-Side Medical Storage API",
    description="API REST de stockage de documents médicaux avec chiffrement côté serveur.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-Id"],
)

@app.get("/", response_class=FileResponse)
async def read_index():
    return FileResponse("index.html")

async def get_current_user_id(
    x_user_id: str = Header(
        default="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        alias="X-User-Id"
    )
) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="L'en-tête 'X-User-Id' est manquant ou n'est pas un UUID valide."
        )

@app.post("/api/documents", response_model=DocumentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_medical_document(
    payload: DocumentUploadSchema,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Client = Depends(get_supabase_client)
) -> DocumentResponseSchema:
    try:
        # CHIFFREMENT CÔTÉ SERVEUR : On chiffre le texte clair avant de l'envoyer à la DB
        encrypted_title = ServerCrypto.encrypt_text(payload.title)
        encrypted_content = ServerCrypto.encrypt_text(payload.content)

        document_data = {
            "user_id": str(user_id),
            "encrypted_title": encrypted_title,
            "encrypted_content": encrypted_content
        }
        
        response = db.table("medical_documents").insert(document_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Erreur lors de l'insertion.")
            
        inserted_row = response.data[0]
        
        # On reconstitue l'objet avec les données en clair pour la réponse
        inserted_row["title"] = payload.title
        inserted_row["content"] = payload.content
        return DocumentResponseSchema.model_validate(inserted_row)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=List[DocumentResponseSchema])
async def list_medical_documents(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Client = Depends(get_supabase_client)
) -> List[DocumentResponseSchema]:
    try:
        response = db.table("medical_documents").select("*").eq("user_id", str(user_id)).execute()
        
        documents = []
        for row in response.data:
            try:
                # DÉCHIFFREMENT CÔTÉ SERVEUR : On déchiffre les données de la DB
                row["title"] = ServerCrypto.decrypt_text(row["encrypted_title"])
                row["content"] = ServerCrypto.decrypt_text(row["encrypted_content"])
                documents.append(DocumentResponseSchema.model_validate(row))
            except Exception as decrypt_error:
                print(f"Erreur de déchiffrement pour le document {row.get('id')}: {decrypt_error}")
                # On ignore les documents qu'on ne peut pas déchiffrer
                continue
                
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/documents/raw",
    summary="Afficher les documents chiffrés bruts (Base64) tels que stockés en DB",
    description="Endpoint pédagogique : retourne les données exactement comme elles sont stockées dans Supabase, sans déchiffrement. Utile pour démontrer que le serveur stocke des données illisibles."
)
async def list_raw_documents(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Client = Depends(get_supabase_client)
):
    """Route pour afficher les données brutes chiffrées de la base de données."""
    try:
        response = (
            db.table("medical_documents")
            .select("id, user_id, encrypted_title, encrypted_content, created_at")
            .eq("user_id", str(user_id))
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/users",
    response_model=List[UserProfileSchema],
    status_code=status.HTTP_200_OK,
    summary="Récupérer tous les profils d'utilisateurs disponibles",
)
async def list_user_profiles(
    db: Client = Depends(get_supabase_client)
) -> List[UserProfileSchema]:
    try:
        response = db.table("profiles").select("id, full_name, role").execute()
        return [UserProfileSchema.model_validate(row) for row in response.data]
    except APIError as e:
        raise HTTPException(status_code=400, detail=f"Erreur DB ({e.code}): {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
