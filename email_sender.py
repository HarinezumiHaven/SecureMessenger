import smtplib
import jwt
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config
from extensions import db
from flask_migrate import Migrate
from flask import current_app

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = config['email']
SMTP_PASSWORD = config['password']


def send_verification_email(user_email):
    token = jwt.encode({"email": user_email, "exp": datetime.datetime.now() + datetime.timedelta(hours=1)},
                       current_app.config['SECRET_KEY'], algorithm="HS256")
    verification_link = f"http://127.0.0.1:5000/verify/{token}"
    
    subject = "Registration confirmation"
    body = f"Hi! Click on this link to confirm your e-mail: {verification_link}"

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, user_email, msg.as_string())
    except:
        print(f"Failed to send email")

    print(f"List sended to {user_email}")
