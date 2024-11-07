import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///market.db'

    # Security settings
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'default_salt_value')  # Replace with a secure value

    # Email server configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'yousefzmarket@gmail.com')  # Replace with actual email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '1030204050Y!')  # Replace with actual password or app-specific password

    # Default sender for emails
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'yousefzmarket@gmail.com')

    # Security settings for cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit on uploads

    # Debugging: Print to confirm environment variables are loading correctly
    print("SECURITY_PASSWORD_SALT:", SECURITY_PASSWORD_SALT)
    print("MAIL_USERNAME:", MAIL_USERNAME)
    print("MAIL_PASSWORD:", MAIL_PASSWORD)  # Caution: Don't print sensitive data in production
    print("MAIL_DEFAULT_SENDER:", MAIL_DEFAULT_SENDER)
