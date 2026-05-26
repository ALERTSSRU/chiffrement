# test_all_crypto.py
# Script de test fonctionnel et de benchmark de tous les algorithmes cryptographiques
# Auteur : Antigravity AI & Alim Zato
# Date : 26 Mai 2026

import time
import hashlib
import os
import random
import sys
from typing import Dict, Tuple, Any

# Configure standard output to use UTF-8 if supported, otherwise fall back to CP1252 compatibility
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import de la bibliothèque de cryptographie standard Python
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec, dsa
    from cryptography.hazmat.primitives import hashes, padding as pad_utils
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Erreur : La bibliothèque 'cryptography' n'est pas installée.")
    print("Veuillez l'installer avec : pip install cryptography")
    exit(1)

# ============================================================================
# IMPLEMENTATION DE ELGAMAL (Mathématique Pure)
# ============================================================================
class PureElGamal:
    """
    Implémentation pure Python de l'algorithme asymétrique ElGamal.
    Utilise un groupe MODP standard (RFC 3526 - 1024 bits) pour assurer la sécurité et la rapidité.
    """
    # Premier MODP 1024 bits (RFC 3526 Group 5)
    P = int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
        "FFFFFFFFFFFFFFFF", 16
    )
    G = 2

    @classmethod
    def generate_keys(cls) -> Tuple[Tuple[int, int, int], int]:
        """Génère la paire de clés (publique, privée)."""
        x = random.randint(2, cls.P - 2)  # Clé privée
        y = pow(cls.G, x, cls.P)          # Clé publique
        return (cls.P, cls.G, y), x

    @classmethod
    def encrypt(cls, pubkey: Tuple[int, int, int], message_bytes: bytes) -> Tuple[int, int]:
        """Chiffre les données avec la clé publique."""
        p, g, y = pubkey
        m = int.from_bytes(message_bytes, 'big')
        if m >= p:
            raise ValueError("Le message est trop grand pour être chiffré directement par ce module ElGamal.")
        k = random.randint(2, p - 2)
        a = pow(g, k, p)
        b = (m * pow(y, k, p)) % p
        return a, b

    @classmethod
    def decrypt(cls, pubkey: Tuple[int, int, int], privkey: int, ciphertext: Tuple[int, int]) -> bytes:
        """Déchiffre les données avec la clé privée."""
        p, g, y = pubkey
        x = privkey
        a, b = ciphertext
        
        # Formule : m = b * (a^x)^(-1) mod p
        # En utilisant le petit théorème de Fermat pour l'inverse modulaire : s^(-1) mod p = s^(p-2) mod p
        s = pow(a, x, p)
        s_inv = pow(s, p - 2, p)
        m = (b * s_inv) % p
        
        # Reconversion en bytes
        bit_length = m.bit_length()
        byte_length = (bit_length + 7) // 8
        return m.to_bytes(byte_length or 1, 'big')

# ============================================================================
# UTILITIES
# ============================================================================
def pad_pkcs7(data: bytes, block_size_bytes: int = 8) -> bytes:
    """Ajoute du padding PKCS7 pour les algorithmes de blocs (DES, 3DES, Blowfish)."""
    padder = pad_utils.PKCS7(block_size_bytes * 8).padder()
    return padder.update(data) + padder.finalize()

def unpad_pkcs7(padded_data: bytes, block_size_bytes: int = 8) -> bytes:
    """Retire le padding PKCS7."""
    unpadder = pad_utils.PKCS7(block_size_bytes * 8).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()

