from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
from app.db.models import DbUsers
from app.core.config import settings
from app.core.security import EMAIL_KEY, create_access_token

config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=587,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


async def send_email(email: List, instance: DbUsers):
    token_data = {
        'id': instance.id,
        'username': instance.username
    }

    token = create_access_token(token_data, settings.EMAIL_TOKEN_EXPIRE_MINUTES, EMAIL_KEY)
    template = f'''
        <!DOCKTYPE html>
        <html>
            <head>
            
            </head>
            <body>
                <div style = "display: flex; align-items: center; justify-content:
                center; flex-direction: column">
                
                    <h3>Account Verification </h3>
                    <br>
                    
                    <p>Please click the button below to verify account</p>
                    
                    <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem;
                    font-size: 1rem; text-decoration: none; background: #0275d8; color: white;"
                    href="https://job-match-c1sd.onrender.com/verification/?token={token}">
                    Verify your email
                    </a>
                    
                    <p>Please do not reply to this email</p>
                    
                </div>
            </body>
        </html>
        '''
    message = MessageSchema(
        subject='Account Verification Email',
        recipients=email,
        body=template,
        subtype='html'
    )

    fm = FastMail(config)
    await fm.send_message(message=message)
