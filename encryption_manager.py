from cryptography.fernet import Fernet
import os


class EncryptionManager:
    def __init__(self):
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)

    def load_or_create_key(self):
        if not os.path.exists('secret.key'):
            with open('secret.key', 'wb') as key_file:
                key = Fernet.generate_key()
                key_file.write(key)
            return key

        with open('secret.key', 'rb') as key_file:
            return key_file.read()

    def encrypt_file(self, input_path, output_path):
        with open(input_path, 'rb') as f:
            data = f.read()
        encrypted = self.cipher.encrypt(data)
        with open(output_path, 'wb') as f:
            f.write(encrypted)

    def decrypt_file(self, input_path, output_path):
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        decrypted = self.cipher.decrypt(encrypted)
        with open(output_path, 'wb') as f:
            f.write(decrypted)