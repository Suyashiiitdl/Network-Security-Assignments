def encrypt(message, e, n):
    message = message.encode()
    encrypted = pow(int.from_bytes(message, 'big'), int(e), int(n))
    return encrypted

def decrypt(encrypted, d, n):
    decrypted = pow(encrypted, int(d), int(n))
    decrypted = decrypted.to_bytes((decrypted.bit_length() + 7) // 8, 'big')
    return decrypted.decode()
