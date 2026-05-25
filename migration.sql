-- migration.sql
-- Script de migration PostgreSQL pour Supabase
-- Initialisation de la table `medical_documents`

-- 1. Nettoyage de la table existante (pour restauration du projet)
DROP TABLE IF EXISTS public.medical_documents;

-- 2. Création de la table avec UUIDs natifs et champs chiffrés côté client
CREATE TABLE public.medical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    encrypted_title TEXT NOT NULL,       -- Titre chiffré par le client
    encrypted_content TEXT NOT NULL,     -- Contenu chiffré par le client
    encrypted_dek TEXT NOT NULL,         -- Clé DEK chiffrée par le client (avec KEK)
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Commentaire de sécurité sur la table
COMMENT ON TABLE public.medical_documents IS 'Stockage sécurisé de documents médicaux (Chiffrement Zéro-Connaissance côté client).';

-- 3. Indexation de la clé user_id
CREATE INDEX IF NOT EXISTS idx_medical_documents_user_id ON public.medical_documents (user_id);

-- 4. Politique d'accès (Pour test, on autorise tout car le backend FastAPI filtre)
ALTER TABLE public.medical_documents DISABLE ROW LEVEL SECURITY;
