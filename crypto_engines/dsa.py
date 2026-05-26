# crypto_engines/dsa.py
# Moteur de signatures asymétriques DSA (Digital Signature Algorithm)
# Algorithme historique de signature numérique (non conçu pour le chiffrement).

from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

class DSAEngine:
    """
    Implémentation standard de DSA.
    DSA est un standard fédéral américain (FIPS) conçu uniquement pour les signatures.
    Il ne permet pas le chiffrement de données.
    Bien qu'ayant été un standard majeur, le NIST l'a officiellement retiré en 2023
    au profit d'algorithmes plus modernes comme l'ECDSA (courbes elliptiques).
    """

    @staticmethod
    def generate_keypair() -> tuple[dsa.DSAPrivateKey, dsa.DSAPublicKey]:
        """Génère une paire de clés DSA de 2048 bits (sécurité standard)."""
        private_key = dsa.generate_private_key(
            key_size=2048,
            backend=default_backend()
        )
        return private_key, private_key.public_key()

    @staticmethod
    def serialize_public_key(public_key: dsa.DSAPublicKey) -> bytes:
        """Sérialise la clé publique au format PEM."""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def serialize_private_key(private_key: dsa.DSAPrivateKey) -> bytes:
        """Sérialise la clé privée au format PEM."""
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    @staticmethod
    def deserialize_public_key(pem_data: bytes) -> dsa.DSAPublicKey:
        """Recharge une clé publique à partir de son format PEM."""
        return serialization.load_pem_public_key(pem_data, backend=default_backend())

    @staticmethod
    def deserialize_private_key(pem_data: bytes) -> dsa.DSAPrivateKey:
        """Recharge une clé privée à partir de son format PEM."""
        return serialization.load_pem_private_key(pem_data, password=None, backend=default_backend())

    @staticmethod
    def sign(message: bytes, private_key: dsa.DSAPrivateKey) -> bytes:
        """Signe numériquement un message avec la clé privée (Authentification)."""
        return private_key.sign(
            message,
            hashes.SHA256()
        )

    @staticmethod
    def verify(message: bytes, signature: bytes, public_key: dsa.DSAPublicKey) -> bool:
        """Vérifie la validité d'une signature numérique avec la clé publique (Non-répudiation)."""
        try:
            public_key.verify(signature, message, hashes.SHA256())
            return True
        except Exception:
            return False

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO DSA-2048 ---")
    data = b"Rapport d'autopsie medicale authentifie"
    
    priv, pub = DSAEngine.generate_keypair()
    pem_pub = DSAEngine.serialize_public_key(pub)
    print(f"Cle publique DSA PEM :\n{pem_pub.decode()[:150]}...\n")
    
    # Signature et vérification
    sig = DSAEngine.sign(data, priv)
    print(f"Signature DSA generee (hex) : {sig.hex()[:80]}...")
    
    is_valid = DSAEngine.verify(data, sig, pub)
    print(f"Signature valide ? {is_valid}")
