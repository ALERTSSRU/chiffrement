# crypto_engines/sha256.py
# Moteur de Hachage SHA-256 (Secure Hash Algorithm 256 bits)
# Standard mondial pour l'intégrité des données et la dérivation.

import hashlib

class SHA256Engine:
    """
    Implémentation standard de SHA-256 (famille SHA-2).
    SHA-256 prend un message d'entrée de n'importe quelle taille
    et produit une empreinte unique fixe de 256 bits (32 octets).
    Il est jugé totalement sûr (aucune collision pratique trouvée).
    """

    @staticmethod
    def hash(data: bytes) -> str:
        """Calcule l'empreinte SHA-256 et la retourne sous forme de chaîne hexadécimale (64 caractères)."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify(data: bytes, expected_hash: str) -> bool:
        """Vérifie si les données fournies correspondent à l'empreinte attendue."""
        return SHA256Engine.hash(data) == expected_hash

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO SHA-256 ---")
    data = b"Dossier medical de test"
    
    h = SHA256Engine.hash(data)
    print(f"Donnees : '{data.decode()}'")
    print(f"Empreinte SHA-256 : {h}")
    
    print(f"Verification reussie ? {SHA256Engine.verify(data, h)}")
