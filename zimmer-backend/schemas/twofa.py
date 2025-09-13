from pydantic import BaseModel

class TwoFAInitiateOut(BaseModel):
    otpauth_uri: str

class TwoFAActivateIn(BaseModel):
    otp_code: str

class TwoFAVerifyIn(BaseModel):
    otp_code: str
    challenge_token: str

class TwoFAStatusOut(BaseModel):
    enabled: bool

class RecoveryCodesOut(BaseModel):
    codes: list[str]
