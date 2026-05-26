# crypto_engines/sha3.py
# Moteur de Hachage SHA3-256 (Secure Hash Algorithm 3)
# Algorithme de hachage de nouvelle génération basé sur l'architecture Keccak.

import hashlib

class SHA3Engine:
    """
    Implémentation standard de SHA3-256 (famille SHA-3).
    Sélectionné par le NIST en 2012 après une compétition publique mondiale.
    Il utilise une structure de 'fonction éponge' (sponge function) radicalement
    différente de SHA-2, le rendant immunisé contre les attaques théoriques sur SHA-2.
    """

    @staticmethod
    def hash(data: bytes) -> str:
        """Calcule l'empreinte SHA3-256 (hexadécimale de 64 caractères)."""
        return hashlib.sha3_256(data).hexdigest()

    @staticmethod
    def verify(data: bytes, expected_hash: str) -> bool:
        """Vérifie si les données correspondent à l'empreinte attendue."""
        return SHA3Engine.hash(data) == expected_hash

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO SHA3-256 ---")
    data = b"Dossier medical de test"
    
    h = SHA3Engine.hash(data)
    print(f"Donnees : '{data.decode()}'")
    print(f"Empreinte SHA3-256 : {h}")
    
    print(f"Verification reussie ? {SHA3Engine.verify(data, h)}")
