import json, base64, secrets, os
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

PUBLIC_PEM  = os.getenv("RSA_PUBLIC_PEM").replace("\\n", "\n")
PRIVATE_PEM = os.getenv("RSA_PRIVATE_PEM").replace("\\n", "\n")

# --------- 工具 ---------
def _rsa_encrypt(plain: bytes) -> bytes:
    return PKCS1_OAEP.new(RSA.import_key(PUBLIC_PEM)).encrypt(plain)

def _rsa_decrypt(cip: bytes) -> bytes:
    return PKCS1_OAEP.new(RSA.import_key(PRIVATE_PEM)).decrypt(cip)

# --------- 对外 ---------
def encrypt_dict(obj: dict) -> str:
    """返回 JSON 字符串：{'k':rsa_enc_aes_key,'n':nonce,'t':tag,'d':ct}"""
    key = secrets.token_bytes(32)
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())
    return json.dumps({
        "k": base64.b64encode(_rsa_encrypt(key)).decode(),
        "n": base64.b64encode(cipher.nonce).decode(),
        "t": base64.b64encode(tag).decode(),
        "d": base64.b64encode(ct).decode()
    }, ensure_ascii=False)

def decrypt_dict(s: str) -> dict:
    """JSON 反序列化 → 解密 → 返回 dict；失败返回空 dict"""
    try:
        blob = json.loads(s)
        key = _rsa_decrypt(base64.b64decode(blob["k"]))
        cipher = AES.new(key, AES.MODE_GCM, nonce=base64.b64decode(blob["n"]))
        raw = cipher.decrypt_and_verify(base64.b64decode(blob["d"]),
                                        base64.b64decode(blob["t"]))
        return json.loads(raw.decode())
    except Exception:
        return {}
