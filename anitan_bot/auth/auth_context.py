import os
import secrets
import smtplib
import database.dbcontext as botdb
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Generates a random otp of length length and expires in duration seconds
def generate_otp(length=6, duration=300):
    return (
        "".join(secrets.choice("0123456789") for _ in range(length)),
        datetime.now() + timedelta(seconds=duration),
    )


def send_otp(receiver_email):
    otp = generate_otp()

    sender_email = os.environ.get("EMAIL_ADDRESS")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    subject = "Your NUSCAS OTP Code"
    body = f"Your OTP is: {otp[0]}.\nIt will expire in 5 minutes."

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        return otp

    except Exception as e:
        print(f"Failed to send OTP. Error: {e}")
