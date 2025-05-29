import random
import sys
from sympy import isprime

sys.stdout.reconfigure(encoding='utf-8')
char_map = {chr(i + 65): i for i in range(26)}
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
def rsa_keygen(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randrange(2, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)
    d = pow(e, -1, phi)
    return n, phi, e, d

def encrypt(m, e, n):
    return pow(m, e, n)

def game():
    print("🔐 RSA Encryption Game! 🎮")


    while True:
        try:
            p = int(input("🔢 Enter the first prime number (p): "))
            q = int(input("🔢 Enter the second prime number (q): "))
            if not (isprime(p) and isprime(q)):
                print("❌ One or both numbers are not prime. Please enter valid primes.")
                continue
            if p == q:
                print("❌ p and q should not be the same. Try again.")
                continue
            break
        except ValueError:
            print("❌ Invalid input. Please enter integers only.")

    n, phi, e, d = rsa_keygen(p, q)
    print(f"\n🔑 RSA Key Details:")
    print(f"  Prime p = {p}, Prime q = {q}")
    print(f"  n = {n}")
    print(f"  φ(n) = {phi}")
    print(f"  Public Key (e, n): ({e}, {n})")
    print(f"  Private Key (d, n): ({d}, {n})")

   
    word_list = ["HI", "CAT", "DOG"]
    word = random.choice(word_list)


    m_values = [char_map[char] for char in word]
    c_values = [encrypt(m, e, n) for m in m_values]

    print(f"\n📝 Your task: Encrypt the word '{word}' using the public key.")
    print(f"🔓 Use the public exponent e = {e} and n = {n}")
    print(f"🧠 Hint: A=0, B=1, ..., Z=25. Use the formula: c = m^e mod n")

    attempts = 3
    while attempts > 0:
        try:
            user_input = input(f"\n✍️ Enter the encrypted numbers for '{word}' separated by spaces: ")
            user_c_values = list(map(int, user_input.strip().split()))
        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by spaces.")
            continue

        if user_c_values == c_values:
            print("🎉 Correct! You encrypted the word successfully!")
            break
        else:
            attempts -= 1
            if attempts > 0:
                print(f"❌ Incorrect. Attempts remaining: {attempts}")
            else:
                print("💀 Game Over! No more attempts.")
                print(f"✔️ Correct encryption of '{word}' is: {' '.join(map(str, c_values))}")

game()