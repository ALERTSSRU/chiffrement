-- migration.sql
-- Script de migration PostgreSQL pour Supabase
-- Initialisation de la table `medical_documents` avec Row Level Security (RLS) et indexation optimale.

-- 1. Création de la table avec UUIDs natifs (SANS contrainte FK pour dev)
CREATE TABLE IF NOT EXISTS public.medical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    encrypted_title TEXT NOT NULL,       -- Titre opaque chiffré côté client (Base64)
    encrypted_content TEXT NOT NULL,     -- Contenu opaque chiffré côté client (Base64)
    encrypted_dek TEXT NOT NULL,         -- Clé DEK chiffrée sous clé maîtresse (Base64)
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    CONSTRAINT encrypted_title_not_empty CHECK (length(trim(encrypted_title)) > 0),
    CONSTRAINT encrypted_content_not_empty CHECK (length(trim(encrypted_content)) > 0),
    CONSTRAINT encrypted_dek_not_empty CHECK (length(trim(encrypted_dek)) > 0)
);

-- Commentaire de sécurité sur la table
COMMENT ON TABLE public.medical_documents IS 'Stockage ultra-sécurisé de documents médicaux chiffrés de bout en bout (Zero-Knowledge).';

-- 2. Indexation de la clé user_id pour optimiser les filtres par utilisateur
CREATE INDEX IF NOT EXISTS idx_medical_documents_user_id ON public.medical_documents (user_id);

-- 3. Activation de la sécurité au niveau des lignes (Row Level Security)
ALTER TABLE public.medical_documents ENABLE ROW LEVEL SECURITY;

-- 4. Désactivation des politiques RLS pour les tests (utilise service_role)
-- En production, ajouter les politiques appropriées

-- 5. Automatisation de la mise à jour du champ updated_at
CREATE OR REPLACE FUNCTION public.set_current_timestamp_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_update_medical_documents_timestamp
    BEFORE UPDATE ON public.medical_documents
    FOR EACH ROW
    EXECUTE FUNCTION public.set_current_timestamp_updated_at();
