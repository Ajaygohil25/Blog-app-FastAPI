from fastapi_mail import FastMail, MessageSchema, MessageType
from conf import conf

async def send_mail(email: str, subject: str, content: str):
    template = f"""
		<html>
          <body style="background-color: #000; color: #fff; padding: 20px; font-family: Arial, sans-serif;">
            <h2 style="margin-bottom: 10px;">It's from Blog Application</h2>
            <p>Sending mail for: <strong>{subject}</strong></p>
            <p>{content}</p>
            <p>Thanks for using Blog app. We hope you enjoy it!</p>
          </body>
        </html>
		"""

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[email],
        body=template,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    print(message)

