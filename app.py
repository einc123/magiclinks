tokens = {}

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import Config
from models import db, User, URL
from forms import EmailForm
import random
import string

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
mail = Mail(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        token = generate_token(email)
        send_magic_link(email, token)
        return redirect(url_for('check_your_email'))
    else:
        print(form.errors)
    return render_template('login.html', form=form)

@app.route('/check-email')
def check_your_email():
    return render_template('check_email.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/validate/<token>')
def validate_magic_link(token):
    email = tokens.get(token)
    if email:
        del tokens[token]
        
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        
        session['user'] = user.id
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid or expired link.', 'danger')
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user'])
    urls = URL.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', urls=urls)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    if 'user' not in session:
        return redirect(url_for('login'))
    original_url = request.form.get('url')
    shortened = generate_short_url()
    new_url = URL(original_url=original_url, shortened_url=shortened, user_id=session['user'])
    db.session.add(new_url)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/<shortened>')
def redirect_to_url(shortened):
    url = URL.query.filter_by(shortened_url=shortened).first_or_404()
    url.clicks += 1
    db.session.commit()
    return redirect(url.original_url)

def generate_token(email):
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    tokens[token] = email
    return token

def send_magic_link(email, token):
    link = url_for('validate_magic_link', token=token, _external=True)
    msg = Message('Your Magic Login Link', recipients=[email])
    msg.body = f'Click here to login to Euans URL Shortner: {link}'
    mail.send(msg)

def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def get_email_from_token(token):
    return "test@euanliv.click" if token == "valid_token" else None

@app.route('/delete/<int:url_id>', methods=['POST'])
def delete_url(url_id):
    url = URL.query.get_or_404(url_id)
    db.session.delete(url)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.cli.command("init-db")
def init_db():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)