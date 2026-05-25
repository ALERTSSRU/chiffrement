# schemas.py
# Définitions et validations strictes des schémas de données de l'API avec Pydantic V2.
# Assure que le serveur ne manipule que des chaînes Base64 opaques et valides.

import base64
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict

def is_valid_base64(value: str) -> bool:
    """
    Vérifie rigoureusement si une chaîne est encodée en Base64 valide (standard ou URL-safe).
    """
    if not value or not value.strip():
        return False
    try:
        # Normalisation pour supporter à la fois le base64 standard et url-safe
        normalized = value.replace('-', '+').replace('_', '/')
        # Correction automatique du padding si manquant
        padding = len(normalized) % 4
        if padding:
            normalized += '=' * (4 - padding)
        
        # Tentative de décodage avec validation stricte
        base64.b64decode(normalized, validate=True)
        return True
    except Exception:
        return False

class DocumentBaseSchema(BaseModel):
    """
    Schéma de base partagé contenant les données chiffrées de manière opaque.
    """
    encrypted_title: str = Field(
        ...,
        description="Le titre du document chiffré côté client, encodé en Base64.",
        examples=["U2VjcmV0IE1lZGljYWwgUmVwb3J0"]
    )
    encrypted_content: str = Field(
        ...,
        description="Le contenu textuel ou JSON chiffré du document médical, encodé en Base64.",
        examples=["dGhpcyBpcyBhIGhpZ2hseSBzZW5zaXRpdmUgbWVkaWNhbCByZWNvcmQgY29udGVudCB0aGF0IGlzIGVuY3J5cHRlZA=="]
    )
    encrypted_dek: str = Field(
        ...,
        description="La clé de chiffrement du document (DEK) elle-même chiffrée par la clé maîtresse de l'utilisateur, encodée en Base64.",
        examples=["YWVzLWdjbS1rZXktZW5jcnlwdGVkLWJ5LW1hc3Rlci1rZXk="]
    )

    @field_validator("encrypted_title", "encrypted_content", "encrypted_dek")
    @classmethod
    def validate_base64_fields(cls, v: str) -> str:
        """
        Validateur strict s'assurant que les données reçues sont du Base64 valide et non vides.
        """
        if not v or not v.strip():
            raise ValueError("Le champ ne peut pas être vide.")
        if not is_valid_base64(v):
            raise ValueError("Le champ doit être une chaîne de caractères encodée en Base64 valide.")
        return v.strip()

class DocumentUploadSchema(DocumentBaseSchema):
    """
    Schéma de validation pour la création d'un nouveau document médical.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "encrypted_title": "Q2FyZGlvbG9neSBSZXBvcnQgMjAyNg==",
                "encrypted_content": "SGVhcnQgcmF0ZSBhbmQgRUNHIHNob3dlZCBub3JtYWwgc2ludXMgcmh5dGhtLiBObyBhYm5vcm1hbGl0aWVzIGRldGVjdGVkLg==",
                "encrypted_dek": "bXktc3VwZXItc2VjdXJlLWRlay1lbmNyeXB0ZWQtd2l0aC11c2VyLW1hc3Rlci1rZXk="
            }
        }
    )

class DocumentResponseSchema(DocumentBaseSchema):
    """
    Schéma de retour d'un document médical après enregistrement ou récupération.
    """
    id: UUID = Field(
        ...,
        description="L'identifiant unique (UUID v4) du document médical enregistré."
    )
    user_id: UUID = Field(
        ...,
        description="L'UUID de l'utilisateur propriétaire du document."
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
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
                "user_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                "encrypted_title": "Q2FyZGlvbG9neSBSZXBvcnQgMjAyNg==",
                "encrypted_content": "SGVhcnQgcmF0ZSBhbmQgRUNHIHNob3dlZCBub3JtYWwgc2ludXMgcmh5dGhtLiBObyBhYm5vcm1hbGl0aWVzIGRldGVjdGVkLg==",
                "encrypted_dek": "bXktc3VwZXItc2VjdXJlLWRlay1lbmNyeXB0ZWQtd2l0aC11c2VyLW1hc3Rlci1rZXk=",
                "created_at": "2026-05-18T12:00:00Z",
                "updated_at": "2026-05-18T12:00:00Z"
            }
        }
    )

class UserProfileSchema(BaseModel):
    """
    Schéma de retour pour les profils d'utilisateurs disponibles dans la base de données.
    """
    id: UUID = Field(..., description="L'UUID unique de l'utilisateur.")
    full_name: str | None = Field(None, description="Le nom complet de l'utilisateur.")
    role: str | None = Field(None, description="Le rôle de l'utilisateur (admin, brand, influencer).")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "b36fae79-481b-4b89-810e-c4761d655914",
                "full_name": "ZATO",
                "role": "admin"
            }
        }
    )

