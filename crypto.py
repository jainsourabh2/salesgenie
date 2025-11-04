from Crypto.Cipher import AES
import base64
import json

def encryptAES(data1):
    key = base64.b64decode('1234567890=')
    iv = base64.b64decode('1234==')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = _pad_data(json.dumps(data1).encode('utf-8'))
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')

def _pad_data(data):
    padding_length = AES.block_size - len(data) % AES.block_size
    padding = chr(padding_length) * padding_length
    return data + padding.encode('utf-8')
