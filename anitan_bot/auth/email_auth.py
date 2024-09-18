import secrets
from datetime import datetime, timedelta


# Generates a random otp of length length and expires in duration seconds
def generate_otp(length=6, duration=300):
    return (
        "".join(secrets.choice("0123456789") for _ in range(length)),
        datetime.now() + timedelta(seconds=duration),
    )
