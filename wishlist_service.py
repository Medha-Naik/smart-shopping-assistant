

from database import get_db_connection

def add_to_wishlist(user_id,product_name,current_price,image_url,url,target_price):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                       INSERT INTO wishlist(user_id,product_name,current_price,image_url,url,target_price)values(%s,%s,%s,%s,%s,%s)
                         ON CONFLICT (user_id,url) DO NOTHING
                           RETURNING *
                            ''',(user_id,product_name,current_price,image_url,url,target_price))
            
            result=cursor.fetchone()
            conn.commit()
            return result
        

def remove_from_wishlist(product_id,user_id):
    
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                 cursor.execute('''
                 DELETE FROM wishlist WHERE id=%s AND user_id= %s
                 RETURNING * 
                ''',(product_id,user_id))
                 result=cursor.fetchone()
                 conn.commit()
                 return result
    
def update_target_price(product_id,user_id,new_target_price):          
        with get_db_connection() as conn:
             with conn.cursor() as cursor:
                  cursor.execute('''
                    UPDATE wishlist SET target_price=%s
                    WHERE id=%s AND user_id = %s
                    RETURNING *''',
                    (new_target_price,product_id,user_id))
                  result=cursor.fetchone()
                  conn.commit()
                  return result
             
def get_wishlist(user_id):
     with get_db_connection() as conn:
          with conn.cursor() as cursor:
               cursor.execute('''
                SELECT * FROM wishlist WHERE user_id=%s''',(user_id,))
               return cursor.fetchall()