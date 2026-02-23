import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()


DB_CONFIG={
    "dbname":os.getenv("DB_NAME"),
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "host":os.getenv("DB_HOST"),
    "port":os.getenv("DB_PORT")
}

def get_db_connection():
    conn=psycopg2.connect(**DB_CONFIG,cursor_factory=RealDictCursor)
    return conn


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users(
                           id SERIAL PRIMARY KEY,
                           user_name VARCHAR(50) NOT NULL,
                           email VARCHAR(150) NOT NULL UNIQUE,
                           password_hash VARCHAR(255) NOT NULL,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wishlist(
                           id SERIAL PRIMARY KEY,
                           user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                           product_name VARCHAR(500) NOT NULL,
                           image_url text,
                           target_price DECIMAL(10,2),
                           current_price DECIMAL(10,2),
                           url TEXT,
                           UNIQUE(user_id, url),
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                           
                ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history(
                           id SERIAL PRIMARY KEY,
                           product_id INTEGER NOT NULL,
                           product_name VARCHAR(500) NOT NULL,
                           price DECIMAL(10,2),
                           url text,
                           recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )            
                ''')
        
            conn.commit()


if __name__ =='__main__':
    conn=get_db_connection()
    print("Connected")
    conn.close()

    init_db()