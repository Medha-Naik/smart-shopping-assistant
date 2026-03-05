from flask import Blueprint,request,jsonify,session
from services.email_service import send_otp_email
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