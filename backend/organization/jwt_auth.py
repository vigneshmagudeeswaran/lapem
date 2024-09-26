import json
import requests
from jose import jwt
from rest_framework import authentication, exceptions
from django.conf import settings

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return None
        
        try:
            token_type, token = auth.split()
            if token_type.lower() != 'bearer':
                raise exceptions.AuthenticationFailed('Authorization header must start with Bearer')

            payload = self.decode_jwt(token)
            return (payload, token)

        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid token')

    def decode_jwt(self, token):
        header = jwt.get_unverified_header(token)
        rsa_key = {}
        if 'kid' not in header:
            raise exceptions.AuthenticationFailed('Authorization malformed.')

        try:
            jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
            jwks = requests.get(jwks_url).json()
            for key in jwks['keys']:
                if key['kid'] == header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
        except Exception:
            raise exceptions.AuthenticationFailed('Unable to find appropriate key.')

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=settings.API_IDENTIFIER,
                issuer=f'https://{settings.AUTH0_DOMAIN}/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('token is expired')
        except jwt.JWTClaimsError:
            raise exceptions.AuthenticationFailed('incorrect claims, please check the audience and issuer')
        except Exception:
            raise exceptions.AuthenticationFailed('Unable to parse authentication token')

