def xor(a, b):
    return ''.join('1' if i != j else '0' for i, j in zip(a, b))

def sbox_substitution(bits):
    # Tiny fixed 4-bit S-box for demo
    sbox = {
        '0000': '1110', '0001': '0100', '0010': '1101', '0011': '0001',
        '0100': '0010', '0101': '1111', '0110': '1011', '0111': '1000',
        '1000': '0011', '1001': '1010', '1010': '0110', '1011': '1100',
        '1100': '0101', '1101': '1001', '1110': '0000', '1111': '0111',
    }
    return ''.join(sbox[bits[i:i+4]] for i in range(0, len(bits), 4))

def feistel_round(left, right, subkey):
    f = sbox_substitution(xor(right, subkey))
    new_right = xor(left, f)
    return right, new_right

def des_encrypt(plaintext_bin, key, rounds=4):
    left = plaintext_bin[:len(plaintext_bin)//2]
    right = plaintext_bin[len(plaintext_bin)//2:]
    subkeys = [key[i:i+len(right)] for i in range(rounds)]

    for subkey in subkeys:
        left, right = feistel_round(left, right, subkey)
    return left + right

def des_decrypt(ciphertext_bin, key, rounds=4):
    left = ciphertext_bin[:len(ciphertext_bin)//2]
    right = ciphertext_bin[len(ciphertext_bin)//2:]
    subkeys = [key[i:i+len(right)] for i in range(rounds)]

    for subkey in reversed(subkeys):
        right, left = feistel_round(right, left, subkey)
    return left + right

def str_to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_str(bin_text):
    return ''.join(chr(int(bin_text[i:i+8], 2)) for i in range(0, len(bin_text), 8))

# Example
text = "HI"
key = "011011100101" * 2  # 24-bit repeated key (just for demo)
text_bin = str_to_bin(text)
cipher_bin = des_encrypt(text_bin, key)
plain_bin = des_decrypt(cipher_bin, key)

print("\nMini DES")
print("Encrypted (bin):", cipher_bin)
print("Decrypted:", bin_to_str(plain_bin))