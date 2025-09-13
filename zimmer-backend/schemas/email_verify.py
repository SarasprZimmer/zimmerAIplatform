from pydantic import BaseModel, EmailStr

class RequestVerifyIn(BaseModel):
    email: EmailStr

class VerifyEmailIn(BaseModel):
    token: str

class VerifyEmailOut(BaseModel):
    ok: bool
    message: str
