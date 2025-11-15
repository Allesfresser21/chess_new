from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(80), nullable=False)  # Добавили username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username
        }

# Модель сообщения
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Связь с пользователем

    # Связываем с моделью User
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

    def __repr__(self):
        return f'<Feedback {self.name}>'
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tasks')
def tasks():
    return render_template('tasks.html')


@app.route('/links')
def links():
    return render_template('links.html')



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Создаём сообщение
        msg = Message(name=name, email=email, message=message)

        # Если пользователь авторизован — связываем с его аккаунтом
        if 'user_email' in session:
            user = User.query.filter_by(email=session['user_email']).first()
            if user:
                msg.user_id = user.id

        db.session.add(msg)
        db.session.commit()

        flash('Ваше сообщение отправлено!', 'success')
        return render_template('contact.html', message='success')

    # Для авторизованных пользователей: берём email из сессии
    initial_email = session.get('user_email', '')
    return render_template('contact.html', initial_email=initial_email)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']  # Добавляем username
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует.', 'error')
            return redirect(url_for('register'))

        user = User(email=email, username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Войдите в систему.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_email'] = email
            flash('Вы вошли в систему!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Неверный email или пароль.', 'error')

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_email' not in session:
        flash('Войдите в систему!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session['user_email']).first()
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
