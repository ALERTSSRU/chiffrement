# crypto_engines/aes.py
# Moteur de chiffrement AES (Advanced Encryption Standard)
# Mode recommandé : GCM (Galois/Counter Mode) pour le chiffrement authentifié (AEAD)

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AESEngine:
    """
    Implémentation standard de l'AES-256 en mode GCM.
    AES est le standard mondial recommandé par l'ANSSI, le NIST et le RGPD.
    """
    
    @staticmethod
    def generate_key() -> bytes:
        """Génère une clé de 256 bits (32 octets)."""
        return os.urandom(32)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
        """
        Chiffre les données en utilisant AES-256-GCM.
        Retourne : (ciphertext, nonce, tag)
        - nonce : Nombre utilisé une seule fois (96 bits) pour éviter la répétition.
        - tag : Code d'authentification pour garantir que le texte n'a pas été altéré.
        """
        if len(key) != 32:
            raise ValueError("La clé AES-256 doit faire exactement 32 octets.")
            
        nonce = os.urandom(12)  # Nonce standard de 12 octets pour GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return ciphertext, nonce, encryptor.tag

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
        """
        Déchiffre les données et valide le tag d'authentification.
        Lève une erreur si les données ont été altérées.
        """
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO AES-256-GCM ---")
    data = b"Notes medicales secretes d'AES"
    
    key = AESEngine.generate_key()
    print(f"Cle générée (hex) : {key.hex()}")
    
    ct, nonce, tag = AESEngine.encrypt(data, key)
    print(f"Texte chiffré (hex) : {ct.hex()}")
    print(f"Nonce (hex) : {nonce.hex()}")
    print(f"Tag (hex) : {tag.hex()}")
    
    pt = AESEngine.decrypt(ct, key, nonce, tag)
    print(f"Texte déchiffré : {pt.decode()}")
