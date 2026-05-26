# crypto_engines/md5.py
# Moteur de Hachage MD5 (Message Digest 5)
# CASSÉ / OBSOLÈTE - Utilisé à but éducatif. Ne pas utiliser en production.

import hashlib

class MD5Engine:
    """
    Implémentation standard de MD5.
    MD5 est un algorithme historique de 128 bits (32 caractères hexa).
    Il a été complètement brisé en 2004 (collisions faciles à générer en quelques secondes).
    Il est strictement interdit pour toute application de sécurité,
    mais reste parfois utilisé pour de simples vérifications d'intégrité non sécurisées (checksums).
    """

    @staticmethod
    def hash(data: bytes) -> str:
        """Calcule l'empreinte MD5."""
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def verify(data: bytes, expected_hash: str) -> bool:
        """Vérifie l'empreinte."""
        return MD5Engine.hash(data) == expected_hash

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO MD5 ---")
    data = b"Dossier medical de test"
    
    h = MD5Engine.hash(data)
    print(f"Donnees : '{data.decode()}'")
    print(f"Empreinte MD5 : {h}")
    
    print(f"Verification reussie ? {MD5Engine.verify(data, h)}")
