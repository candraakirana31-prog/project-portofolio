from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Akun untuk login ke dashboard admin."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Profile(db.Model):
    """Data profil pemilik portofolio yang ditampilkan di halaman publik."""
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, default='Nama Anda')
    headline = db.Column(db.String(200), default='Mahasiswa Informatika')
    about = db.Column(db.Text, default='Ceritakan sedikit tentang diri Anda di sini.')
    photo = db.Column(db.String(120), default='default-profile.png')
    email = db.Column(db.String(120), default='')
    github_url = db.Column(db.String(200), default='')
    linkedin_url = db.Column(db.String(200), default='')

    skills = db.relationship('Skill', backref='profile', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Profile {self.name}>'


class Skill(db.Model):
    """Satu item keahlian/skill milik profil (relasi one-to-many ke Profile)."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)

    def __repr__(self):
        return f'<Skill {self.name}>'


class Project(db.Model):
    """Satu item karya/proyek yang ditampilkan di halaman Portofolio."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(200))  # disimpan sebagai string dipisah koma
    image_file = db.Column(db.String(120), default='default-project.png')
    github_link = db.Column(db.String(200))
    live_link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def tech_list(self):
        if not self.technologies:
            return []
        return [t.strip() for t in self.technologies.split(',') if t.strip()]

    def __repr__(self):
        return f'<Project {self.title}>'


class Message(db.Model):
    """Pesan yang dikirim pengunjung lewat form kontak."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message from {self.name}>'
