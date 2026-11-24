from fastapi import FastAPI

from codes import decrypt, encrypt
from config import CRIPTO_SECRET_KEY

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, this is a secret message!"}


@app.get("/secret")
def read_secret(message: str):
    encrypted = encrypt(message)
    # La misma clave con la que se cifró. decrypt exige (mensaje, clave).
    decrypted = decrypt(encrypted, CRIPTO_SECRET_KEY)
    return {"encrypted": encrypted, "decrypted": decrypted}
