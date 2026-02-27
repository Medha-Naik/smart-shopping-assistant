from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flipkart_scraper import scrape_flipkart
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from auth_service import register_user, login_user as auth_login
from database import get_db_connection
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import os
from wishlist_service import add_to_wishlist,remove_from_wishlist,get_wishlist
from apscheduler.schedulers.background import BackgroundScheduler
from price_checker import check_prices

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # dev only, remove in production

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRETS = 'client_secret.json'
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:5000/login/google/callback'
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


scheduler=BackgroundScheduler()
scheduler.add_job(check_prices,'interval',hours=6,max_instances=2)
scheduler.start()

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if user:
                return User(user['id'], user['user_name'], user['email'])
            return None


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/search")
def search_product():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'please provide a valid query'})
    data = scrape_flipkart(query)
    if not data:
        return jsonify({'error': 'no products found'})
    return jsonify(data)


@app.route("/result")
def result():
    return render_template('result.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = register_user(username, email, password)
        if user:
            user_obj = User(user['id'], user['user_name'], user['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('register.html', error='Email already exists')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = auth_login(email, password)
        if user:
            user_obj = User(user['id'], user['user_name'], user['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/login/google')
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


@app.route('/login/google/callback')
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
            return redirect(url_for('login'))

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

        user_obj = User(user['id'], user['user_name'], user['email'])
        login_user(user_obj)
        session.pop('oauth_state', None)
        return redirect(url_for('home'))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/wishlist/add', methods=['POST'])
@login_required
def wishlist_add():
    data=request.json
    raw_price=data.get('price','0')
    clean_price=raw_price.replace('₹','').replace(',','').strip()
    result=add_to_wishlist(
        user_id=current_user.id,
        product_name=data.get('name'),
        current_price=clean_price,
        image_url=data.get('image'),
        url=data.get('url'),
        target_price=data.get('target_price',None)
    )
    return jsonify({'success':True})

@app.route('/wishlist/remove',methods=['POST'])
@login_required
def wishlist_remove():
    data=request.json
    remove_from_wishlist(data.get('product_id'),current_user.id)
    return jsonify({'success':True})


@app.route('/wishlist')
@login_required
def wishlist():
    items=get_wishlist(current_user.id)
    return render_template('wishlist.html',items=items)

@app.route('/check-login')
def check_login():
    return jsonify({'logged_in':current_user.is_authenticated})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)