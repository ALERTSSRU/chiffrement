# database.py
# Initialisation et exposition du client Supabase officiel (supabase-py).
# Configure le client de manière globale pour être réutilisé à travers toute l'application FastAPI.

from supabase import create_client, Client
from config import settings

# Enregistrement et initialisation du client Supabase
# IMPORTANT : Dans Pydantic V2, HttpUrl est un objet typé.
# Nous devons le caster explicitement en chaîne de caractères pour create_client.
supabase_client: Client = create_client(
    supabase_url=str(settings.SUPABASE_URL),
    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_supabase_client() -> Client:
    """
    Dépendance FastAPI ou fonction utilitaire pour obtenir le client Supabase.
    Bien que supabase_client soit un singleton thread-safe, cette fonction permet
    d'abstraire l'accès direct et de faciliter le mocking dans les tests unitaires.
    """
    return supabase_client
