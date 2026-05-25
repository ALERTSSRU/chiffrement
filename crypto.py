# crypto.py
# Module cryptographique complet : hachage, chiffrement symétrique et asymétrique.
# Fournit les fonctions pour sécuriser les données sensibles stockées en base de données.

import hashlib
import hmac
import time
from typing import Dict, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

# ============================================================================
# SECTION 1 : FONCTIONS DE HACHAGE
# ============================================================================

class HashAlgorithm:
    """Interface pour les algorithmes de hachage."""
    
    @staticmethod
    def sha256(data: bytes) -> str:
        """
        Hachage SHA-256 (NIST).
        Usage : Hachage de mots de passe, dérivation de clés.
        Sécurité : ⭐⭐⭐⭐⭐ (Recommandé pour production)
        """
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha3_256(data: bytes) -> str:
        """
        Hachage SHA-3 256 (Keccak, gagnant Cryptographic Hash Algorithm Competition).
        Usage : Intégrité de données, signatures numériques.
        Sécurité : ⭐⭐⭐⭐⭐ (Meilleur que SHA-2)
        """
        return hashlib.sha3_256(data).hexdigest()
    
    @staticmethod
    def blake2b(data: bytes, digest_size: int = 64) -> str:
        """
        Hachage BLAKE2b (Swiss Army Knife of hashing, RFC 7693).
        Usage : Performance et sécurité, hachage haute performance.
        Sécurité : ⭐⭐⭐⭐⭐ (Excellent, plus rapide que SHA-3)
        """
        return hashlib.blake2b(data, digest_size=digest_size).hexdigest()
    
    @staticmethod
    def md5(data: bytes) -> str:
        """
        Hachage MD5 (DEPRECATED - À ne pas utiliser pour la sécurité).
        Usage : Vérification d'intégrité simple, empreintes non-sécurisées.
        Sécurité : ⭐ (DÉPRÉCIÉ - Collisions connues, ne pas utiliser en production)
        """
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def hmac_sha256(key: bytes, data: bytes) -> str:
        """
        HMAC-SHA256 pour l'authentification de message.
        Garantit que le message n'a pas été modifié ET provient de la clé connue.
        """
        return hmac.new(key, data, hashlib.sha256).hexdigest()


# ============================================================================
# SECTION 2 : CHIFFREMENT SYMÉTRIQUE
# ============================================================================

