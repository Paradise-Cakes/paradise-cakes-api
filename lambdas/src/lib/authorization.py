from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import boto3
import os
import requests
from aws_lambda_powertools.logging import Logger

logger = Logger()

REGION = os.environ.get("REGION", "us-east-1")
USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")
COGNITO_ISSUER = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_jwks():
    jwks_url = f"{COGNITO_ISSUER}/.well-known/jwks.json"
    try:
        jwks_response = requests.get(jwks_url)
        jwks_response.raise_for_status()
        return jwks_response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching JWKS: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch JWKS")


def verify_cognito_token(token: str) -> dict:
    try:
        jwks = get_jwks()
        unverified_headers = jwt.get_unverified_headers(token)
        kid = unverified_headers.get("kid")
        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=APP_CLIENT_ID,
                issuer=COGNITO_ISSUER,
            )
            return payload
        else:
            raise JWTError("Public key not found.")
    except JWTError as e:
        logger.error(f"JWT verification error: {e}")
        raise HTTPException(status_code=403, detail="Token verification failed")


def admin_only(token: str = Depends(oauth2_scheme)):
    logger.info(f"Checking token: {token}")
    payload = verify_cognito_token(token)
    user_groups = payload.get("cognito:groups", [])
    logger.info(f"User groups: {user_groups}")
    if "paradise-cakes-admin-group" not in user_groups:
        raise HTTPException(status_code=403, detail="Not enough permissions")
