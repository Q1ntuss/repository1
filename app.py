import os
from flask import Flask, render_template, request, redirect, flash, jsonify, session, url_for
from flasgger import Swagger
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash  
from models import (
    init_db, add_feedback, get_feedbacks, delete_feedback,
    add_product, get_products, delete_product, decrease_stock,
    add_order, get_order, get_order_items, update_order_status,
    get_user_by_email, add_user,
    add_contact_message, get_contact_messages, delete_contact_message
)

DATABASE_PATH = os.environ.get("DATABASE_PATH", "data/database.db")
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'this_is_a_fixed_secret_key_for_dev'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.permanent_session_lifetime = 60*60*24  # 1 день

swagger = Swagger(app)
init_db()

ADMIN_PASSWORD = "admin12345"

# ======= HTML маршрути =======
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        add_contact_message(name, email, message)
        flash("Ваше повідомлення надіслано!", "success")
        return redirect('/contact')
    return render_template('contact.html')

@app.route('/shop')
def shop():
    products = get_products()
    return render_template('shop.html', products=products)

@app.route('/shop/add', methods=['GET', 'POST'])
def shop_add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        price = float(request.form['price'])
        stock = int(request.form['stock'])

        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = '/' + image_path.replace('\\', '/')

        add_product(name, description, price, stock, image=image_filename)
        flash(f"Продукт '{name}' додано!", "success")
        return redirect('/shop')
    return render_template('add_product.html')

@app.route('/shop/<int:product_id>')
def product_detail(product_id):
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash("Продукт не знайдено", "error")
        return redirect('/shop')
    return render_template('product_detail.html', product=product)

@app.route('/shop/delete/<int:product_id>')
def shop_delete(product_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    delete_product(product_id)
    flash("Продукт видалено.", "success")
    return redirect('/shop')

# ======= Кошик =======
@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in get_products() if p['id'] == product_id), None)
    if not product:
        flash("Продукт не знайдено", "error")
        return redirect('/shop')

    quantity = int(request.args.get('quantity', 1))
    if quantity <= 0:
        flash("Невірна кількість", "error")
        return redirect('/shop')

    if product['stock'] <= 0:
        flash(f"Товар '{product['name']}' закінчився на складі", "error")
        return redirect('/shop')

    if quantity > product['stock']:
        flash(f"В наявності лише {product['stock']} шт. товару '{product['name']}'", "error")
        return redirect('/shop')

    cart = session.get('cart', {})
    if str(product_id) in cart:
        new_quantity = cart[str(product_id)]['quantity'] + quantity
        if new_quantity > product['stock']:
            flash(f"Не можна додати більше {product['stock']} шт. товару '{product['name']}'", "error")
            return redirect('/shop')
        cart[str(product_id)]['quantity'] = new_quantity
    else:
        cart[str(product_id)] = {
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity
        }

    session['cart'] = cart
    flash(f"Додано {quantity} шт. '{product['name']}' до кошика", "success")
    return redirect('/shop')

# 🔴 ======= ДОДАНО: зменшити кількість на 1 =======
@app.route('/cart/decrease/<product_id>', methods=['POST'])
def decrease_cart_item(product_id):
    cart = session.get('cart', {})

    if product_id in cart:
        cart[product_id]['quantity'] -= 1
        if cart[product_id]['quantity'] <= 0:
            del cart[product_id]
        session['cart'] = cart

    return redirect(url_for('view_cart'))
# 🔴 =============================================

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash("Кошик порожній!", "error")
        return redirect('/shop')

    email = request.form['email']
    address = request.form['address']
    items = [v.copy() for v in cart.values()]

    for product_id_str, item in cart.items():
        decrease_stock(int(product_id_str), item['quantity'])

    order_id = add_order(email, address, items)
    session['cart'] = {}
    flash(f"Замовлення #{order_id} успішно створено!", "success")
    return redirect('/shop')

# ======= Feedback =======
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        add_feedback(request.form['name'], request.form['message'])
        return redirect('/feedback')

    feedbacks = get_feedbacks()
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/feedback/delete/<int:fb_id>')
def feedback_delete(fb_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    delete_feedback(fb_id)
    flash("Відгук видалено.", "success")
    return redirect('/feedback')

# ======= АДМІН ЛОГІН =======
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            session.permanent = True
            flash("Успішний вхід в адмін-панель", "success")
            return redirect('/admin')
        flash("Невірний пароль", "error")
        return redirect('/admin/login')
    return render_template('admin_login.html')

# ======= АДМІН-ПАНЕЛЬ =======
@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin/login')
    return render_template(
        'admin.html',
        feedbacks=get_feedbacks(),
        products=get_products(),
        contact_messages=get_contact_messages()
    )

@app.route('/contact/delete/<int:msg_id>')
def contact_delete(msg_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    delete_contact_message(msg_id)
    flash("Повідомлення видалено.", "success")
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("Ви вийшли з адмін-панелі", "success")
    return redirect('/admin/login')

# ======= API та Swagger =======
@app.route('/api/products', methods=['GET'])
def api_get_products():
    return jsonify(get_products())

# ---- Health ----
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# ======= Auth =======
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Паролі не співпадають", "error")
            return redirect('/register')

        if get_user_by_email(email):
            flash("Користувач вже існує", "error")
            return redirect('/register')

        add_user(email, generate_password_hash(password))
        flash("Реєстрація успішна!", "success")
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user_by_email(request.form['email'])
        if not user or not check_password_hash(user['password'], request.form['password']):
            flash("Невірні дані", "error")
            return redirect('/login')

        session['user_id'] = user['id']
        session['user_email'] = user['email']
        return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)