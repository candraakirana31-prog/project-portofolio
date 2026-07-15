import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Ganti SECRET_KEY ini dengan nilai acak yang kuat sebelum deploy ke production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ganti-kunci-rahasia-ini-sebelum-deploy')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'portfolio.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Batas upload 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Akun admin default yang dibuat otomatis saat database pertama kali dibuat.
    # SANGAT DISARANKAN untuk mengganti password ini lewat dashboard setelah login pertama kali.
    DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    # Nama situs yang tampil di header; ubah sesuai kebutuhan
    SITE_NAME = os.environ.get('SITE_NAME', 'Portofolio')
