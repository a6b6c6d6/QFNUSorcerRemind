import json, base64, os, secrets
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# 从环境变量读 PEM
PUBLIC_PEM  = os.getenv("RSA_PUBLIC_PEM").replace("\\n", "\n")
PRIVATE_PEM = os.getenv("RSA_PRIVATE_PEM").replace("\\n", "\n")

# --- 基础工具 ---
def _rsa_encrypt(plain: bytes) -> bytes:
    pub = RSA.import_key(PUBLIC_PEM)
    return PKCS1_OAEP.new(pub).encrypt(plain)

def _rsa_decrypt(cip: bytes) -> bytes:
    priv = RSA.import_key(PRIVATE_PEM)
    return PKCS1_OAEP.new(priv).decrypt(cip)

# --- 对外接口 ---
def encrypt_dict(obj: dict) -> str:
    """返回 base64 字符串：rsa_enc_aes_key|nonce|tag|ciphertext"""
    key = secrets.token_bytes(32)               # 256-bit AES key
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())
    blob = _rsa_encrypt(key) + b"|" + cipher.nonce + b"|" + tag + b"|" + ct
    return base64.b64encode(blob).decode()

def decrypt_dict(b64: str) -> dict:
    try:
        blob = base64.b64decode(b64.encode())
        # 最少要有 4 段（rsa|nonce|tag|ct）
        parts = blob.split(b"|")
        if len(parts) != 4:
            raise ValueError("Bad crypto format")
        rsa_key_size = RSA.import_key(PUBLIC_PEM).size_in_bytes()
        if len(parts[0]) != rsa_key_size:
            raise ValueError("RSA part length mismatch")
        key = _rsa_decrypt(parts[0])
        cipher = AES.new(key, AES.MODE_GCM, nonce=parts[1])
        raw = cipher.decrypt_and_verify(parts[3], parts[2])
        return json.loads(raw.decode())
    except Exception:
        # 任何异常都视为“无旧数据”
        return {}
