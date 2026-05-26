# crypto_engines/elgamal.py
# Moteur de chiffrement ElGamal (Implémentation Mathématique Pure)
# Algorithme asymétrique basé sur la difficulté du logarithme discret.

import random

class ElGamalEngine:
    """
    Implémentation pure Python de l'algorithme asymétrique ElGamal.
    ElGamal est un précurseur des courbes elliptiques, basé sur la difficulté
    de résoudre le problème du logarithme discret dans les corps finis.
    
    Il est peu utilisé aujourd'hui au profit de l'ECC car les clés nécessaires
    sont extrêmement grandes pour rester sécurisées (au moins 2048 bits).
    """

    # Premier sûr de 1024 bits (RFC 3526 - MODP Group 5) pour les calculs modulaires
    P = int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
        "FFFFFFFFFFFFFFFF", 16
    )
    G = 2  # Générateur du groupe cyclique

    @classmethod
    def generate_keypair(cls) -> tuple[tuple[int, int, int], int]:
        """
        Génère une paire de clés ElGamal.
        - Clé privée : un entier secret x
        - Clé publique : le triplet (P, G, y) où y = G^x mod P
        """
        x = random.randint(2, cls.P - 2)      # Clé privée
        y = pow(cls.G, x, cls.P)              # Clé publique y = G^x mod P
        return (cls.P, cls.G, y), x

    @classmethod
    def encrypt(cls, plaintext: bytes, public_key: tuple[int, int, int]) -> tuple[int, int]:
        """
        Chiffre des données (bytes) avec la clé publique.
        Étapes :
        1. Convertir les bytes en un très grand entier m.
        2. Choisir un nombre aléatoire éphémère k.
        3. Calculer a = G^k mod P
        4. Calculer b = m * y^k mod P
        Retourne le couple de ciphertext (a, b)
        """
        p, g, y = public_key
        
        # Conversion du texte en grand entier
        m = int.from_bytes(plaintext, byteorder='big')
        if m >= p:
            raise ValueError("Le message est trop grand pour être chiffré directement (m >= P).")
            
        k = random.randint(2, p - 2)          # Clé éphémère k
        a = pow(g, k, p)                      # a = G^k mod P
        b = (m * pow(y, k, p)) % p            # b = m * y^k mod P
        
        return a, b

    @classmethod
    def decrypt(cls, ciphertext: tuple[int, int], public_key: tuple[int, int, int], private_key: int) -> bytes:
        """
        Déchiffre le couple (a, b) avec la clé privée x.
        Formule mathématique :
        m = b * (a^x)^(-1) mod P
        
        Pour calculer l'inverse modulaire, on utilise le petit théorème de Fermat :
        s^(-1) mod P = s^(P-2) mod P  (puisque P est un nombre premier)
        """
        p, g, y = public_key
        x = private_key
        a, b = ciphertext
        
        # 1. Calculer le secret partagé s = a^x mod P
        s = pow(a, x, p)
        
        # 2. Calculer l'inverse modulaire de s (s_inv) via Fermat
        s_inv = pow(s, p - 2, p)
        
        # 3. Retrouver le message m = b * s_inv mod P
        m = (b * s_inv) % p
        
        # Reconversion du grand entier en bytes
        bit_length = m.bit_length()
        byte_length = (bit_length + 7) // 8
        return m.to_bytes(byte_length or 1, byteorder='big')

# Code d'exemple si exécuté directement
if __name__ == "__main__":
    print("--- DEMO ELGAMAL ---")
    data = b"Notes medicales secretes d'ElGamal"
    
    # Génération des clés
    pub, priv = ElGamalEngine.generate_keypair()
    print(f"Clé privée x : {priv} (entier géant)")
    print(f"Clé publique y (G^x mod P) : {pub[2]}...")
    
    # Chiffrement et déchiffrement
    ct = ElGamalEngine.encrypt(data, pub)
    print(f"\nMessage chiffré :")
    print(f"  a (G^k mod P) : {ct[0]}...")
    print(f"  b (m * y^k mod P) : {ct[1]}...")
    
    pt = ElGamalEngine.decrypt(ct, pub, priv)
    print(f"\nMessage déchiffré : {pt.decode()}")
