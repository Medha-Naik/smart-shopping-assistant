import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


DB_CONFIG={
    'dbname':'pricepulse',
    'user':'postgres',
    'password':'Tzenz@23',
    'host':'localhost',
    'port': 5432
}

def get_db_connection():
    conn=psycopg2.connect(**DB_CONFIG,cursor_factory=RealDictCursor)
    return conn


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wishlist(
                           id SERIAL PRIMARY KEY,
                           product_id NOT NULL,
                           product_name VARCHAR(500) NOT NULL,
                           image_url text,
                           target_price DECIMAL(10,2),
                           current_price DECIMAL(10,2),
                           url TEXT,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

                ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prie_history(
                           id SERIAL PRIMARY KEY,
                           product_id NOT NULL,
                           product_name VARCHAR(500) NOT NULL,
                           price DECIMAL(10,2),
                           url text,
                           recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )            
                ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users(
                           id SERIAL PRIMARY KEY,
                           user_name VARCHAR(50) NOT NULL,
                           email VARCHAR(150) NOT NULL,
                           password_hash VARCHAR(255) NOT NULL,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                ''')
            conn.commit()


if __name__ =='__main__':
    conn=get_db_connection()
    print("Connected")
    conn.close()

    init_db()