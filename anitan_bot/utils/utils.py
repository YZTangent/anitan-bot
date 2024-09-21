import re

email_pattern = re.compile(
    r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]*\.?(nus\.edu|nus\.edu\.sg)$"
)

otp_pattern = re.compile(r"^\d{6}$")


def test_valid_nus_email(input):
    return email_pattern.fullmatch(input)


def test_valid_otp(input):
    return otp_pattern.fullmatch(input)
