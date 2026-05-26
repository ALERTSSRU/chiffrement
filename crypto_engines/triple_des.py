# crypto_engines/triple_des.py
# Moteur de chiffrement 3DES (Triple Data Encryption Standard)
# DÉPRÉCIÉ - Utilisé à but éducatif et historique.

import os
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Gestion dynamique des imports pour TripleDES
try:
    from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
except (ImportError, AttributeError):
    try:
        from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
    except ImportError:
        TripleDES = None

class TripleDESEngine:
    """
    Implémentation de TripleDES (3DES) en mode CBC.
    3DES applique 3 fois l'algorithme DES pour augmenter la clé à 168 bits.
    Bien que plus sûr que DES, il est très lent et officiellement déprécié par le NIST fin 2023.
    """

    @staticmethod
    def is_supported() -> bool:
        """Indique si 3DES est supporté."""
        return TripleDES is not None

    @staticmethod
    def generate_key() -> bytes:
        """Génère une clé de 192 bits (24 octets, dont 168 bits effectifs)."""
        return os.urandom(24)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """Chiffre les données en 3DES-CBC avec padding PKCS7."""
        if not TripleDESEngine.is_supported():
            raise NotImplementedError("TripleDES n'est pas supporté par votre environnement local.")
            
        if len(key) != 24:
            raise ValueError("La clé TripleDES doit faire exactement 24 octets (3 clés de 8 octets).")

        # Padding PKCS7 à 64 bits (taille de bloc 3DES)
        padder = padding.PKCS7(64).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        iv = os.urandom(8)  # Vecteur d'initialisation de 8 octets
        cipher = Cipher(TripleDES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, iv

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Déchiffre les données en 3DES-CBC."""
        if not TripleDESEngine.is_supported():
            raise NotImplementedError("TripleDES n'est pas supporté par votre environnement local.")
            
        cipher = Cipher(TripleDES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(64).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO TripleDES ---")
    if not TripleDESEngine.is_supported():
        print("[ALERTE] TripleDES n'est pas supporté.")
    else:
        data = b"Notes medicales secretes de 3DES"
        key = TripleDESEngine.generate_key()
        print(f"Cle générée (hex) : {key.hex()}")
        
        ct, iv = TripleDESEngine.encrypt(data, key)
        print(f"Texte chiffré (hex) : {ct.hex()}")
        print(f"IV (hex) : {iv.hex()}")
        
        pt = TripleDESEngine.decrypt(ct, key, iv)
        print(f"Texte déchiffré : {pt.decode()}")
