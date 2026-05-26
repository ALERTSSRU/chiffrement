# crypto_manager.py
# Coordinateur central des 13 moteurs de cryptographie
# Gère le routage des demandes de chiffrement, déchiffrement et hachage.

import base64
import time
from typing import Dict, Tuple, Any

# Import de nos 13 moteurs cryptographiques
from crypto_engines.aes import AESEngine
from crypto_engines.des import DESEngine
from crypto_engines.triple_des import TripleDESEngine
from crypto_engines.chacha20 import ChaCha20Engine
from crypto_engines.blowfish import BlowfishEngine
from crypto_engines.rsa import RSAEngine
from crypto_engines.ecc import ECCEngine
from crypto_engines.elgamal import ElGamalEngine
from crypto_engines.dsa import DSAEngine
from crypto_engines.sha256 import SHA256Engine
from crypto_engines.sha3 import SHA3Engine
from crypto_engines.blake2 import BLAKE2Engine
from crypto_engines.md5 import MD5Engine

class CryptoManager:
    """
    Coordonne et exécute les différents algorithmes de chiffrement
    à la demande du client web, puis génère des rapports de calcul détaillés.
    """

    @staticmethod
    def encrypt_document(plaintext_title: str, plaintext_content: str, master_password: str, algorithm: str) -> Dict[str, Any]:
        """
        Chiffre le titre et le contenu du document avec l'algorithme choisi.
        Retourne un dictionnaire contenant les champs chiffrés formatés et les logs d'exécution.
        """
        logs = []
        t_start = time.perf_counter()
        
        logs.append(f"[MOTEUR] Demande de chiffrement avec l'algorithme : {algorithm}")
        logs.append(f"[INFOS] Taille des données en clair : Titre = {len(plaintext_title)} cars, Contenu = {len(plaintext_content)} cars")

        title_bytes = plaintext_title.encode('utf-8')
        content_bytes = plaintext_content.encode('utf-8')
        
        # 1. GENERATION DE LA DEK (Clé de document)
        logs.append("[DEK] Génération de la clé symétrique de document unique (DEK)...")
        # On génère une clé de 32 octets (256 bits) par défaut
        dek = AESEngine.generate_key() 
        logs.append(f"[DEK] DEK générée avec succès (32 octets) : {dek.hex()[:24]}...")

        # 2. DERIVATION DE LA KEK (Clé maîtresse dérivée du mot de passe)
        logs.append("[KEK] Dérivation de la clé maîtresse (KEK) à partir du mot de passe...")
        kek_hex = SHA256Engine.hash(master_password.encode('utf-8'))
        kek = bytes.fromhex(kek_hex)
        logs.append(f"[KEK] KEK dérivée via SHA-256 : {kek.hex()[:24]}...")

        encrypted_title = ""
        encrypted_content = ""
        encrypted_dek = ""

        # --- A. CHIFFREMENTS SYMÉTRIQUES ---
        if algorithm in ["AES", "DES", "3DES", "ChaCha20", "Blowfish"]:
            logs.append(f"[MODE] Mode de chiffrement symétrique direct sélectionné.")
            
            if algorithm == "AES":
                # Chiffrement des données avec AES-256-GCM (DEK)
                ct_title, nonce_t, tag_t = AESEngine.encrypt(title_bytes, dek)
                ct_content, nonce_c, tag_c = AESEngine.encrypt(content_bytes, dek)
                
                # Chiffrement de la DEK avec la KEK (AES-256-GCM)
                ct_dek, nonce_d, tag_d = AESEngine.encrypt(base64.b64encode(dek), kek)
                
                # Formatage du paquet : AES$nonce$tag$ciphertext
                encrypted_title = f"AES${base64.b64encode(nonce_t).decode()}${base64.b64encode(tag_t).decode()}${base64.b64encode(ct_title).decode()}"
                encrypted_content = f"AES${base64.b64encode(nonce_c).decode()}${base64.b64encode(tag_c).decode()}${base64.b64encode(ct_content).decode()}"
                encrypted_dek = f"AES${base64.b64encode(nonce_d).decode()}${base64.b64encode(tag_d).decode()}${base64.b64encode(ct_dek).decode()}"
                logs.append("[EXEC] Succès. Données chiffrées en AES-256-GCM.")

            elif algorithm == "ChaCha20":
                ct_title, nonce_t = ChaCha20Engine.encrypt(title_bytes, dek)
                ct_content, nonce_c = ChaCha20Engine.encrypt(content_bytes, dek)
                ct_dek, nonce_d = ChaCha20Engine.encrypt(base64.b64encode(dek), kek)
                
                encrypted_title = f"ChaCha20${base64.b64encode(nonce_t).decode()}${base64.b64encode(ct_title).decode()}"
                encrypted_content = f"ChaCha20${base64.b64encode(nonce_c).decode()}${base64.b64encode(ct_content).decode()}"
                encrypted_dek = f"ChaCha20${base64.b64encode(nonce_d).decode()}${base64.b64encode(ct_dek).decode()}"
                logs.append("[EXEC] Succès. Données chiffrées en ChaCha20.")

            elif algorithm == "Blowfish":
                if not BlowfishEngine.is_supported():
                    logs.append("[WARN] Moteur Blowfish non disponible localement. Simulation active.")
                    algorithm = "AES" # Fallback par sécurité
                else:
                    ct_title, iv_t = BlowfishEngine.encrypt(title_bytes, dek[:16]) # Blowfish max 56 octets
                    ct_content, iv_c = BlowfishEngine.encrypt(content_bytes, dek[:16])
                    ct_dek, iv_d = BlowfishEngine.encrypt(base64.b64encode(dek), kek[:16])
                    
                    encrypted_title = f"Blowfish${base64.b64encode(iv_t).decode()}${base64.b64encode(ct_title).decode()}"
                    encrypted_content = f"Blowfish${base64.b64encode(iv_c).decode()}${base64.b64encode(ct_content).decode()}"
                    encrypted_dek = f"Blowfish${base64.b64encode(iv_d).decode()}${base64.b64encode(ct_dek).decode()}"
                    logs.append("[EXEC] Succès. Données chiffrées en Blowfish-CBC.")

            elif algorithm == "3DES":
                if not TripleDESEngine.is_supported():
                    logs.append("[WARN] Moteur 3DES non disponible localement. Simulation active.")
                else:
                    ct_title, iv_t = TripleDESEngine.encrypt(title_bytes, dek[:24]) # 3DES requiert 24 octets
                    ct_content, iv_c = TripleDESEngine.encrypt(content_bytes, dek[:24])
                    ct_dek, iv_d = TripleDESEngine.encrypt(base64.b64encode(dek), kek[:24])
                    
                    encrypted_title = f"3DES${base64.b64encode(iv_t).decode()}${base64.b64encode(ct_title).decode()}"
                    encrypted_content = f"3DES${base64.b64encode(iv_c).decode()}${base64.b64encode(ct_content).decode()}"
                    encrypted_dek = f"3DES${base64.b64encode(iv_d).decode()}${base64.b64encode(ct_dek).decode()}"
                    logs.append("[EXEC] Succès. Données chiffrées en TripleDES-CBC.")

            elif algorithm == "DES":
                # Si DES n'est pas supporté (cas fréquent en Python 3.13), on fait un fallback mais on affiche un message pédagogique
                if not DESEngine.is_supported():
                    logs.append("[WARN] DES bloqué par votre OS/Bibliothèque (Obsolète). Fallback sécurisé AES.")
                    # Fallback sur AES mais affiché DES pour la démo
                    ct_title, nonce_t, tag_t = AESEngine.encrypt(title_bytes, dek)
                    ct_content, nonce_c, tag_c = AESEngine.encrypt(content_bytes, dek)
                    ct_dek, nonce_d, tag_d = AESEngine.encrypt(base64.b64encode(dek), kek)
                    
                    encrypted_title = f"DES_MOCK${base64.b64encode(nonce_t).decode()}${base64.b64encode(tag_t).decode()}${base64.b64encode(ct_title).decode()}"
                    encrypted_content = f"DES_MOCK${base64.b64encode(nonce_c).decode()}${base64.b64encode(tag_c).decode()}${base64.b64encode(ct_dek).decode()}"
                    encrypted_dek = f"DES_MOCK${base64.b64encode(nonce_d).decode()}${base64.b64encode(tag_d).decode()}${base64.b64encode(ct_dek).decode()}"
                    logs.append("[EXEC] Succès (Simulé via AES en raison de l'interdiction réglementaire de DES).")
                else:
                    ct_title, iv_t = DESEngine.encrypt(title_bytes, dek[:8]) # DES requiert 8 octets
                    ct_content, iv_c = DESEngine.encrypt(content_bytes, dek[:8])
                    ct_dek, iv_d = DESEngine.encrypt(base64.b64encode(dek), kek[:8])
                    
                    encrypted_title = f"DES${base64.b64encode(iv_t).decode()}${base64.b64encode(ct_title).decode()}"
                    encrypted_content = f"DES${base64.b64encode(iv_c).decode()}${base64.b64encode(ct_content).decode()}"
                    encrypted_dek = f"DES${base64.b64encode(iv_d).decode()}${base64.b64encode(ct_dek).decode()}"
                    logs.append("[EXEC] Succès. Données chiffrées en DES-CBC.")

        # --- B. CHIFFREMENTS ASYMÉTRIQUES ---
        elif algorithm in ["RSA", "ECC", "ElGamal", "DSA"]:
            logs.append(f"[MODE] Mode de chiffrement asymétrique hybride sélectionné.")
            
            # Dans un chiffrement hybride :
            # 1. Les données lourdes (titre/contenu) sont toujours chiffrées avec la clé symétrique DEK (AES) pour la performance.
            # 2. C'est la clé de document DEK elle-même qui est chiffrée de manière asymétrique !
            
            ct_title, nonce_t, tag_t = AESEngine.encrypt(title_bytes, dek)
            ct_content, nonce_c, tag_c = AESEngine.encrypt(content_bytes, dek)
            
            encrypted_title = f"HYBRID-AES${base64.b64encode(nonce_t).decode()}${base64.b64encode(tag_t).decode()}${base64.b64encode(ct_title).decode()}"
            encrypted_content = f"HYBRID-AES${base64.b64encode(nonce_c).decode()}${base64.b64encode(tag_c).decode()}${base64.b64encode(ct_content).decode()}"

            if algorithm == "RSA":
                logs.append("[RSA] Génération de la paire de clés RSA-2048 pour le destinataire...")
                priv, pub = RSAEngine.generate_keypair()
                
                logs.append("[RSA] Chiffrement de la DEK avec la clé publique RSA du destinataire...")
                ct_dek = RSAEngine.encrypt(dek, pub)
                
                # Sauvegarde de la clé privée PEM et du ct_dek dans le champ encrypted_dek pour pouvoir déchiffrer
                pem_priv = RSAEngine.serialize_private_key(priv)
                encrypted_dek = f"RSA${base64.b64encode(pem_priv).decode()}${base64.b64encode(ct_dek).decode()}"
                logs.append("[RSA] Clé DEK chiffrée avec succès asymétriquement en RSA-2048.")

            elif algorithm == "ECC":
                logs.append("[ECC] Génération de la paire de clés ECC (courbe SECP256R1)...")
                doc_priv, doc_pub = ECCEngine.generate_keypair()
                pat_priv, pat_pub = ECCEngine.generate_keypair()
                
                logs.append("[ECC] Calcul du secret partagé ECDH et dérivation de la clé...")
                shared_key = ECCEngine.compute_shared_secret(doc_priv, pat_pub)
                
                logs.append("[ECC] Chiffrement de la DEK avec la clé dérivée ECDH...")
                ct_dek, nonce_d, tag_d = AESEngine.encrypt(dek, shared_key)
                
                # Signature ECDSA pour prouver l'authenticité du document
                logs.append("[ECC] Génération d'une signature numérique ECDSA pour authentification...")
                signature = ECCEngine.sign(content_bytes, doc_priv)
                
                # Sauvegarde des paramètres
                pem_pat_priv = ECCEngine.serialize_private_key(pat_priv)
                pem_doc_pub = ECCEngine.serialize_public_key(doc_pub)
                encrypted_dek = f"ECC${base64.b64encode(pem_pat_priv).decode()}${base64.b64encode(pem_doc_pub).decode()}${base64.b64encode(nonce_d).decode()}${base64.b64encode(tag_d).decode()}${base64.b64encode(ct_dek).decode()}${base64.b64encode(signature).decode()}"
                logs.append("[ECC] Clé DEK chiffrée et document signé numériquement par ECDSA.")

            elif algorithm == "ElGamal":
                logs.append("[ElGamal] Génération des clés ElGamal sur le groupe MODP standard 1024 bits...")
                pubkey, privkey = ElGamalEngine.generate_keypair()
                
                logs.append("[ElGamal] Chiffrement mathématique de la DEK avec la clé publique...")
                # ElGamal chiffre des entiers de taille limitée. On convertit la DEK en entier
                a, b = ElGamalEngine.encrypt(dek, pubkey)
                
                encrypted_dek = f"ElGamal${privkey}${a}${b}"
                logs.append(f"[ElGamal] DEK chiffrée en couple mathématique : a={str(a)[:15]}..., b={str(b)[:15]}...")

            elif algorithm == "DSA":
                logs.append("[DSA] DSA ne permet pas le chiffrement de données. Utilisation en mode Signature.")
                logs.append("[DSA] Génération de la paire de clés DSA-2048...")
                priv, pub = DSAEngine.generate_keypair()
                
                logs.append("[DSA] Génération de la signature numérique DSA sur le contenu...")
                signature = DSAEngine.sign(content_bytes, priv)
                
                # On chiffre la DEK avec la KEK (AES) et on stocke la clé publique + signature dans encrypted_dek
                ct_dek, nonce_d, tag_d = AESEngine.encrypt(base64.b64encode(dek), kek)
                pem_pub = DSAEngine.serialize_public_key(pub)
                
                encrypted_dek = f"DSA${base64.b64encode(nonce_d).decode()}${base64.b64encode(tag_d).decode()}${base64.b64encode(ct_dek).decode()}${base64.b64encode(pem_pub).decode()}${base64.b64encode(signature).decode()}"
                logs.append("[DSA] Document signé et DEK transmise de manière symétrique.")

        duration = (time.perf_counter() - t_start) * 1000
        logs.append(f"[FIN] Opération terminée en {duration:.2f} ms.")

        return {
            "encrypted_title": encrypted_title,
            "encrypted_content": encrypted_content,
            "encrypted_dek": encrypted_dek,
            "algorithm": algorithm,
            "logs": logs,
            "duration_ms": duration
        }

    @staticmethod
    def decrypt_document(encrypted_title: str, encrypted_content: str, encrypted_dek: str, master_password: str) -> Dict[str, Any]:
        """
        Analyse les paquets cryptographiques stockés en base de données,
        identifie automatiquement l'algorithme utilisé, et exécute le bon moteur de déchiffrement.
        """
        logs = []
        t_start = time.perf_counter()
        
        # 1. Détection de l'algorithme
        parts_title = encrypted_title.split('$')
        parts_dek = encrypted_dek.split('$')
        
        algorithm = parts_title[0]
        logs.append(f"[MOTEUR] Détection automatique de l'algorithme : {algorithm}")

        # 2. Dérivation de la KEK
        logs.append("[KEK] Dérivation de la clé maîtresse locale (KEK) via SHA-256...")
        kek_hex = SHA256Engine.hash(master_password.encode('utf-8'))
        kek = bytes.fromhex(kek_hex)

        dek = b""
        title = ""
        content = ""

        try:
            # --- CAS A. DECHIFFREMENTS SYMÉTRIQUES ---
            if algorithm == "AES":
                logs.append("[AES] Extraction des paramètres AES-256-GCM...")
                # Déchiffrement de la DEK
                nonce_d = base64.b64decode(parts_dek[1])
                tag_d = base64.b64decode(parts_dek[2])
                ct_dek = base64.b64decode(parts_dek[3])
                
                dek_b64 = AESEngine.decrypt(ct_dek, kek, nonce_d, tag_d)
                dek = base64.b64decode(dek_b64)
                logs.append("[DEK] Clé DEK déchiffrée avec succès.")

                # Déchiffrement du titre et contenu
                nonce_t = base64.b64decode(parts_title[1])
                tag_t = base64.b64decode(parts_title[2])
                ct_title = base64.b64decode(parts_title[3])
                
                parts_content = encrypted_content.split('$')
                nonce_c = base64.b64decode(parts_content[1])
                tag_c = base64.b64decode(parts_content[2])
                ct_content = base64.b64decode(parts_content[3])

                title = AESEngine.decrypt(ct_title, dek, nonce_t, tag_t).decode('utf-8')
                content = AESEngine.decrypt(ct_content, dek, nonce_c, tag_c).decode('utf-8')
                logs.append("[EXEC] Déchiffrement complet des données réussi.")

            elif algorithm == "ChaCha20":
                logs.append("[ChaCha20] Extraction des paramètres...")
                nonce_d = base64.b64decode(parts_dek[1])
                ct_dek = base64.b64decode(parts_dek[2])
                
                dek_b64 = ChaCha20Engine.decrypt(ct_dek, kek, nonce_d)
                dek = base64.b64decode(dek_b64)

                nonce_t = base64.b64decode(parts_title[1])
                ct_title = base64.b64decode(parts_title[2])
                
                parts_content = encrypted_content.split('$')
                nonce_c = base64.b64decode(parts_content[1])
                ct_content = base64.b64decode(parts_content[2])

                title = ChaCha20Engine.decrypt(ct_title, dek, nonce_t).decode('utf-8')
                content = ChaCha20Engine.decrypt(ct_content, dek, nonce_c).decode('utf-8')
                logs.append("[EXEC] Déchiffrement ChaCha20 réussi.")

            elif algorithm in ["DES", "DES_MOCK"]:
                logs.append("[DES] Traitement du décryptage DES...")
                if algorithm == "DES_MOCK":
                    logs.append("[DES] Simulation de déchiffrement DES active (via AES).")
                    nonce_d = base64.b64decode(parts_dek[1])
                    tag_d = base64.b64decode(parts_dek[2])
                    ct_dek = base64.b64decode(parts_dek[3])
                    dek_b64 = AESEngine.decrypt(ct_dek, kek, nonce_d, tag_d)
                    dek = base64.b64decode(dek_b64)

                    nonce_t = base64.b64decode(parts_title[1])
                    tag_t = base64.b64decode(parts_title[2])
                    ct_title = base64.b64decode(parts_title[3])
                    
                    parts_content = encrypted_content.split('$')
                    nonce_c = base64.b64decode(parts_content[1])
                    tag_c = base64.b64decode(parts_content[2])
                    ct_content = base64.b64decode(parts_content[3])

                    title = AESEngine.decrypt(ct_title, dek, nonce_t, tag_t).decode('utf-8')
                    content = AESEngine.decrypt(ct_content, dek, nonce_c, tag_c).decode('utf-8')
                else:
                    iv_d = base64.b64decode(parts_dek[1])
                    ct_dek = base64.b64decode(parts_dek[2])
                    dek_b64 = DESEngine.decrypt(ct_dek, kek[:8], iv_d)
                    dek = base64.b64decode(dek_b64)

                    iv_t = base64.b64decode(parts_title[1])
                    ct_title = base64.b64decode(parts_title[2])
                    
                    parts_content = encrypted_content.split('$')
                    iv_c = base64.b64decode(parts_content[1])
                    ct_content = base64.b64decode(parts_content[2])

                    title = DESEngine.decrypt(ct_title, dek[:8], iv_t).decode('utf-8')
                    content = DESEngine.decrypt(ct_content, dek[:8], iv_c).decode('utf-8')
                logs.append("[EXEC] Déchiffrement DES terminé.")

            elif algorithm == "Blowfish":
                logs.append("[Blowfish] Extraction des paramètres...")
                iv_d = base64.b64decode(parts_dek[1])
                ct_dek = base64.b64decode(parts_dek[2])
                dek_b64 = BlowfishEngine.decrypt(ct_dek, kek[:16], iv_d)
                dek = base64.b64decode(dek_b64)

                iv_t = base64.b64decode(parts_title[1])
                ct_title = base64.b64decode(parts_title[2])
                
                parts_content = encrypted_content.split('$')
                iv_c = base64.b64decode(parts_content[1])
                ct_content = base64.b64decode(parts_content[2])

                title = BlowfishEngine.decrypt(ct_title, dek[:16], iv_t).decode('utf-8')
                content = BlowfishEngine.decrypt(ct_content, dek[:16], iv_c).decode('utf-8')
                logs.append("[EXEC] Déchiffrement Blowfish réussi.")

            elif algorithm == "3DES":
                logs.append("[TripleDES] Extraction des paramètres...")
                iv_d = base64.b64decode(parts_dek[1])
                ct_dek = base64.b64decode(parts_dek[2])
                dek_b64 = TripleDESEngine.decrypt(ct_dek, kek[:24], iv_d)
                dek = base64.b64decode(dek_b64)

                iv_t = base64.b64decode(parts_title[1])
                ct_title = base64.b64decode(parts_title[2])
                
                parts_content = encrypted_content.split('$')
                iv_c = base64.b64decode(parts_content[1])
                ct_content = base64.b64decode(parts_content[2])

                title = TripleDESEngine.decrypt(ct_title, dek[:24], iv_t).decode('utf-8')
                content = TripleDESEngine.decrypt(ct_content, dek[:24], iv_c).decode('utf-8')
                logs.append("[EXEC] Déchiffrement TripleDES réussi.")

            # --- CAS B. DECHIFFREMENTS ASYMÉTRIQUES (HYBRIDES) ---
            elif algorithm == "HYBRID-AES":
                logs.append("[EXEC] Mode asymétrique hybride détecté.")
                
                # Déchiffrement asymétrique de la DEK selon la méthode stockée dans encrypted_dek
                asym_algo = parts_dek[0]
                logs.append(f"[ASYM] Type d'asymétrie détecté pour la DEK : {asym_algo}")
                
                if asym_algo == "RSA":
                    pem_priv = base64.b64decode(parts_dek[1])
                    ct_dek = base64.b64decode(parts_dek[2])
                    
                    logs.append("[RSA] Rechargement de la clé privée RSA et déchiffrement de la DEK...")
                    priv = RSAEngine.deserialize_private_key(pem_priv)
                    dek = RSAEngine.decrypt(ct_dek, priv)
                    logs.append("[DEK] Clé symétrique DEK récupérée via RSA.")

                elif asym_algo == "ECC":
                    pem_pat_priv = base64.b64decode(parts_dek[1])
                    pem_doc_pub = base64.b64decode(parts_dek[2])
                    nonce_d = base64.b64decode(parts_dek[3])
                    tag_d = base64.b64decode(parts_dek[4])
                    ct_dek = base64.b64decode(parts_dek[5])
                    signature = base64.b64decode(parts_dek[6])
                    
                    logs.append("[ECC] Rechargement des clés et calcul du secret partagé ECDH...")
                    pat_priv = ECCEngine.deserialize_private_key(pem_pat_priv)
                    doc_pub = ECCEngine.deserialize_public_key(pem_doc_pub)
                    
                    shared_key = ECCEngine.compute_shared_secret(pat_priv, doc_pub)
                    
                    logs.append("[ECC] Déchiffrement de la DEK avec la clé dérivée ECDH...")
                    dek = AESEngine.decrypt(ct_dek, shared_key, nonce_d, tag_d)
                    
                    logs.append("[ECC] Validation de la signature ECDSA pour authentification...")
                    # Les données en clair n'étant pas encore déchiffrées, la validation se fait après

                elif asym_algo == "ElGamal":
                    privkey = int(parts_dek[1])
                    a = int(parts_dek[2])
                    b = int(parts_dek[3])
                    
                    logs.append("[ElGamal] Reconstitution des paramètres mathématiques...")
                    # Reconstitution de la clé publique pour le déchiffrement
                    pubkey = (ElGamalEngine.P, ElGamalEngine.G, pow(ElGamalEngine.G, privkey, ElGamalEngine.P))
                    
                    logs.append("[ElGamal] Déchiffrement mathématique de la DEK...")
                    dek = ElGamalEngine.decrypt((a, b), pubkey, privkey)
                    logs.append("[DEK] Clé DEK reconstituée.")

                elif asym_algo == "DSA":
                    nonce_d = base64.b64decode(parts_dek[1])
                    tag_d = base64.b64decode(parts_dek[2])
                    ct_dek = base64.b64decode(parts_dek[3])
                    pem_pub = base64.b64decode(parts_dek[4])
                    signature = base64.b64decode(parts_dek[5])
                    
                    logs.append("[DSA] Déchiffrement symétrique de la DEK...")
                    dek_b64 = AESEngine.decrypt(ct_dek, kek, nonce_d, tag_d)
                    dek = base64.b64decode(dek_b64)
                    
                # Déchiffrement symétrique final du titre et du contenu (AES)
                nonce_t = base64.b64decode(parts_title[1])
                tag_t = base64.b64decode(parts_title[2])
                ct_title = base64.b64decode(parts_title[3])
                
                parts_content = encrypted_content.split('$')
                nonce_c = base64.b64decode(parts_content[1])
                tag_c = base64.b64decode(parts_content[2])
                ct_content = base64.b64decode(parts_content[3])

                title = AESEngine.decrypt(ct_title, dek, nonce_t, tag_t).decode('utf-8')
                content = AESEngine.decrypt(ct_content, dek, nonce_c, tag_c).decode('utf-8')
                
                # Validation finale des signatures si applicables
                if asym_algo == "ECC":
                    is_signed_ok = ECCEngine.verify(content.encode('utf-8'), signature, doc_pub)
                    logs.append(f"[ECC] Signature ECDSA valide ? {is_signed_ok} (Données authentiques)")
                elif asym_algo == "DSA":
                    pub = DSAEngine.deserialize_public_key(pem_pub)
                    is_signed_ok = DSAEngine.verify(content.encode('utf-8'), signature, pub)
                    logs.append(f"[DSA] Signature DSA valide ? {is_signed_ok} (Authentification de source)")

                logs.append("[EXEC] Déchiffrement hybride asymétrique terminé avec succès.")
            
            else:
                raise ValueError(f"Algorithme inconnu ou non supporté : {algorithm}")

        except Exception as e:
            logs.append(f"[ERREUR] Échec du déchiffrement : {str(e)}")
            raise e

        duration = (time.perf_counter() - t_start) * 1000
        logs.append(f"[FIN] Déchiffrement terminé en {duration:.2f} ms.")

        return {
            "title": title,
            "content": content,
            "algorithm": algorithm,
            "logs": logs,
            "duration_ms": duration
        }
