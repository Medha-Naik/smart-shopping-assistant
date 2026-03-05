from flask import Blueprint,request,jsonify,session
from services.email_service import send_otp_email
from database import get_db_connection
import bcrypt
import random
import time

otp_bp=Blueprint('otp',__name__)

@otp_bp.route('/send-otp',methods=['POST'])
def send_otp():
    data=request.json
    email=data.get('email')
    otp=str(random.randint(100000,999999))
    print(otp)
    session['otp']=otp
    session['otp_email']=email
    session['otp_expiry']=time.time()+600
    send_otp_email(email,otp)
    return jsonify({'success':True})

@otp_bp.route('/verify-otp',methods=['POST'])
def verify_otp():
    data=request.json
    otp=data.get('otp')

    if time.time()>session.get('otp_expiry',0):
        return jsonify({'success':False,'error':'OTP expired'})
    
    if otp== session.get('otp'):
        session.pop('otp',None)
        session.pop('otp_expiry',None)
        return jsonify({'success':True})
    else:
        return jsonify({'success':False,'error':'Invalid OTP'})

@otp_bp.route('/reset-password',methods=['POST'])
def reset_password():
    data=request.json
    email=data.get('email')
    password=data.get('password')

    new_hash=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATe users SET password_hash=%s WHERE email=%s',(new_hash,email))
        conn.commit()
    return jsonify({'success':True})