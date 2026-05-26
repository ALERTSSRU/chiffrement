# crypto_engines/rsa.py
# Moteur de chiffrement RSA (Rivest-Shamir-Adleman)
# Algorithme asymétrique standard mondial pour l'échange de clés et les signatures.

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

class RSAEngine:
    """
    Implémentation standard de RSA-2048.
    RSA utilise une clé publique pour chiffrer et une clé privée pour déchiffrer.
    C'est la base de la sécurisation des échanges sur Internet (HTTPS, SSH).
    """

    @staticmethod
    def generate_keypair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Génère une paire de clés publique/privée RSA de 2048 bits."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        return private_key, private_key.public_key()

    @staticmethod
    def serialize_private_key(private_key: rsa.RSAPrivateKey) -> bytes:
        """Sérialise la clé privée au format PEM standard (non chiffrée pour la démo)."""
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    @staticmethod
    def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
        """Sérialise la clé publique au format PEM standard (pour partage)."""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def deserialize_private_key(pem_data: bytes) -> rsa.RSAPrivateKey:
        """Charge une clé privée à partir de son format PEM."""
        return serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )

    @staticmethod
    def deserialize_public_key(pem_data: bytes) -> rsa.RSAPublicKey:
        """Charge une clé publique à partir de son format PEM."""
        return serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )

    @staticmethod
    def encrypt(plaintext: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """
        Chiffre les données en utilisant la clé publique.
        Utilise OAEP Padding avec SHA-256 (recommandé par l'ANSSI/NIST).
        """
        return public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    @staticmethod
    def decrypt(ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """Déchiffre les données en utilisant la clé privée."""
        return private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO RSA-2048 ---")
    data = b"Notes medicales secretes transmises par RSA"
    
    # 1. Génération et sérialisation
    priv_key, pub_key = RSAEngine.generate_keypair()
    pem_priv = RSAEngine.serialize_private_key(priv_key)
    pem_pub = RSAEngine.serialize_public_key(pub_key)
    
    print(f"Cle publique PEM :\n{pem_pub.decode()[:150]}...\n")
    
    # 2. Rechargement des clés (pour simuler la réception réseau)
    loaded_pub = RSAEngine.deserialize_public_key(pem_pub)
    loaded_priv = RSAEngine.deserialize_private_key(pem_priv)
    
    # 3. Chiffrement (avec clé publique) et Déchiffrement (avec clé privée)
    ct = RSAEngine.encrypt(data, loaded_pub)
    print(f"Texte chiffré (hex) : {ct.hex()[:100]}... (longueur : {len(ct)} octets)")
    
    pt = RSAEngine.decrypt(ct, loaded_priv)
    print(f"Texte déchiffré : {pt.decode()}")
