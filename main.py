from fastapi import FastAPI, Query
from pydantic import EmailStr
from email_validator import validate_email, EmailNotValidError
from typing import Union

app = FastAPI(title="Email Validation API")

port = 10000

@app.get("/")
def welcome():
    return {"message": "Email Validation API is Running 🔥"}

@app.get("/validate-email/")
def validate(email: EmailStr = Query(example="user@gmail.com")):
    try:
        email_info = validate_email(email)
        return {
            "is_email_valid": True,
            "email": email_info.email,
            "domain": email_info.domain
        }
    except EmailNotValidError:
        return {
            "is_email_valid": False,
            "email": email,
            "message": "Invalid Email Address"
        }

@app.head("/")
async def head():
    return {"status": "Server is Running 🔥"}

