# schemas.py
# Définitions des schémas de données de l'API avec Pydantic V2.

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class DocumentUploadSchema(BaseModel):
    """
    Schéma de validation pour la création d'un nouveau document médical.
    Le client envoie les données en clair, le serveur se chargera de les chiffrer.
    """
    title: str = Field(
        ...,
        min_length=1,
        description="Le titre du document en clair.",
        examples=["Bilan sanguin"]
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Le contenu textuel du document médical en clair.",
        examples=["Le patient présente un taux de fer un peu bas..."]
    )

class DocumentResponseSchema(BaseModel):
    """
    Schéma de retour d'un document médical (déchiffré par le serveur).
    """
    id: UUID = Field(
        ...,
        description="L'identifiant unique (UUID v4) du document médical enregistré."
    )
    user_id: UUID = Field(
        ...,
        description="L'UUID de l'utilisateur propriétaire du document."
    )
    title: str = Field(
        ...,
        description="Le titre du document déchiffré."
    )
    content: str = Field(
        ...,
        description="Le contenu du document déchiffré."
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
