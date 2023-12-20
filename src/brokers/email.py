import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Body, Form


router = APIRouter()


async def send_email(email_message, smtp_username, smtp_password):
    # Configure your SMTP server settings here
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = smtp_username if smtp_username else "vivasvan@ultimateworld.io"
    SMTP_PASSWORD = smtp_password if smtp_password else os.environ.get("SMTP_PASSWORD")
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
    background_tasks: BackgroundTasks,
    recipient: str = Form(...),
    subject: str = Form(...),
    message_html: str = Form(...),
    smtp_username: str = Body(default=None),
    smtp_password: str = Body(default=None),
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
    background_tasks.add_task(send_email, msg, smtp_username, smtp_password)
    return {"message": "Email sending task has been added to the background queue"}
