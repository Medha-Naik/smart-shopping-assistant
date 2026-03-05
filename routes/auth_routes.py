from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import register_user, login_user as auth_login
from database import get_db_connection
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from dotenv import load_dotenv
import os

load_dotenv()

auth_bp = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRETS = 'client_secret.json'
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:5000/login/google/callback'
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = register_user(username, email, password)
        if user:
            from app import User
            user_obj = User(user['id'], user['user_name'], user['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('register.html', error='Email already exists')
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = auth_login(email, password)
        if user:
            from app import User
            user_obj = User(user['id'], user['user_name'], user['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@auth_bp.route('/login/google')
def google_login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt='consent')
    session['oauth_state'] = state
    session.modified = True
    return redirect(auth_url)


@auth_bp.route('/login/google/callback')
def google_callback():
    try:
        flow = Flow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRETS,
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI,
            state=session['oauth_state']
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            grequests.Request(),
            GOOGLE_CLIENT_ID
        )
        email = id_info.get('email')
        username = id_info.get('name')
        if not email:
            return redirect(url_for('auth.login'))
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
                if not user:
                    cursor.execute('''
                        INSERT INTO users(user_name, email, password_hash)
                        VALUES(%s, %s, %s) RETURNING *
                    ''', (username, email, 'google_oauth'))
                    user = cursor.fetchone()
                    conn.commit()
        from app import User
        user_obj = User(user['id'], user['user_name'], user['email'])
        login_user(user_obj)
        session.pop('oauth_state', None)
        return redirect(url_for('home'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@auth_bp.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')