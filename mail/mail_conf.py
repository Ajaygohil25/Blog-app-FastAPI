from fastapi_mail import FastMail, MessageSchema,ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME ="ajayg.inexture@gmail.com",
    MAIL_PASSWORD = "sjdv xztl omhg kghz",
    MAIL_FROM = "ajayg.inexture@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
