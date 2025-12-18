from flask import Blueprint, render_template, request, redirect, url_for
from models import get_conn

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/shop')
def shop_index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, price, stock FROM products')
    products = cur.fetchall()
    conn.close()
    return render_template('shop.html', products=products)

@shop_bp.route('/shop/add_to_cart', methods=['POST'])
def add_to_cart():
    # дуже простий приклад — створимо одразу замовлення з одним товаром
    product_id = int(request.form.get('product_id'))
    qty = int(request.form.get('quantity', 1))
    client_name = request.form.get('client_name', 'Guest')
    client_email = request.form.get('client_email', None)

    conn = get_conn()
    cur = conn.cursor()
    # створимо клієнта (якщо email вказаний — унікальний)
    client_id = None
    if client_email:
        try:
            cur.execute('INSERT OR IGNORE INTO clients (name, email) VALUES (?, ?)', (client_name, client_email))
            conn.commit()
        except Exception:
            pass
        cur.execute('SELECT id FROM clients WHERE email=?', (client_email,))
        row = cur.fetchone()
        client_id = row[0] if row else None
    # отримуємо ціну товару
    cur.execute('SELECT price, stock FROM products WHERE id=?', (product_id,))
    p = cur.fetchone()
    if not p:
        conn.close()
        return "Товар не знайдено", 404
    price, stock = p
    total = price * qty
    # створюємо замовлення
    cur.execute('INSERT INTO orders (client_id, status, total) VALUES (?, ?, ?)', (client_id, 'new', total))
    order_id = cur.lastrowid
    cur.execute('INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (?, ?, ?, ?)',
                (order_id, product_id, qty, price))
    # оновимо запас
    new_stock = max(stock - qty, 0)
    cur.execute('UPDATE products SET stock=? WHERE id=?', (new_stock, product_id))

    conn.commit()
    conn.close()
    return redirect(url_for('shop.shop_index'))

@shop_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, client_id, status, total, created_at FROM orders WHERE id=?', (order_id,))
    order = cur.fetchone()
    cur.execute('SELECT oi.product_id, p.name, oi.quantity, oi.price_at_order FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?', (order_id,))
    items = cur.fetchall()
    conn.close()
    return render_template('order_detail.html', order=order, items=items)