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
    
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        ...,
        min_length=1,
        description="Clé de service secrète de Supabase. Utilisée uniquement côté serveur pour bypass la RLS."
    )

# Chargement et validation immédiate de la configuration
try:
    settings = Settings()
except ValidationError as e:
    print(
        "========================================================================",
        file=sys.stderr
    )
    print(
        "CRITICAL: Échec de la validation de la configuration de l'application !",
        file=sys.stderr
    )
    print(
        "Veuillez définir correctement les variables d'environnement requises.",
        file=sys.stderr
    )
    print(
        "========================================================================",
        file=sys.stderr
    )
    for err in e.errors():
        field = " -> ".join(str(loc_item) for loc_item in err["loc"])
        print(f"  [Erreur] {field}: {err['msg']} (Valeur fournie: {err.get('input')})", file=sys.stderr)
    print(
        "\nAssurez-vous que vos variables d'environnement ou votre fichier .env contiennent :",
        file=sys.stderr
    )
    print("  - SUPABASE_URL (URL HTTP/HTTPS valide)", file=sys.stderr)
    print("  - SUPABASE_SERVICE_ROLE_KEY (Chaîne de caractères non vide)", file=sys.stderr)
    print(
        "========================================================================",
        file=sys.stderr
    )
    sys.exit(1)
