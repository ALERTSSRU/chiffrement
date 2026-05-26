# crypto_engines/blowfish.py
# Moteur de chiffrement Blowfish
# OBSOLÈTE - Utilisé à but éducatif et historique.

import os
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

try:
    from cryptography.hazmat.primitives.ciphers.algorithms import Blowfish
except (ImportError, AttributeError):
    Blowfish = None

class BlowfishEngine:
    """
    Implémentation de Blowfish en mode CBC.
    Blowfish est un algorithme de blocs historique conçu en 1993.
    Sa taille de bloc de 64 bits le rend vulnérable aux attaques de collision.
    Il est aujourd'hui déconseillé, remplacé par Twofish et AES.
    """

    @staticmethod
    def is_supported() -> bool:
        """Indique si Blowfish est supporté."""
        return Blowfish is not None

    @staticmethod
    def generate_key() -> bytes:
        """Génère une clé de 128 bits (16 octets). Clé variable de 32 à 448 bits."""
        return os.urandom(16)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """Chiffre les données en Blowfish-CBC avec padding PKCS7."""
        if not BlowfishEngine.is_supported():
            raise NotImplementedError("Blowfish n'est pas supporté par votre environnement local.")
            
        if not (4 <= len(key) <= 56):
            raise ValueError("La clé Blowfish doit faire entre 4 et 56 octets (32 à 448 bits).")

        # Padding PKCS7 à 64 bits (taille de bloc Blowfish)
        padder = padding.PKCS7(64).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        iv = os.urandom(8)  # Vecteur d'initialisation de 8 octets
        cipher = Cipher(Blowfish(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, iv

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Déchiffre les données en Blowfish-CBC."""
        if not BlowfishEngine.is_supported():
            raise NotImplementedError("Blowfish n'est pas supporté par votre environnement local.")
            
        cipher = Cipher(Blowfish(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(64).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO Blowfish ---")
    if not BlowfishEngine.is_supported():
        print("[ALERTE] Blowfish n'est pas supporté.")
    else:
        data = b"Notes medicales secretes de Blowfish"
        key = BlowfishEngine.generate_key()
        print(f"Cle générée (hex) : {key.hex()}")
        
        ct, iv = BlowfishEngine.encrypt(data, key)
        print(f"Texte chiffré (hex) : {ct.hex()}")
        print(f"IV (hex) : {iv.hex()}")
        
        pt = BlowfishEngine.decrypt(ct, key, iv)
        print(f"Texte déchiffré : {pt.decode()}")
