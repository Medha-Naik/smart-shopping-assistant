from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from database import get_db_connection
import bcrypt

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def profile():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id=%s', (current_user.id,))
            user = cursor.fetchone()
            cursor.execute('SELECT COUNT(*) as count FROM wishlist WHERE user_id=%s', (current_user.id,))
            wishlist_count = cursor.fetchone()['count']
    return render_template('profile.html', user=user, wishlist_count=wishlist_count)


@profile_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id=%s', (current_user.id,))
            user = cursor.fetchone()

    if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return render_template('profile.html', user=user, wishlist_count=0, error='Current password is incorrect')

    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET password_hash=%s WHERE id=%s', (new_hash, current_user.id))
        conn.commit()

    return redirect(url_for('profile.profile'))