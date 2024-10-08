import os

class Config:
   sqlite:///market.db   'sqlite:///market.db'
   SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
   MAIL_SERVER = 'smtp.gmail.com'
   MAIL_PORT = 587
   MAIL_USE_TLS = True
   MAIL_USERNAME =os.environ.get('MAIL_USERNAME')
   MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  
   MAIL_DEFAULT_SENDER = ('Your App Name', 'yousefzmarket@gmail.com')
   SESSION_COOKIE_SECURE = True  
   SESSION_COOKIE_HTTPONLY = True  
   MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
