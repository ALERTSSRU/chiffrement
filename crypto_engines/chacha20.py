# crypto_engines/chacha20.py
# Moteur de chiffrement ChaCha20
# Algorithme symétrique par flux moderne et ultra-rapide.

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend

class ChaCha20Engine:
    """
    Implémentation standard de ChaCha20.
    ChaCha20 est un chiffrement par flux moderne et extrêmement rapide.
    Il est largement adopté (IETF, TLS 1.3, Android, SSH) et n'a aucune faille connue.
    """

    @staticmethod
    def generate_key() -> bytes:
        """Génère une clé de 256 bits (32 octets)."""
        return os.urandom(32)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
        """
        Chiffre les données en utilisant ChaCha20.
        Puisqu'il s'agit d'un chiffrement par flux, aucun padding n'est requis.
        Retourne : (ciphertext, nonce)
        - nonce : Nombre de 16 octets à usage unique.
        """
        if len(key) != 32:
            raise ValueError("La clé ChaCha20 doit faire exactement 32 octets.")
            
        nonce = os.urandom(16)  # Nonce de 16 octets
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return ciphertext, nonce

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
        """Déchiffre les données ChaCha20 avec la clé et le nonce associés."""
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO ChaCha20 ---")
    data = b"Notes medicales secretes de ChaCha20"
    key = ChaCha20Engine.generate_key()
    print(f"Cle générée (hex) : {key.hex()}")
    
    ct, nonce = ChaCha20Engine.encrypt(data, key)
    print(f"Texte chiffré (hex) : {ct.hex()}")
    print(f"Nonce (hex) : {nonce.hex()}")
    
    pt = ChaCha20Engine.decrypt(ct, key, nonce)
    print(f"Texte déchiffré : {pt.decode()}")
