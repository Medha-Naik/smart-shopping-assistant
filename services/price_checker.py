from database import get_db_connection
from services.email_service import send_alert
from scrapers.flipkart_scraper import flipkart_price
from scrapers.girias_scraper import girias_price


def check_prices():
    print("Running price check")
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT w.*,u.email
            FROM wishlist w 
            JOIN users u ON w.user_id=u.id
            WHERE w.target_price IS NOT NULL
''')
            items=cursor.fetchall()

    for item in items:
        
        if 'giriasindia.com' in item['url']:
            current_price=girias_price(item['url'])
        else:
            current_price=flipkart_price(item['url'])

        
        if not current_price:
            continue

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE wishlist SET current_price=%s WHERE id=%s''',(current_price,item['id']))
                conn.commit()
  
        if current_price<=float(item['target_price']):
            send_alert(
                to_email=item['email'],
                product_name=item['product_name'],
                current_price=current_price,
                target_price=item['target_price'],
                url=item['url']

            )