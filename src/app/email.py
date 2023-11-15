from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
from app.db.models import DbUsers
import jwt


config = ConnectionConfig(
    MAIL_USERNAME="g4jobshub@gmail.com",
    MAIL_PASSWORD="hjxs yhvy fxrr prjq",
    MAIL_FROM="g4jobshub@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


async def send_email(email: List, instance: DbUsers):
    token_data = {
        'id': instance.id,
        'username': instance.username
    }

    token = jwt.encode(token_data, 'mnogosekretenkey', algorithm='HS256')
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
                    href="http://localhost:8000/verification/?token={token}">
                    Verify your email
                    </a>
                    
                    <p>Please do not reply to this email</p>
                    
                </div>
            </body>
        </html>
        '''
    message = MessageSchema(
        subject='Job Match Account Verification Email',
        recipients=email,
        body=template,
        subtype='html'
    )

    fm = FastMail(config)
    await fm.send_message(message=message)

