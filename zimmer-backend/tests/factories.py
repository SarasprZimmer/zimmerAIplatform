from faker import Faker
fake = Faker()

def user_payload(email=None, role="manager"):
    return {
        "name": fake.name(),
        "email": email or fake.unique.email(),
        "password": "Passw0rd!",
        "role": role
    }

def creds(email):
    return {"email": email, "password": "Passw0rd!"}
