
import os
import smtplib
from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv

PROJECT_DIR = Path("/root/linux-server-monitoring")
ENV_FILE = PROJECT_DIR / "config" / "email.env"

load_dotenv(ENV_FILE)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_email(subject, body):

    required_values = [
        SMTP_SERVER,
        EMAIL_SENDER,
        EMAIL_PASSWORD,
        EMAIL_RECEIVER,
    ]

    if not all(required_values):
        raise ValueError("Email configuration is incomplete.")

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = EMAIL_SENDER
    message["To"] = EMAIL_RECEIVER

    message.set_content(body)

    with smtplib.SMTP(
        SMTP_SERVER, SMTP_PORT, timeout=20
    ) as server:

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        server.send_message(message)

    print("Email notification sent successfully!")


if __name__ == "__main__":

    try:
        send_email(
            "Linux Server Monitoring - Test Email",
            """
Hello,

This is a test email from your Automated Linux
Server Monitoring project.

Gmail SMTP integration is working.

Regards,
Linux Server Monitoring System
"""
        )

    except Exception as error:
        print(f"Email delivery failed: {error}")
        raise SystemExit(1)
