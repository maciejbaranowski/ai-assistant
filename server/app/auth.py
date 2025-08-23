import os
import logging
from fastapi import HTTPException, Header

AUTH_TOKEN_SECRET = os.getenv("AUTH_TOKEN_SECRET")

def verify_token(x_auth: str = Header(..., alias="x-auth")):
    if x_auth != f"{AUTH_TOKEN_SECRET}":
        logging.error("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")