class SymmetricEncryption:
    """Chiffrement symétrique avec AES."""
    
    @staticmethod
    def generate_key(size: int = 256) -> bytes:
        """Génère une clé aléatoire (128, 192, ou 256 bits)."""
        return os.urandom(size // 8)
    
    @staticmethod
    def encrypt_aes_gcm(plaintext: bytes, key: bytes, nonce: bytes = None) -> Tuple[str, str]:
        """
        Chiffrement AES-GCM (Authenticated Encryption).
        Retourne : (ciphertext_base64, nonce_base64)
        """
        if nonce is None:
            nonce = os.urandom(12)  # 96 bits pour GCM
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return base64.b64encode(ciphertext + encryptor.tag).decode(), base64.b64encode(nonce).decode()
    
    @staticmethod
    def decrypt_aes_gcm(ciphertext_base64: str, nonce_base64: str, key: bytes) -> bytes:
        """Déchiffrement AES-GCM."""
        ciphertext_with_tag = base64.b64decode(ciphertext_base64)
        nonce = base64.b64decode(nonce_base64)
        
        # Séparer le ciphertext et l'authentification tag
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()


# ============================================================================
# SECTION 3 : CHIFFREMENT ASYMÉTRIQUE
# ============================================================================

class AsymmetricEncryption:
    """Chiffrement asymétrique avec RSA."""
    
    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> Tuple[str, str]:
        """
        Génère une paire de clés RSA (public/privé).
        Retourne : (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        from cryptography.hazmat.primitives import serialization
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return private_pem, public_pem
    
    @staticmethod
    def rsa_encrypt(plaintext: bytes, public_key_pem: str) -> str:
        """Chiffrement RSA avec OAEP."""
        from cryptography.hazmat.primitives import serialization
        
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode()
    
    @staticmethod
    def rsa_decrypt(ciphertext_base64: str, private_key_pem: str) -> bytes:
        """Déchiffrement RSA."""
        from cryptography.hazmat.primitives import serialization
        
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        ciphertext = base64.b64decode(ciphertext_base64)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext


# ============================================================================
# SECTION 4 : TABLEAU COMPARATIF DE PERFORMANCE
# ============================================================================

class CryptoBenchmark:
    """Benchmark des performances cryptographiques."""
    
    COMPARISON_TABLE = {
        "hash_algorithms": [
            {
                "name": "SHA-256",
                "speed": "⚡⚡⚡⚡",
                "security": "⭐⭐⭐⭐⭐",
                "output": "256 bits (32 octets)",
                "use_case": "Hachage standard, dérivation de clés",
                "status": "✅ Production"
            },
            {
                "name": "SHA-3",
                "speed": "⚡⚡⚡",
                "security": "⭐⭐⭐⭐⭐",
                "output": "256 bits (32 octets)",
                "use_case": "Alternative plus sécurisée à SHA-2",
                "status": "✅ Production"
            },
            {
                "name": "BLAKE2b",
                "speed": "⚡⚡⚡⚡⚡",
                "security": "⭐⭐⭐⭐⭐",
                "output": "512 bits (64 octets)",
                "use_case": "Performance extrême + sécurité",
                "status": "✅ Production"
            },
            {
                "name": "MD5",
                "speed": "⚡⚡⚡⚡⚡",
                "security": "⭐",
                "output": "128 bits (16 octets)",
                "use_case": "❌ DÉPRÉCIÉ (collisions connues)",
                "status": "🚫 Ne pas utiliser"
            }
        ],
        "symmetric_encryption": [
            {
                "name": "AES-256-GCM",
                "speed": "⚡⚡⚡⚡",
                "security": "⭐⭐⭐⭐⭐",
                "key_size": "256 bits",
                "mode": "GCM (Authenticated Encryption)",
                "use_case": "Chiffrement données sensibles",
                "status": "✅ Production"
            }
        ],
        "asymmetric_encryption": [
            {
                "name": "RSA-2048",
                "speed": "⚡⚡",
                "security": "⭐⭐⭐⭐",
                "key_size": "2048 bits",
                "padding": "OAEP + SHA-256",
                "use_case": "Échange de clés, signatures",
                "status": "✅ Production"
            },
            {
                "name": "RSA-4096",
                "speed": "⚡",
                "security": "⭐⭐⭐⭐⭐",
                "key_size": "4096 bits",
                "padding": "OAEP + SHA-256",
                "use_case": "Ultra-sécurité long terme",
                "status": "✅ Production"
            }
        ]
    }
    
    @staticmethod
    def benchmark_hash_algorithms() -> Dict:
        """Teste la performance des algorithmes de hachage."""
        test_data = b"This is a test document for hashing performance comparison." * 100
        results = {}
        
        algorithms = [
            ("SHA-256", HashAlgorithm.sha256),
            ("SHA-3-256", HashAlgorithm.sha3_256),
            ("BLAKE2b", HashAlgorithm.blake2b),
            ("MD5", HashAlgorithm.md5),
        ]
        
        for name, func in algorithms:
            start = time.time()
            for _ in range(10000):
                func(test_data)
            elapsed = time.time() - start
            results[name] = f"{elapsed:.4f}s (pour 10k iterations)"
        
        return results
    
    @staticmethod
    def get_comparison_table() -> Dict:
        """Retourne le tableau comparatif complet."""
        return CryptoBenchmark.COMPARISON_TABLE
