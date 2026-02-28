from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from services.wishlist_service import add_to_wishlist, remove_from_wishlist, get_wishlist
from database import get_db_connection

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('/wishlist/add', methods=['POST'])
@login_required
def wishlist_add():
    data = request.json
    raw_price = data.get('price', '0')
    clean_price = raw_price.replace('₹', '').replace(',', '').strip()
    add_to_wishlist(
        user_id=current_user.id,
        product_name=data.get('name'),
        current_price=clean_price,
        image_url=data.get('image'),
        url=data.get('url'),
        target_price=data.get('target_price', None)
    )
    return jsonify({'success': True})


@wishlist_bp.route('/wishlist/remove', methods=['POST'])
@login_required
def wishlist_remove():
    data = request.json
    remove_from_wishlist(data.get('product_id'), current_user.id)
    return jsonify({'success': True})


@wishlist_bp.route('/wishlist')
@login_required
def wishlist():
    items = get_wishlist(current_user.id)
    return render_template('wishlist.html', items=items)


@wishlist_bp.route('/wishlist/items')
@login_required
def get_wishlist_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT url FROM wishlist WHERE user_id=%s', (current_user.id,))
            items = cursor.fetchall()
    return jsonify([item['url'] for item in items])