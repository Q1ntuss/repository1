from flask import Blueprint, render_template, redirect, url_for, request
from models import get_conn

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin():
    conn = get_conn()
    cur = conn.cursor()
    # витягаємо відгуки, товари та замовлення
    cur.execute('SELECT id, name, message, created_at FROM feedback ORDER BY created_at DESC')
    feedbacks = cur.fetchall()
    cur.execute('SELECT id, name, price, stock FROM products')
    products = cur.fetchall()
    cur.execute('SELECT id, client_id, status, total, created_at FROM orders ORDER BY created_at DESC')
    orders = cur.fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks, products=products, orders=orders)

@admin_bp.route('/admin/delete_feedback/<int:fid>')
def delete_feedback(fid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM feedback WHERE id=?', (fid,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin'))

# зниження/збільшення статусу замовлення (приклад зміни)
@admin_bp.route('/admin/change_order_status/<int:order_id>', methods=['POST'])
def change_order_status(order_id):
    new_status = request.form.get('status')
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE orders SET status=? WHERE id=?', (new_status, order_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin'))

# CRUD для товарів (простий приклад додати/видалити)
@admin_bp.route('/admin/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = float(request.form.get('price', 0))
    stock = int(request.form.get('stock', 0))
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', (name, price, stock))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/delete_product/<int:pid>')
def delete_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM products WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin'))