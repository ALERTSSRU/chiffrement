# crypto.py
# Module de chiffrement côté serveur (Server-Side Encryption)
# Utilise Fernet (AES-128 en mode CBC avec signature HMAC) pour chiffrer/déchiffrer les textes simplement.

from cryptography.fernet import Fernet
from config import settings

class ServerCrypto:
    """Gestion du chiffrement/déchiffrement avec la clé maîtresse du serveur."""
    
    _fernet = Fernet(settings.ENCRYPTION_MASTER_KEY.encode())

    @classmethod
    def encrypt_text(cls, plain_text: str) -> str:
        """
        Chiffre une chaîne de caractères en clair.
        Retourne la chaîne chiffrée (base64 URL-safe).
        """
        # Fernet prend des bytes, on doit encoder la string
        encrypted_bytes = cls._fernet.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    @classmethod
    def decrypt_text(cls, cipher_text: str) -> str:
        """
        Déchiffre une chaîne chiffrée.
        Retourne la chaîne en clair d'origine.
        """
        decrypted_bytes = cls._fernet.decrypt(cipher_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
