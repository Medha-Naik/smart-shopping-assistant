import bcrypt
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from database import get_db_connection


def register_user(username,email,password):
    password_hash= bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')


    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute('''
                    INSERT INTO users(user_name,email,password_hash)
                    VALUES(%s,%s,%s)
                    RETURNING id,user_name,email'''
                    ,(username,email,password_hash))
                user=cursor.fetchone()
                conn.commit()
                return user
            except Exception as e:
                conn.rollback()
                return None
        
def login_user(email,password):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT * FROM users WHERE email=%s''',(email,))

            user=cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'),user['password_hash'].encode('utf-8')) :
                return user
            return None
