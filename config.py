class Config:
    SECRET_KEY = 'YOUR SECRET KEY'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///urls.db'
    MAIL_SERVER = 'smtp.email.com'
    MAIL_PORT = 000
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'email@email.com'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = 'email@email.com'