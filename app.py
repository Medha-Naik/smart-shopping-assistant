from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_required, current_user
from database import get_db_connection
from dotenv import load_dotenv
from scrapers.flipkart_scraper import scrape_flipkart
from scrapers.girias_scraper import scrape_girias
from services.price_checker import check_prices
from routes.auth_routes import auth_bp
from routes.wishlist_routes import wishlist_bp
from routes.profile_routes import profile_bp
from routes.otp_routes import otp_bp
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
import os

load_dotenv()
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', hours=6, max_instances=2)
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

app.register_blueprint(auth_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(otp_bp)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search_product():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'please provide a valid query'})
    with ThreadPoolExecutor(max_workers=2) as executor:
        flipkart_future=executor.submit(scrape_flipkart,query)
        girias_future=executor.submit(scrape_girias,query)

        flipkart_results=flipkart_future.result()
        girias_results=girias_future.result()

    for r in flipkart_results:
        r['source']='Flipkart'
    
    data=flipkart_results+girias_results

    if not data:
        return jsonify({'error':'No products found'})
    return jsonify(data)

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/check-login')
def check_login():
    return jsonify({'logged_in': current_user.is_authenticated})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)