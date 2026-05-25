# schemas.py
# Définitions des schémas de données de l'API avec Pydantic V2.

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class DocumentUploadSchema(BaseModel):
    """
    Schéma de validation pour la création d'un nouveau document médical.
    Le client envoie les données DEJA CHIFFRÉES (Zero-Knowledge).
    """
    encrypted_title: str = Field(
        ...,
        min_length=1,
        description="Le titre du document chiffré par le client (Base64)."
    )
    encrypted_content: str = Field(
        ...,
        min_length=1,
        description="Le contenu du document chiffré par le client (Base64)."
    )
    encrypted_dek: str = Field(
        ...,
        min_length=1,
        description="La clé DEK chiffrée par la KEK du client (Base64)."
    )

class DocumentResponseSchema(BaseModel):
    """
    Schéma de retour d'un document médical (toujours chiffré).
    """
    id: UUID = Field(
        ...,
        description="L'identifiant unique (UUID v4) du document médical enregistré."
    )
    user_id: UUID = Field(
        ...,
        description="L'UUID de l'utilisateur propriétaire du document."
    )
    encrypted_title: str = Field(
        ...,
        description="Le titre du document chiffré."
    )
    encrypted_content: str = Field(
        ...,
        description="Le contenu du document chiffré."
    )
    encrypted_dek: str = Field(
        ...,
        description="La clé DEK chiffrée."
    )
    created_at: datetime = Field(
        ...,
        description="Date et heure de création UTC du document."
    )
    updated_at: datetime = Field(
        ...,
        description="Date et heure de la dernière mise à jour UTC du document."
    )

    model_config = ConfigDict(
        from_attributes=True
    )

class UserProfileSchema(BaseModel):
    """
    Schéma de retour pour les profils d'utilisateurs disponibles.
    """
    id: UUID = Field(..., description="L'UUID unique de l'utilisateur.")
    full_name: str | None = Field(None, description="Le nom complet de l'utilisateur.")
    role: str | None = Field(None, description="Le rôle de l'utilisateur.")

    model_config = ConfigDict(
        from_attributes=True
    )
