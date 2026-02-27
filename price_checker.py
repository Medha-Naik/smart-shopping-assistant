from database import get_db_connection
from email_service import send_alert
from flipkart_scraper import scrape_price_by_url

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
        print(f"checking:item['product_name']")
        print(f"URL:{item['url']}")
        current_price=scrape_price_by_url(item['url'])
        print(f"scraped price:{current_price}")
        print(f"target_price:{item['target_price']}")

        if not current_price:
            continue

        print(f"Clean price: {current_price}")
        print(f"Condition: {current_price} <= {float(item['target_price'])}")

        if current_price<=float(item['target_price']):
            send_alert(
                to_email=item['email'],
                product_name=item['product_name'],
                current_price=current_price,
                target_price=item['target_price'],
                url=item['url']

            )