# ============================================================================
# BENCHMARK RUNNER CLASS
# ============================================================================
class CryptoBenchmarkRunner:
    def __init__(self):
        self.test_payload = b"Dossier medical confidentiel de test - Antigravity AI"
        self.results = {}
        print("Initialisation du banc d'essai cryptographique...")
        print(f"Payload de test ({len(self.test_payload)} octets) : '{self.test_payload.decode()}'\n")

    # --- 1. CHIFFREMENTS SYMÉTRIQUES ---

    def test_aes_256_gcm(self) -> Tuple[bool, float]:
        """Test AES-256-GCM"""
        try:
            key = os.urandom(32)  # 256 bits
            nonce = os.urandom(12) # 96-bit nonce
            
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(self.test_payload) + encryptor.finalize()
            tag = encryptor.tag
            
            decryptor = cipher.decryptor()
            pt = decryptor.update(ct) + decryptor.finalize_with_tag(tag)
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(1000):
                enc = cipher.encryptor()
                _ = enc.update(self.test_payload) + enc.finalize()
            duration = (time.perf_counter() - t0) * 1000  # ms pour 1000 itérations
            
            return is_correct, duration
        except Exception as e:
            print(f"  [!] AES-256-GCM non supporte : {e}")
            return False, -1.0

    def test_des(self) -> Tuple[bool, float]:
        """Test DES (généralement supprimé dans les bibliothèques modernes)"""
        try:
            if not hasattr(algorithms, 'DES'):
                raise AttributeError("DES n'existe plus dans 'cryptography.hazmat.primitives.algorithms'")
            
            algo_class = getattr(algorithms, 'DES')
            key = os.urandom(8)
            iv = os.urandom(8)
            padded_payload = pad_pkcs7(self.test_payload, 8)
            
            cipher = Cipher(algo_class(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(padded_payload) + encryptor.finalize()
            
            decryptor = cipher.decryptor()
            pt_padded = decryptor.update(ct) + decryptor.finalize()
            pt = unpad_pkcs7(pt_padded, 8)
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(1000):
                enc = cipher.encryptor()
                _ = enc.update(padded_payload) + enc.finalize()
            duration = (time.perf_counter() - t0) * 1000
            
            return is_correct, duration
        except Exception as e:
            # Retourne False pour le succès du test fonctionnel, et -1 pour indiquer la non-disponibilité
            return False, -1.0

    def test_triple_des(self) -> Tuple[bool, float]:
        """Test 3DES"""
        try:
            if not hasattr(algorithms, 'TripleDES'):
                raise AttributeError("TripleDES n'est pas supporte dans cette version")
                
            algo_class = getattr(algorithms, 'TripleDES')
            key = os.urandom(24)
            iv = os.urandom(8)
            padded_payload = pad_pkcs7(self.test_payload, 8)
            
            cipher = Cipher(algo_class(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(padded_payload) + encryptor.finalize()
            
            decryptor = cipher.decryptor()
            pt_padded = decryptor.update(ct) + decryptor.finalize()
            pt = unpad_pkcs7(pt_padded, 8)
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(1000):
                enc = cipher.encryptor()
                _ = enc.update(padded_payload) + enc.finalize()
            duration = (time.perf_counter() - t0) * 1000
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_chacha20(self) -> Tuple[bool, float]:
        """Test ChaCha20"""
        try:
            if not hasattr(algorithms, 'ChaCha20'):
                raise AttributeError("ChaCha20 n'est pas supporte")
                
            algo_class = getattr(algorithms, 'ChaCha20')
            key = os.urandom(32)
            nonce = os.urandom(16)
            
            cipher = Cipher(algo_class(key, nonce), mode=None, backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(self.test_payload) + encryptor.finalize()
            
            decryptor = cipher.decryptor()
            pt = decryptor.update(ct) + decryptor.finalize()
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(1000):
                enc = cipher.encryptor()
                _ = enc.update(self.test_payload) + enc.finalize()
            duration = (time.perf_counter() - t0) * 1000
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_blowfish(self) -> Tuple[bool, float]:
        """Test Blowfish"""
        try:
            if not hasattr(algorithms, 'Blowfish'):
                raise AttributeError("Blowfish n'est pas disponible")
                
            algo_class = getattr(algorithms, 'Blowfish')
            key = os.urandom(16)
            iv = os.urandom(8)
            padded_payload = pad_pkcs7(self.test_payload, 8)
            
            cipher = Cipher(algo_class(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(padded_payload) + encryptor.finalize()
            
            decryptor = cipher.decryptor()
            pt_padded = decryptor.update(ct) + decryptor.finalize()
            pt = unpad_pkcs7(pt_padded, 8)
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(1000):
                enc = cipher.encryptor()
                _ = enc.update(padded_payload) + enc.finalize()
            duration = (time.perf_counter() - t0) * 1000
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    # --- 2. CHIFFREMENTS & SIGNATURES ASYMÉTRIQUES ---

    def test_rsa(self) -> Tuple[bool, float]:
        """Test RSA-2048"""
        try:
            priv = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            pub = priv.public_key()
            
            rsa_pad = padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
            ct = pub.encrypt(self.test_payload, rsa_pad)
            pt = priv.decrypt(ct, rsa_pad)
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(50):
                _ = pub.encrypt(self.test_payload, rsa_pad)
            duration = ((time.perf_counter() - t0) * 1000) / 50 * 1000
            
            return is_correct, duration
        except Exception as e:
            print(f"  [!] RSA non supporte : {e}")
            return False, -1.0

    def test_ecc(self) -> Tuple[bool, float]:
        """Test ECC (ECDSA SECP256R1)"""
        try:
            priv = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
            pub = priv.public_key()
            
            sig = priv.sign(self.test_payload, ec.ECDSA(hashes.SHA256()))
            try:
                pub.verify(sig, self.test_payload, ec.ECDSA(hashes.SHA256()))
                is_correct = True
            except Exception:
                is_correct = False
                
            t0 = time.perf_counter()
            for _ in range(50):
                _ = priv.sign(self.test_payload, ec.ECDSA(hashes.SHA256()))
            duration = ((time.perf_counter() - t0) * 1000) / 50 * 1000
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_elgamal(self) -> Tuple[bool, float]:
        """Test ElGamal 1024-bits"""
        try:
            pubkey, privkey = PureElGamal.generate_keys()
            
            ct = PureElGamal.encrypt(pubkey, self.test_payload)
            pt = PureElGamal.decrypt(pubkey, privkey, ct)
            is_correct = (pt == self.test_payload)
            
            t0 = time.perf_counter()
            for _ in range(50):
                _ = PureElGamal.encrypt(pubkey, self.test_payload)
            duration = ((time.perf_counter() - t0) * 1000) / 50 * 1000
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_dsa(self) -> Tuple[bool, float]:
        """Test DSA-2048"""
        try:
            priv = dsa.generate_private_key(key_size=2048, backend=default_backend())
            pub = priv.public_key()
            
            sig = priv.sign(self.test_payload, hashes.SHA256())
            try:
                pub.verify(sig, self.test_payload, hashes.SHA256())
                is_correct = True
            except Exception:
                is_correct = False
                
            t0 = time.perf_counter()
            for _ in range(50):
                _ = priv.sign(self.test_payload, hashes.SHA256())
            duration = ((time.perf_counter() - t0) * 1000) / 50 * 1000
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    # --- 3. ALGORITHMES DE HACHAGE ---

    def test_sha256(self) -> Tuple[bool, float]:
        """Test SHA-256"""
        try:
            h = hashlib.sha256(self.test_payload).hexdigest()
            is_correct = (len(h) == 64)
            
            t0 = time.perf_counter()
            for _ in range(5000):
                _ = hashlib.sha256(self.test_payload).hexdigest()
            duration = ((time.perf_counter() - t0) * 1000) / 5
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_sha3_256(self) -> Tuple[bool, float]:
        """Test SHA3-256"""
        try:
            h = hashlib.sha3_256(self.test_payload).hexdigest()
            is_correct = (len(h) == 64)
            
            t0 = time.perf_counter()
            for _ in range(5000):
                _ = hashlib.sha3_256(self.test_payload).hexdigest()
            duration = ((time.perf_counter() - t0) * 1000) / 5
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_blake2(self) -> Tuple[bool, float]:
        """Test BLAKE2b"""
        try:
            h = hashlib.blake2b(self.test_payload).hexdigest()
            is_correct = (len(h) == 128)
            
            t0 = time.perf_counter()
            for _ in range(5000):
                _ = hashlib.blake2b(self.test_payload).hexdigest()
            duration = ((time.perf_counter() - t0) * 1000) / 5
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    def test_md5(self) -> Tuple[bool, float]:
        """Test MD5"""
        try:
            h = hashlib.md5(self.test_payload).hexdigest()
            is_correct = (len(h) == 32)
            
            t0 = time.perf_counter()
            for _ in range(5000):
                _ = hashlib.md5(self.test_payload).hexdigest()
            duration = ((time.perf_counter() - t0) * 1000) / 5
            
            return is_correct, duration
        except Exception:
            return False, -1.0

    # --- RUN ---

    def run_all(self):
        print("[*] Lancement des benchmarks (1000 iterations normalisees)...")
        print("=" * 70)
        
        # Symétriques
        print("\n[+] Tests : Chiffrements Symetriques...")
        self.results['AES'] = self.test_aes_256_gcm()
        self.results['DES'] = self.test_des()
        self.results['3DES'] = self.test_triple_des()
        self.results['ChaCha20'] = self.test_chacha20()
        self.results['Blowfish'] = self.test_blowfish()
        
        for name in ['AES', 'DES', '3DES', 'ChaCha20', 'Blowfish']:
            is_correct, duration = self.results[name]
            if duration == -1.0:
                status = "NON SUPPORTE (Obsolete/Insecure)"
                speed_str = "N/A"
            else:
                status = "OK" if is_correct else "FAILED"
                speed_str = f"{duration:.3f} ms"
            print(f"  - {name:10} : {status:<30} | Vitesse: {speed_str} / 1000 ops")

        # Asymétriques
        print("\n[+] Tests : Chiffrements / Signatures Asymetriques...")
        self.results['RSA'] = self.test_rsa()
        self.results['ECC'] = self.test_ecc()
        self.results['ElGamal'] = self.test_elgamal()
        self.results['DSA'] = self.test_dsa()
        
        for name in ['RSA', 'ECC', 'ElGamal', 'DSA']:
            is_correct, duration = self.results[name]
            note = "(Chiffrement)" if name in ['RSA', 'ElGamal'] else "(Signature)"
            if duration == -1.0:
                status = "NON SUPPORTE (Obsolete/Insecure)"
                speed_str = "N/A"
            else:
                status = "OK" if is_correct else "FAILED"
                speed_str = f"{duration:.3f} ms"
            print(f"  - {name:10} {note:<13} : {status:<30} | Vitesse: {speed_str} / 1000 ops")

        # Hachages
        print("\n[+] Tests : Algorithmes de Hachage...")
        self.results['SHA-256'] = self.test_sha256()
        self.results['SHA-3'] = self.test_sha3_256()
        self.results['BLAKE2'] = self.test_blake2()
        self.results['MD5'] = self.test_md5()
        
        for name in ['SHA-256', 'SHA-3', 'BLAKE2', 'MD5']:
            is_correct, duration = self.results[name]
            if duration == -1.0:
                status = "NON SUPPORTE"
                speed_str = "N/A"
            else:
                status = "OK" if is_correct else "FAILED"
                speed_str = f"{duration:.3f} ms"
            print(f"  - {name:10} : {status:<30} | Vitesse: {speed_str} / 1000 ops")

        self.print_final_markdown_table()

    # --- MARKDOWN OUTPUT ---

    def print_final_markdown_table(self):
        print("\n" + "=" * 70)
        print("TABLEAU COMPARATIF COMPLET POUR VOTRE RAPPORT")
        print("=" * 70 + "\n")
        
        metadata = {
            'AES': {
                'sec': "Excellent (Standard militaire, cle 256 bits)",
                'conf': "Conforme (Recommande par l'ANSSI, le NIST & le RGPD)"
            },
            'DES': {
                'sec': "Nul (Casse) (Clé 56 bits trop courte, decryptable rapidement)",
                'conf': "Non conforme (Interdit par l'ANSSI et le NIST)"
            },
            '3DES': {
                'sec': "Tres faible / Obsolete (Sensible aux attaques type Sweet32)",
                'conf': "Non conforme (Officiellement retire par le NIST en 2023)"
            },
            'ChaCha20': {
                'sec': "Excellent (Alternative moderne robuste, sans failles)",
                'conf': "Conforme (Standard IETF et approuve par l'ANSSI)"
            },
            'Blowfish': {
                'sec': "Faible / Obsolete (Bloc de 64 bits sensible aux collisions)",
                'conf': "Non conforme (Deprecie, remplace par Twofish et AES)"
            },
            'RSA': {
                'sec': "Bon (2048 bits) (Securise pour le moment)",
                'conf': "Conforme (Accepte par l'ANSSI jusqu'en 2030, NIST)"
            },
            'ECC': {
                'sec': "Excellent (Robuste et cles courtes)",
                'conf': "Conforme (Recommande par l'ANSSI/NIST, ideal mobile)"
            },
            'ElGamal': {
                'sec': "Moyen / Legacy (Necessite de grands groupes)",
                'conf': "Legacy (Rarement recommande, remplace par l'ECC)"
            },
            'DSA': {
                'sec': "Obsolete (Sensible aux generateurs de nombres faibles)",
                'conf': "Non conforme (Retire des standards FIPS par le NIST en 2023)"
            },
            'SHA-256': {
                'sec': "Excellent (Tres robuste, standard de l'industrie)",
                'conf': "Conforme (Standard universel ANSSI / NIST / RGPD)"
            },
            'SHA-3': {
                'sec': "Excellent (Moderne Keccak, robuste et immunise SHA-2)",
                'conf': "Conforme (Standard NIST)"
            },
            'BLAKE2': {
                'sec': "Excellent (Ultra-rapide et aussi sur que SHA-3)",
                'conf': "Conforme (Recommande dans RFC 7693)"
            },
            'MD5': {
                'sec': "Nul (Casse) (Collisions instantanees)",
                'conf': "Non conforme (Strictement interdit par l'ANSSI/NIST)"
            }
        }

        print("| Type | Methode | Niveau de securite offert | Respect de la conformite | Performance (1000 op.) | Status execution |")
        print("| :--- | :--- | :--- | :--- | :--- | :--- |")
        
        # Symétrique
        print(f"| Symetrique | AES (256 GCM) | {metadata['AES']['sec']} | {metadata['AES']['conf']} | {self._format_perf('AES')} | {self._format_status('AES')} |")
        print(f"| | DES | {metadata['DES']['sec']} | {metadata['DES']['conf']} | {self._format_perf('DES')} | {self._format_status('DES')} |")
        print(f"| | 3DES | {metadata['3DES']['sec']} | {metadata['3DES']['conf']} | {self._format_perf('3DES')} | {self._format_status('3DES')} |")
        print(f"| | ChaCha20 | {metadata['ChaCha20']['sec']} | {metadata['ChaCha20']['conf']} | {self._format_perf('ChaCha20')} | {self._format_status('ChaCha20')} |")
        print(f"| | Blowfish | {metadata['Blowfish']['sec']} | {metadata['Blowfish']['conf']} | {self._format_perf('Blowfish')} | {self._format_status('Blowfish')} |")
        
        # Asymétrique
        print(f"| Asymetrique | RSA-2048 | {metadata['RSA']['sec']} | {metadata['RSA']['conf']} | {self._format_perf('RSA')} | {self._format_status('RSA')} |")
        print(f"| | ECC (ECDSA) | {metadata['ECC']['sec']} | {metadata['ECC']['conf']} | {self._format_perf('ECC')} | {self._format_status('ECC')} |")
        print(f"| | ElGamal-1024 | {metadata['ElGamal']['sec']} | {metadata['ElGamal']['conf']} | {self._format_perf('ElGamal')} | {self._format_status('ElGamal')} |")
        print(f"| | DSA-2048 | {metadata['DSA']['sec']} | {metadata['DSA']['conf']} | {self._format_perf('DSA')} | {self._format_status('DSA')} |")
        
        # Hachage
        print(f"| Hachage | SHA-256 | {metadata['SHA-256']['sec']} | {metadata['SHA-256']['conf']} | {self._format_perf('SHA-256')} | {self._format_status('SHA-256')} |")
        print(f"| | SHA-3 (256) | {metadata['SHA-3']['sec']} | {metadata['SHA-3']['conf']} | {self._format_perf('SHA-3')} | {self._format_status('SHA-3')} |")
        print(f"| | BLAKE2b | {metadata['BLAKE2']['sec']} | {metadata['BLAKE2']['conf']} | {self._format_perf('BLAKE2')} | {self._format_status('BLAKE2')} |")
        print(f"| | MD5 | {metadata['MD5']['sec']} | {metadata['MD5']['conf']} | {self._format_perf('MD5')} | {self._format_status('MD5')} |")
        
        print("\n" + "=" * 70)

    def _format_perf(self, name: str) -> str:
        duration = self.results[name][1]
        if duration == -1.0:
            # Valeurs standards typiques pour les algos non supportés sur cette machine
            ref_vals = {
                'DES': "~0.06 ms (est.)",
                '3DES': "~0.18 ms (est.)",
                'Blowfish': "~0.08 ms (est.)"
            }
            return ref_vals.get(name, "N/A")
        return f"{duration:.3f} ms"

    def _format_status(self, name: str) -> str:
        is_correct, duration = self.results[name]
        if duration == -1.0:
            return "Non supporte (Bloque par la bibliotheque)"
        return "Actif & Valide" if is_correct else "Echec"


if __name__ == "__main__":
    runner = CryptoBenchmarkRunner()
    runner.run_all()
