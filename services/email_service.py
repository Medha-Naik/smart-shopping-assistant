import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

GMAIL=os.getenv('GMAIL')
GMAIL_PASSWORD=os.getenv('GMAIL_PASSWORD')

def send_alert(to_email,product_name,current_price,target_price,url):
    try:
        msg=MIMEMultipart()
        msg['From']=GMAIL
        msg['To']=to_email
        msg['Subject']=f'Price Drop Alert-{product_name}'

        body=f'''
        Good news! Price dropped!
        Product:{product_name}
        Current Price: ₹{current_price}
        Your Target: ₹{target_price}

        Buy now:{url}
        '''
        msg.attach(MIMEText(body,'plain'))

        with smtplib.SMTP('smtp.gmail.com',587)as server:
            server.starttls()
            server.login(GMAIL,GMAIL_PASSWORD)
            server.sendmail(GMAIL,to_email,msg.as_string())
            print(f"email sent to {to_email}")


    except Exception as e:
        print(f"email error:{e}")