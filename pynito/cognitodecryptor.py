import jwt
import requests
import base64
from Cryptodome.PublicKey import RSA

from helper import decode_base64urlUInt

class CognitoDecryptor():

    def __init__(self, cognito_endpoint, cognito_app_client_id):
        self.iss = f"https://{cognito_endpoint}"
        self.aud = cognito_app_client_id

        self.targetURL = f"https://{cognito_endpoint}/.well-known/jwks.json"
        self.cognito_keys = {}
        self.cognito_keys_update()


    def cognito_keys_update(self):
        response = requests.get(self.targetURL)
        COGNITO_KEYS = response.json()['keys']
        self.cognito_keys = {d['kid']: d for d in COGNITO_KEYS}


    def valid(self, cert, token_claim_type, both_token_claim=False):
        try:
            decryptedHeader = jwt.get_unverified_header(cert)
            kid = decryptedHeader['kid']
        except:
            return None

        if kid not in self.cognito_keys:
            self.cognito_keys_update()
            if kid not in self.cognito_keys:
                return None

        jwk = self.cognito_keys[kid]
        n = decode_base64urlUInt(jwk['n'])
        e = decode_base64urlUInt(jwk['e'])

        secret = RSA.construct((n, e)).exportKey()

        try:
            decoded = jwt.decode(cert, secret, issuer=self.iss, audience=self.aud)
        except:
            return None

        claim = decoded['token_use']

        if both_token_claim:
            if claim not in ['access', 'id']:
                return None
        else:
            if claim != token_claim_type:
                return None
        
        return decoded
