import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ganti-kunci-rahasia-ini-sebelum-deploy')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    else:
        for prefix in ["postgres://", "postgresql://"]:
            if SQLALCHEMY_DATABASE_URI.startswith(prefix):
                target = "postgresql+psycopg2://"
                SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(prefix, target, 1)
                break

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'Candra Kirana')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'candrakiranaa31')
    SITE_NAME = os.environ.get('SITE_NAME', 'Portofolio')
