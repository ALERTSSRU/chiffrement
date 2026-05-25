# config.py
# Gestion et validation rigoureuse des variables d'environnement de l'application.
# Utilise Pydantic V2 et pydantic-settings pour une configuration robuste.

import sys
from pydantic import HttpUrl, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuration de l'application validée via Pydantic.
    Prend en charge le chargement depuis l'environnement système ou un fichier `.env`.
    """
    
    # Configuration du modèle Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    SUPABASE_URL: HttpUrl = Field(
        ...,
        description="L'URL de l'instance Supabase (ex: https://abcde12345.supabase.co)."
    )
    
    SUPABASE_ANON_KEY: str = Field(
        ...,
        min_length=1,
        description="Clé publique (anon) de Supabase."
    )

    ENCRYPTION_MASTER_KEY: str = Field(
        ...,
        min_length=43,
        description="Clé maîtresse (Fernet) pour chiffrer les données côté serveur."
    )

# Chargement et validation immédiate de la configuration
try:
    settings = Settings()
except ValidationError as e:
    print("CRITICAL: Échec de la validation de la configuration !", file=sys.stderr)
    for err in e.errors():
        print(f"  [Erreur]: {err['msg']}", file=sys.stderr)
    sys.exit(1)
