-- migration.sql
-- Script de migration PostgreSQL pour Supabase
-- Tables : users + medical_documents

-- ═══════════════════════════════════════════
-- TABLE : users (Profils patients)
-- ═══════════════════════════════════════════

-- 1. Nettoyage
DROP TABLE IF EXISTS public.medical_documents;
DROP TABLE IF EXISTS public.users;

-- 2. Création de la table users
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Patient',
    date_of_birth DATE,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.users IS 'Profils des patients/médecins de la clinique MedVault.';
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;

-- 3. Insertion de 10 profils patients de démonstration
INSERT INTO public.users (id, full_name, role, date_of_birth, email, phone) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Alim ZATO',        'Patient',    '1995-06-14', 'alim.zato@email.fr',          '+33 6 12 34 56 78'),
    ('b1ffcd88-8d1c-4fa9-ac7e-7cc0ce491b22', 'Jean DUPONT',       'Médecin',    '1978-03-22', 'dr.dupont@medvault.fr',        '+33 6 98 76 54 32'),
    ('c2aaef77-7e2b-4ab8-bd8f-8dd1df582c33', 'Marie MARTIN',      'Patient',    '1989-11-05', 'marie.martin@email.fr',        '+33 7 23 45 67 89'),
    ('d3bbfe66-6f3c-4bc7-ae9e-9ee2ef693d44', 'Pierre BERNARD',    'Patient',    '1965-07-30', 'pierre.bernard@email.fr',      '+33 6 34 56 78 90'),
    ('e4ccad55-5a4d-4cd6-bf0f-0ff3fa7a4e55', 'Sophie LEFEBVRE',   'Infirmière', '1990-02-18', 'sophie.lefebvre@clinique.fr',  '+33 6 45 67 89 01'),
    ('f5ddbe44-4b5e-4de5-aa1a-1aa4ab8b5f66', 'Mohamed DIALLO',    'Patient',    '1982-09-12', 'mohamed.diallo@email.fr',      '+33 7 56 78 90 12'),
    ('a6eecf33-3c6f-4ef4-bb2b-2bb5bc9c6a77', 'Camille ROUSSEAU',  'Patient',    '2001-04-25', 'camille.rousseau@email.fr',    '+33 6 67 89 01 23'),
    ('b7fada22-2d7a-4fa3-ac3c-3cc6cd0d7b88', 'Thomas MOREAU',     'Médecin',    '1974-12-08', 'dr.moreau@medvault.fr',        '+33 6 78 90 12 34'),
    ('c8abeb11-1e8b-4ab2-bd4d-4dd7de1e8c99', 'Fatima BENALI',     'Patient',    '1998-08-17', 'fatima.benali@email.fr',       '+33 7 89 01 23 45'),
    ('d9bcfc00-0f9c-4bc1-ae5e-5ee8ef2f9d00', 'Lucas SIMON',       'Patient',    '1975-01-03', 'lucas.simon@email.fr',         '+33 6 90 12 34 56');

-- ═══════════════════════════════════════════
-- TABLE : medical_documents
-- ═══════════════════════════════════════════

-- 4. Création de la table medical_documents
CREATE TABLE public.medical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    encrypted_title TEXT NOT NULL,       -- Titre chiffré par le client (AES-GCM)
    encrypted_content TEXT NOT NULL,     -- Contenu chiffré par le client (AES-GCM)
    encrypted_dek TEXT NOT NULL,         -- Clé DEK chiffrée par le client (avec KEK)
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

COMMENT ON TABLE public.medical_documents IS 'Stockage sécurisé de documents médicaux (Zéro-Connaissance — chiffrement côté client).';

-- 5. Indexation
CREATE INDEX IF NOT EXISTS idx_medical_documents_user_id ON public.medical_documents (user_id);

-- 6. Politique d'accès
ALTER TABLE public.medical_documents DISABLE ROW LEVEL SECURITY;
