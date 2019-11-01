import base64

def decode_base64urlUInt(val):
    return int.from_bytes(base64.urlsafe_b64decode(val + '=' * (4 - len(val) % 4)), 'big')