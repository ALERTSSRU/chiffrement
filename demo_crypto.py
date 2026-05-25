# demo_crypto.py
# Script de démonstration des fonctionnalités cryptographiques

from crypto import HashAlgorithm, SymmetricEncryption, AsymmetricEncryption, CryptoBenchmark
import json

print("=" * 80)
print("DÉMONSTRATION - Module Cryptographique".center(80))
print("=" * 80)

# ============================================================================
# 1. HACHAGE
# ============================================================================
print("\n📊 1. HACHAGE - Comparaison d'Algorithmes")
print("-" * 80)

test_password = "MySecurePassword123!"
test_data = b"Important medical record data"

print(f"\nTexte à hacher: {test_password}")
print(f"Données: {test_data.decode()}\n")

hashes = {
    "SHA-256": HashAlgorithm.sha256(test_password.encode()),
    "SHA-3-256": HashAlgorithm.sha3_256(test_password.encode()),
    "BLAKE2b": HashAlgorithm.blake2b(test_password.encode()),
    "MD5": HashAlgorithm.md5(test_password.encode()),
}

for algo, hash_value in hashes.items():
    print(f"{algo:15} : {hash_value}")

# HMAC
print(f"\nHMAC-SHA256 (key='secret'):")
hmac_sig = HashAlgorithm.hmac_sha256(b"secret", test_data)
print(f"  {hmac_sig}")

# ============================================================================
# 2. CHIFFREMENT SYMÉTRIQUE
# ============================================================================
print("\n\n🔐 2. CHIFFREMENT SYMÉTRIQUE (AES-256-GCM)")
print("-" * 80)

key = SymmetricEncryption.generate_key(256)
plaintext = b"Patient: John Doe\nDiagnosis: Confidential Medical Info"

print(f"\nClé générée (256 bits): {key.hex()[:32]}... (truncated)")
print(f"Texte en clair: {plaintext.decode()}")

ciphertext_b64, nonce_b64 = SymmetricEncryption.encrypt_aes_gcm(plaintext, key)
print(f"\nChiffré (Base64): {ciphertext_b64[:60]}...")
print(f"Nonce (Base64):  {nonce_b64}")

decrypted = SymmetricEncryption.decrypt_aes_gcm(ciphertext_b64, nonce_b64, key)
print(f"\nDéchiffré: {decrypted.decode()}")
print(f"Déchiffrement réussi: {'✅ OUI' if decrypted == plaintext else '❌ NON'}")

# ============================================================================
# 3. CHIFFREMENT ASYMÉTRIQUE
# ============================================================================
print("\n\n🔑 3. CHIFFREMENT ASYMÉTRIQUE (RSA-2048)")
print("-" * 80)

private_key_pem, public_key_pem = AsymmetricEncryption.generate_rsa_keypair(2048)

print(f"\nClé publique générée (PEM):")
print(public_key_pem[:100] + "...")

message = b"Top Secret: Lab Results"
print(f"\nMessage original: {message.decode()}")

encrypted_msg = AsymmetricEncryption.rsa_encrypt(message, public_key_pem)
print(f"Message chiffré (Base64): {encrypted_msg[:60]}...")

decrypted_msg = AsymmetricEncryption.rsa_decrypt(encrypted_msg, private_key_pem)
print(f"Message déchiffré: {decrypted_msg.decode()}")
print(f"Déchiffrement réussi: {'✅ OUI' if decrypted_msg == message else '❌ NON'}")

# ============================================================================
# 4. TABLEAU COMPARATIF
# ============================================================================
print("\n\n📈 4. TABLEAU COMPARATIF (Performance/Sécurité)")
print("-" * 80)

comparison_table = CryptoBenchmark.get_comparison_table()

print("\n🟢 HACHAGE (Hash Algorithms):")
for algo in comparison_table["hash_algorithms"]:
    print(f"  • {algo['name']:20} Vitesse: {algo['speed']:10} Sécurité: {algo['security']:10} Status: {algo['status']}")

print("\n🟡 CHIFFREMENT SYMÉTRIQUE (Symmetric Encryption):")
for algo in comparison_table["symmetric_encryption"]:
    print(f"  • {algo['name']:20} Vitesse: {algo['speed']:10} Sécurité: {algo['security']:10} Status: {algo['status']}")

print("\n🔵 CHIFFREMENT ASYMÉTRIQUE (Asymmetric Encryption):")
for algo in comparison_table["asymmetric_encryption"]:
    print(f"  • {algo['name']:20} Vitesse: {algo['speed']:10} Sécurité: {algo['security']:10} Status: {algo['status']}")

# ============================================================================
# 5. BENCHMARK
# ============================================================================
print("\n\n⚡ 5. BENCHMARK DE PERFORMANCE")
print("-" * 80)

benchmark_results = CryptoBenchmark.benchmark_hash_algorithms()
print("\nPerformance (10 000 itérations):")
for algo, result in benchmark_results.items():
    print(f"  • {algo:15} : {result}")

print("\n" + "=" * 80)
print("✅ Démonstration terminée avec succès!".center(80))
print("=" * 80)
