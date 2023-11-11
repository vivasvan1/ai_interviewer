import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from fastapi import APIRouter, BackgroundTasks

# Configure your SMTP server settings here
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "vivasvan@ultimateworld.io"
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

router = APIRouter()


async def send_email(email_message):
    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Use TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(email_message)
    except Exception as e:
        print(f"Error sending email: {str(e)}")


@router.post("/send_email")
async def send_email_background(
    recipient: str,
    subject: str,
    message_html: str,
    background_tasks: BackgroundTasks,
    message_body: Optional[str] = "",
):
    # Create an EmailMessage object
    msg = EmailMessage()
    # Set the HTML content of the email
    msg.set_content(message_html, subtype="html")

    # Set the plain text content as an alternative to HTML
    # msg.add_alternative(message_body, subtype="plain")

    msg["Subject"] = subject
    msg["From"] = "vivasvan@utimateworld.io"
    msg["To"] = recipient

    # Send the email in the background
    background_tasks.add_task(send_email, msg)
    return {"message": "Email sending task has been added to the background queue"}
