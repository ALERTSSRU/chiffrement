"""
apply_migration.py - Crée les tables users + medical_documents dans Supabase
puis insère 10 profils patients
"""
import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PATIENTS = [
    {"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "full_name": "Alim ZATO",        "role": "Patient",    "date_of_birth": "1995-06-14", "email": "alim.zato@email.fr",          "phone": "+33 6 12 34 56 78"},
    {"id": "b1ffcd88-8d1c-4fa9-cc7e-7cc0ce491b22", "full_name": "Jean DUPONT",       "role": "Médecin",   "date_of_birth": "1978-03-22", "email": "dr.dupont@medvault.fr",       "phone": "+33 6 98 76 54 32"},
    {"id": "c2aaef77-7e2b-4ab8-bd8f-8dd1df582c33", "full_name": "Marie MARTIN",      "role": "Patient",    "date_of_birth": "1989-11-05", "email": "marie.martin@email.fr",       "phone": "+33 7 23 45 67 89"},
    {"id": "d3bbfe66-6f3c-4bc7-ae9e-9ee2ef693d44", "full_name": "Pierre BERNARD",    "role": "Patient",    "date_of_birth": "1965-07-30", "email": "pierre.bernard@email.fr",     "phone": "+33 6 34 56 78 90"},
    {"id": "e4ccad55-5a4d-4cd6-bf0f-0ff3fa7a4e55", "full_name": "Sophie LEFEBVRE",   "role": "Infirmière", "date_of_birth": "1990-02-18", "email": "sophie.lefebvre@clinique.fr", "phone": "+33 6 45 67 89 01"},
    {"id": "f5ddbe44-4b5e-4de5-ca1a-1aa4ab8b5f66", "full_name": "Mohamed DIALLO",    "role": "Patient",    "date_of_birth": "1982-09-12", "email": "mohamed.diallo@email.fr",     "phone": "+33 7 56 78 90 12"},
    {"id": "a6eecf33-3c6f-4ef4-bb2b-2bb5bc9c6a77", "full_name": "Camille ROUSSEAU",  "role": "Patient",    "date_of_birth": "2001-04-25", "email": "camille.rousseau@email.fr",   "phone": "+33 6 67 89 01 23"},
    {"id": "b7fada22-2d7a-4fa3-ac3c-3cc6cd0d7b88", "full_name": "Thomas MOREAU",     "role": "Médecin",   "date_of_birth": "1974-12-08", "email": "dr.moreau@medvault.fr",       "phone": "+33 6 78 90 12 34"},
    {"id": "c8abeb11-1e8b-4ab2-bd4d-4dd7de1e8c99", "full_name": "Fatima BENALI",     "role": "Patient",    "date_of_birth": "1998-08-17", "email": "fatima.benali@email.fr",      "phone": "+33 7 89 01 23 45"},
    {"id": "d9bcfc00-0f9c-4bc1-ae5e-5ee8ef2f9d00", "full_name": "Lucas SIMON",       "role": "Patient",    "date_of_birth": "1975-01-03", "email": "lucas.simon@email.fr",        "phone": "+33 6 90 12 34 56"},
]

print("=" * 60)
print("  MedVault Pro — Migration + Seed des utilisateurs")
print("=" * 60)

print("\n[1] Insertion des 10 profils dans public.users (upsert)...")
try:
    res = supabase.table("users").upsert(PATIENTS, on_conflict="id").execute()
    print(f"    ✅ {len(res.data)} profil(s) insérés/mis à jour.")
except Exception as e:
    print(f"    ❌ Erreur : {e}")
    print("\n    → La table 'users' n'existe peut-être pas encore.")
    print("    → Exécutez d'abord migration.sql dans l'éditeur SQL Supabase.")
    sys.exit(1)

print("\n[2] Vérification...")
check = supabase.table("users").select("id, full_name, role").order("full_name").execute()
for u in check.data:
    print(f"    • {u['full_name']:<22} ({u['role']:<12}) {u['id'][:8]}...")

print(f"\n✅ {len(check.data)} utilisateurs disponibles dans la base.")
print("=" * 60)
