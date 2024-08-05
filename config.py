import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456789.@localhost/contactpp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
