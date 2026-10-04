from fastapi_mail import FastMail,ConnectionConfig , MessageSchema, MessageType
from config import Config
from pathlib import Path
from typing import List 
s =  Config

BASE_DIR =  Path(__file__).resolve().parent.parent

config = ConnectionConfig(
    MAIL_USERNAME= s.MAIL_USERNAME,
    MAIL_PASSWORD = s.MAIL_PASSWORD,  # type: ignore
    MAIL_FROM=  s.MAIL_FROM,
    MAIL_PORT= s.MAIL_PORT,
    MAIL_SERVER= s.MAIL_SERVER,
    MAIL_STARTTLS= True, 
    MAIL_SSL_TLS = False , 
    USE_CREDENTIALS=True , 
    VALIDATE_CERTS=True, 
    TEMPLATE_FOLDER= Path(BASE_DIR, 'templates')
    
    
) # type: ignore



mail = FastMail(config =  config)
def create_message(recipients: List[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, # type: ignore
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    return message
 