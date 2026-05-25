from supabase import create_client, Client
from config import settings

supabase_client: Client = create_client(
    supabase_url=str(settings.SUPABASE_URL),
    supabase_key=settings.SUPABASE_ANON_KEY
)

def get_supabase_client() -> Client:
    return supabase_client
