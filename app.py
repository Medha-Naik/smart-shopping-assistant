from flask import Flask,render_template, jsonify,request,redirect,url_for
from flask_cors import CORS
from flipkart_scraper import scrape_flipkart
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from auth_service import register_user,login_user as auth_login
from database import get_db_connection
from dotenv import load_dotenv
import os

app= Flask(__name__)
load_dotenv()

app.secret_key=os.getenv('SECRET_KEY')

CORS(app)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/search")
def search_product():
    query=request.args.get('q')
    if not query:
        return jsonify({'error':'please provide a valid query'})
    
    data=scrape_flipkart(query)
    if not data:
        return jsonify({'error':'no products found'})
    
    return jsonify(data)

@app.route("/result")
def result():
    return render_template('result.html')
    
class User(UserMixin):
    def __init__(self,id,username,email):
        self.id=id
        self.username=username
        self.email=email


@login_manager.user_loader
def load_user(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id =%s',(user_id,))
            user=cursor.fetchone()
            if user:
                return User(user['id'],user['user_name'],user['email'])
            return None

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

        user=register_user(username,email,password)

        if user:
            user_obj=User(user['id'],user['user_name'],user['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('register.html',error='email already exists')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=auth_login(email,password)


        if user:
            user_obj=User(user['id'],user['user_name'],user['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            return render_template('login_html',error='Invalid email or password')
        
    return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)

