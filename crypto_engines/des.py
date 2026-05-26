# crypto_engines/des.py
# Moteur de chiffrement DES (Data Encryption Standard)
# OBSOLÈTE - Utilisé à but éducatif. Ne pas utiliser en production.

import os
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Gestion dynamique des imports pour les versions récentes de cryptography (Python 3.13+)
# DES ayant été jugé trop dangereux, il a été déplacé dans le sous-module 'decrepit'
try:
    from cryptography.hazmat.primitives.ciphers.algorithms import DES
except (ImportError, AttributeError):
    try:
        from cryptography.hazmat.decrepit.ciphers.algorithms import DES
    except ImportError:
        DES = None

class DESEngine:
    """
    Implémentation de DES en mode CBC.
    DES est un algorithme historique obsolète avec une clé de 56 bits.
    Il est sensible aux attaques par force brute (décrypté en quelques heures).
    """

    @staticmethod
    def is_supported() -> bool:
        """Indique si DES est pris en charge par l'environnement actuel."""
        return DES is not None

    @staticmethod
    def generate_key() -> bytes:
        """Génère une clé de 64 bits (8 octets, dont 56 bits effectifs)."""
        return os.urandom(8)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """
        Chiffre les données avec DES-CBC.
        DES requiert des blocs de 8 octets, donc du padding PKCS7 est ajouté.
        """
        if not DESEngine.is_supported():
            raise NotImplementedError("DES n'est pas supporté par votre installation Python moderne (désactivé par sécurité).")
            
        if len(key) != 8:
            raise ValueError("La clé DES doit faire exactement 8 octets.")

        # Padding PKCS7 pour obtenir des blocs de 8 octets (64 bits)
        padder = padding.PKCS7(64).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        iv = os.urandom(8)  # Vecteur d'initialisation de 8 octets
        cipher = Cipher(DES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, iv

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Déchiffre les données DES-CBC et retire le padding PKCS7."""
        if not DESEngine.is_supported():
            raise NotImplementedError("DES n'est pas supporté par votre installation Python moderne (désactivé par sécurité).")
            
        cipher = Cipher(DES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(64).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO DES ---")
    if not DESEngine.is_supported():
        print("[ALERTE] DES n'est pas disponible de base sur ce système (trop dangereux).")
    else:
        data = b"Notes medicales secretes de DES"
        key = DESEngine.generate_key()
        print(f"Cle générée (hex) : {key.hex()}")
        
        ct, iv = DESEngine.encrypt(data, key)
        print(f"Texte chiffré (hex) : {ct.hex()}")
        print(f"IV (hex) : {iv.hex()}")
        
        pt = DESEngine.decrypt(ct, key, iv)
        print(f"Texte déchiffré : {pt.decode()}")
