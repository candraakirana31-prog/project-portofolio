import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort
)
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Profile, Skill, Project, Message
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    )


def save_uploaded_image(file_storage, current_filename=None):
    """Menyimpan file gambar yang diupload dan mengembalikan nama filenya.
    Jika tidak ada file baru yang valid, filename lama (current_filename) dipertahankan."""
    if file_storage and file_storage.filename:
        if not allowed_file(file_storage.filename):
            flash('Format file tidak didukung. Gunakan PNG, JPG, JPEG, GIF, atau WEBP.', 'error')
            return current_filename, False
        filename = secure_filename(file_storage.filename)
        # Hindari nama file bentrok dengan menambahkan prefix unik
        unique_name = f"{os.urandom(4).hex()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file_storage.save(filepath)
        return unique_name, True
    return current_filename, True


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses halaman ini.', 'error')
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def get_profile():
    """Mengambil satu-satunya baris Profile, membuatnya jika belum ada."""
    profile = Profile.query.first()
    if profile is None:
        profile = Profile()
        db.session.add(profile)
        db.session.commit()
    return profile


@app.context_processor
def inject_globals():
    """Inject common template variables: site name, current year, and profile."""
    try:
        profile = get_profile()
    except Exception:
        profile = None
    return {
        'site_name': app.config.get('SITE_NAME', 'Portofolio'),
        'current_year': datetime.utcnow().year,
        'profile': profile,
    }


# ---------------------------------------------------------------------------
# Rute Halaman Publik
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    profile = get_profile()
    latest_projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    return render_template('index.html', profile=profile, projects=latest_projects)


@app.route('/about')
def about():
    profile = get_profile()
    return render_template('about.html', profile=profile, skills=profile.skills)


@app.route('/portfolio')
def portfolio():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('portfolio.html', projects=projects)


@app.route('/portfolio/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    profile = get_profile()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        pesan = request.form.get('message', '').strip()

        if not name or not email or not pesan:
            flash('Semua kolom wajib diisi.', 'error')
            return render_template('contact.html', profile=profile)

        new_message = Message(name=name, email=email, message=pesan)
        db.session.add(new_message)
        db.session.commit()
        flash('Pesan Anda berhasil terkirim. Terima kasih!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', profile=profile)


# ---------------------------------------------------------------------------
# Rute Autentikasi
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Selamat datang kembali, {user.username}!', 'success')
            next_url = request.args.get('next') or url_for('dashboard_index')
            return redirect(next_url)

        flash('Username atau password salah.', 'error')

    return render_template('dashboard/login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Rute Dashboard (Admin) - dilindungi login_required
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard_index():
    total_projects = Project.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    total_messages = Message.query.count()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    return render_template(
        'dashboard/index.html',
        total_projects=total_projects,
        unread_messages=unread_messages,
        total_messages=total_messages,
        recent_messages=recent_messages,
    )


# --- Manajemen Proyek (CRUD) ---

@app.route('/dashboard/projects')
@login_required
def dashboard_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('dashboard/projects.html', projects=projects)


@app.route('/dashboard/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technologies = request.form.get('technologies', '').strip()
        github_link = request.form.get('github_link', '').strip()
        live_link = request.form.get('live_link', '').strip()

        if not title or not description:
            flash('Judul dan deskripsi proyek wajib diisi.', 'error')
            return render_template('dashboard/add_project.html', form=request.form)

        image_file = request.files.get('image')
        filename, ok = save_uploaded_image(image_file, current_filename='default-project.png')
        if not ok:
            return render_template('dashboard/add_project.html', form=request.form)

        project = Project(
            title=title,
            description=description,
            technologies=technologies,
            github_link=github_link,
            live_link=live_link,
            image_file=filename or 'default-project.png',
        )
        db.session.add(project)
        db.session.commit()
        flash('Proyek baru berhasil ditambahkan.', 'success')
        return redirect(url_for('dashboard_projects'))

    return render_template('dashboard/add_project.html', form={})


@app.route('/dashboard/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title or not description:
            flash('Judul dan deskripsi proyek wajib diisi.', 'error')
            return render_template('dashboard/edit_project.html', project=project)

        project.title = title
        project.description = description
        project.technologies = request.form.get('technologies', '').strip()
        project.github_link = request.form.get('github_link', '').strip()
        project.live_link = request.form.get('live_link', '').strip()

        image_file = request.files.get('image')
        filename, ok = save_uploaded_image(image_file, current_filename=project.image_file)
        if not ok:
            return render_template('dashboard/edit_project.html', project=project)
        project.image_file = filename

        db.session.commit()
        flash('Proyek berhasil diperbarui.', 'success')
        return redirect(url_for('dashboard_projects'))

    return render_template('dashboard/edit_project.html', project=project)


@app.route('/dashboard/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Proyek berhasil dihapus.', 'success')
    return redirect(url_for('dashboard_projects'))


# --- Manajemen Profil ---

@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def dashboard_profile():
    profile = get_profile()

    if request.method == 'POST':
        profile.name = request.form.get('name', '').strip()
        profile.headline = request.form.get('headline', '').strip()
        profile.about = request.form.get('about', '').strip()
        profile.email = request.form.get('email', '').strip()
        profile.github_url = request.form.get('github_url', '').strip()
        profile.linkedin_url = request.form.get('linkedin_url', '').strip()

        photo = request.files.get('photo')
        filename, ok = save_uploaded_image(photo, current_filename=profile.photo)
        if not ok:
            return render_template('dashboard/profile.html', profile=profile)
        profile.photo = filename

        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('dashboard_profile'))

    return render_template('dashboard/profile.html', profile=profile)


@app.route('/dashboard/profile/skills/add', methods=['POST'])
@login_required
def add_skill():
    profile = get_profile()
    name = request.form.get('skill_name', '').strip()
    if name:
        db.session.add(Skill(name=name, profile_id=profile.id))
        db.session.commit()
        flash(f'Skill "{name}" ditambahkan.', 'success')
    return redirect(url_for('dashboard_profile'))


@app.route('/dashboard/profile/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill dihapus.', 'success')
    return redirect(url_for('dashboard_profile'))


# --- Kotak Masuk Pesan ---

@app.route('/dashboard/messages')
@login_required
def dashboard_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('dashboard/messages.html', messages=messages)


@app.route('/dashboard/messages/read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    msg = Message.query.get_or_404(message_id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for('dashboard_messages'))


@app.route('/dashboard/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    msg = Message.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Pesan dihapus.', 'success')
    return redirect(url_for('dashboard_messages'))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# ---------------------------------------------------------------------------
# Inisialisasi database + akun admin default
# ---------------------------------------------------------------------------

def init_db():
    with app.app_context():
        db.create_all()

        if User.query.count() == 0:
            admin = User(username=app.config['DEFAULT_ADMIN_USERNAME'])
            admin.set_password(app.config['DEFAULT_ADMIN_PASSWORD'])
            db.session.add(admin)

        if Profile.query.count() == 0:
            db.session.add(Profile(
                name='Nama Anda',
                headline='Mahasiswa Informatika | Web Developer',
                about='Halo! Saya mahasiswa yang sedang belajar pengembangan web dengan Python dan Flask. '
                      'Ganti teks ini lewat menu Manajemen Profil di dashboard.',
                email='email@contoh.com',
            ))

        db.session.commit()


@app.before_request
def initialize_app_on_first_request():
    # Membuat fungsi ini hanya berjalan sekali saja
    app.before_request_funcs[None].remove(initialize_app_on_first_request)
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
