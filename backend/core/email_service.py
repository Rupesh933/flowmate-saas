import os
import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = os.getenv("EMAIL_ADDRESS")
    message["To"] = to_email

    print(message, message["Subject"], message["From"], message["To"])

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(
                os.getenv("EMAIL_ADDRESS"),
                os.getenv("EMAIL_APP_PASSWORD")
            )
            smtp_server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False