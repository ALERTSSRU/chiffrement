-- migration.sql
-- Script de migration PostgreSQL pour Supabase
-- Initialisation de la table `medical_documents`

-- 1. Création de la table avec UUIDs natifs
CREATE TABLE IF NOT EXISTS public.medical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    encrypted_title TEXT NOT NULL,       -- Titre chiffré par le serveur
    encrypted_content TEXT NOT NULL,     -- Contenu chiffré par le serveur
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Commentaire de sécurité sur la table
COMMENT ON TABLE public.medical_documents IS 'Stockage sécurisé de documents médicaux chiffrés côté serveur.';

-- 2. Indexation de la clé user_id
CREATE INDEX IF NOT EXISTS idx_medical_documents_user_id ON public.medical_documents (user_id);

-- 3. Politique d'accès (Pour test, on autorise tout car le backend FastAPI filtre)
-- ATTENTION: En production, il faut configurer l'authentification JWT proprement.
-- Ici on désactive RLS pour faciliter le développement avec la clé anon via FastAPI.
ALTER TABLE public.medical_documents DISABLE ROW LEVEL SECURITY;
