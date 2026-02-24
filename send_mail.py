import os
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
FROM_EMAIL = "riccardo.abrami@we-wealth.com"
TO_EMAIL = "oscar.logoteta@we-wealth.com"

SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

def send_email():
    subject = "Report giornaliero"
    body = "Questo è il report delle 9."

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    send_email()
