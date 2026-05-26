# crypto_engines/blake2.py
# Moteur de Hachage BLAKE2b
# Algorithme moderne, extrêmement robuste et ultra-rapide.

import hashlib

class BLAKE2Engine:
    """
    Implémentation standard de BLAKE2b.
    BLAKE2b est basé sur ChaCha20 et est optimisé pour les processeurs 64 bits.
    Il est aussi robuste que SHA-3 mais offre des vitesses d'exécution exceptionnelles,
    surpassant largement SHA-256 et même l'historique MD5.
    """

    @staticmethod
    def hash(data: bytes) -> str:
        """Calcule l'empreinte BLAKE2b (hexadécimale de 128 caractères)."""
        return hashlib.blake2b(data).hexdigest()

    @staticmethod
    def verify(data: bytes, expected_hash: str) -> bool:
        """Vérifie si les données correspondent à l'empreinte."""
        return BLAKE2Engine.hash(data) == expected_hash

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO BLAKE2b ---")
    data = b"Dossier medical de test"
    
    h = BLAKE2Engine.hash(data)
    print(f"Donnees : '{data.decode()}'")
    print(f"Empreinte BLAKE2b (128 char) : {h}")
    
    print(f"Verification reussie ? {BLAKE2Engine.verify(data, h)}")
