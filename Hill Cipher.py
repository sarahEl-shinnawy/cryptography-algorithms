import numpy as np

def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("No modular inverse found")

def encrypt_hill(plaintext, key_matrix):
    plaintext = plaintext.upper().replace(" ", "")
    if len(plaintext) % 2 != 0:
        plaintext += 'X'

    encrypted = ""
    for i in range(0, len(plaintext), 2):
        pair = [ord(c) - ord('A') for c in plaintext[i:i+2]]
        vector = np.array(pair).reshape(2, 1)
        result = np.dot(key_matrix, vector) % 26
        encrypted += ''.join(chr(int(n) + ord('A')) for n in result)
    return encrypted

def decrypt_hill(ciphertext, key_matrix):
    det = int(np.round(np.linalg.det(key_matrix))) % 26
    det_inv = mod_inverse(det, 26)

    matrix_inv = np.round(det_inv * np.linalg.inv(key_matrix) * det) % 26
    matrix_inv = matrix_inv.astype(int)

    decrypted = ""
    for i in range(0, len(ciphertext), 2):
        pair = [ord(c) - ord('A') for c in ciphertext[i:i+2]]
        vector = np.array(pair).reshape(2, 1)
        result = np.dot(matrix_inv, vector) % 26
        decrypted += ''.join(chr(int(n) + ord('A')) for n in result)
    return decrypted

# Example
key_matrix = np.array([[3, 3], [2, 5]])
plaintext = "HELLO"
encrypted = encrypt_hill(plaintext, key_matrix)
decrypted = decrypt_hill(encrypted, key_matrix)

print("Hill Cipher")
print("Encrypted:", encrypted)
print("Decrypted:", decrypted)
