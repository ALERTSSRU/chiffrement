# crypto_engines/ecc.py
# Moteur de cryptographie sur courbes elliptiques (ECC - Elliptic Curve Cryptography)
# Courbe recommandée : SECP256R1 (NIST P-256)
# Fournit ECDSA (signatures) et ECDH (échange de clés sécurisé).

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

class ECCEngine:
    """
    Implémentation standard d'ECC (ECDSA et ECDH).
    ECC offre le même niveau de sécurité que RSA mais avec des clés beaucoup plus petites,
    ce qui le rend infiniment plus rapide et économe en batterie (idéal pour mobile/IoT).
    """

    @staticmethod
    def generate_keypair() -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        """Génère une paire de clés ECC sur la courbe standard SECP256R1."""
        private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
        return private_key, private_key.public_key()

    @staticmethod
    def serialize_public_key(public_key: ec.EllipticCurvePublicKey) -> bytes:
        """Sérialise la clé publique ECC au format PEM."""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def serialize_private_key(private_key: ec.EllipticCurvePrivateKey) -> bytes:
        """Sérialise la clé privée ECC au format PEM."""
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    @staticmethod
    def deserialize_public_key(pem_data: bytes) -> ec.EllipticCurvePublicKey:
        """Recharge une clé publique ECC à partir de son format PEM."""
        return serialization.load_pem_public_key(pem_data, backend=default_backend())

    @staticmethod
    def deserialize_private_key(pem_data: bytes) -> ec.EllipticCurvePrivateKey:
        """Recharge une clé privée ECC à partir de son format PEM."""
        return serialization.load_pem_private_key(pem_data, password=None, backend=default_backend())

    # --- ECDSA : Signatures numériques ---

    @staticmethod
    def sign(message: bytes, private_key: ec.EllipticCurvePrivateKey) -> bytes:
        """Signe numériquement un message avec la clé privée ECC (Authenticité)."""
        return private_key.sign(
            message,
            ec.ECDSA(hashes.SHA256())
        )

    @staticmethod
    def verify(message: bytes, signature: bytes, public_key: ec.EllipticCurvePublicKey) -> bool:
        """
        Vérifie la signature avec la clé publique.
        Retourne True si valide, False sinon (Non-répudiation et Intégrité).
        """
        try:
            public_key.verify(
                signature,
                message,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    # --- ECDH : Échange de clés Diffie-Hellman ---

    @staticmethod
    def compute_shared_secret(private_key: ec.EllipticCurvePrivateKey, peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
        """
        Calcule un secret partagé unique (ECDH) entre deux entités.
        Exemple : Le docteur utilise sa clé privée + la clé publique du patient.
        Le patient utilise sa clé privée + la clé publique du docteur.
        Les deux obtiendront exactement le même secret partagé !
        """
        shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
        
        # Dérivation du secret brut en une clé symétrique exploitable (AES-256) via HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"medical-dossier-encryption-key",
            backend=default_backend()
        ).derive(shared_key)
        
        return derived_key

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO ECC (ECDSA & ECDH) ---")
    data = b"Rapport cardiologique confidentiel"
    
    # 1. Test de Signature ECDSA
    print("[+] Test ECDSA (Signature) :")
    priv, pub = ECCEngine.generate_keypair()
    sig = ECCEngine.sign(data, priv)
    print(f"  Signature générée (hex) : {sig.hex()[:80]}...")
    
    is_valid = ECCEngine.verify(data, sig, pub)
    print(f"  Signature valide ? {is_valid}")
    
    # 2. Test d'échange de clés ECDH (Docteur <-> Patient)
    print("\n[+] Test ECDH (Échange de clés) :")
    doc_priv, doc_pub = ECCEngine.generate_keypair()      # Paire du Docteur
    pat_priv, pat_pub = ECCEngine.generate_keypair()      # Paire du Patient
    
    # Le Docteur calcule le secret avec la clé publique du Patient
    secret_docteur = ECCEngine.compute_shared_secret(doc_priv, pat_pub)
    
    # Le Patient calcule le secret avec la clé publique du Docteur
    secret_patient = ECCEngine.compute_shared_secret(pat_priv, doc_pub)
    
    print(f"  Clé dérivée Docteur (hex) : {secret_docteur.hex()}")
    print(f"  Clé dérivée Patient (hex) : {secret_patient.hex()}")
    print(f"  Clés identiques ? {secret_docteur == secret_patient}")
