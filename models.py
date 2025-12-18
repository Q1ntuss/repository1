import sqlite3
from datetime import datetime

DB_NAME = 'db.sqlite'

def get_conn():
    """Повертає підключення до бази даних з Row factory"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ======= Ініціалізація бази =======
def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # Таблиця для відгуків користувачів
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')

    # Таблиця для продуктів (додано image)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        image TEXT
    )
    ''')

    # Таблиця для замовлень
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        total_price REAL NOT NULL,
        status TEXT NOT NULL,
        date TEXT NOT NULL
    )
    ''')

    # Таблиця для товарів у замовленнях
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    )
    ''')

    # Таблиця користувачів
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Таблиця контактних повідомлень
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

# ======= Feedback =======
def add_feedback(name, message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO feedback (name, message, created_at) VALUES (?, ?, ?)',
            (name, message, current_time)
        )
        conn.commit()

def get_feedbacks():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback ORDER BY id DESC')
        return [dict(row) for row in cursor.fetchall()]

def delete_feedback(fb_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM feedback WHERE id = ?', (fb_id,))
        conn.commit()

# ======= Products =======
def add_product(name, description, price, stock, image=None):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, description, price, stock, image) VALUES (?, ?, ?, ?, ?)',
            (name, description, price, stock, image)
        )
        conn.commit()

def get_products():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY id DESC')
        rows = cursor.fetchall()
        products = []
        for row in rows:
            p = dict(row)
            p['image_url'] = p['image'] if p['image'] else None
            products.append(p)
        return products

def delete_product(product_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()

def decrease_stock(product_id, quantity):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?',
            (quantity, product_id, quantity)
        )
        conn.commit()

# ======= Orders =======
def add_order(email, address, items):
    total_price = sum(item['price'] * item['quantity'] for item in items)
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "Нове"
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO orders (email, address, total_price, status, date) VALUES (?, ?, ?, ?, ?)',
            (email, address, total_price, status, date_now)
        )
        order_id = cursor.lastrowid
        for item in items:
            cursor.execute(
                'INSERT INTO order_items (order_id, name, price, quantity) VALUES (?, ?, ?, ?)',
                (order_id, item['name'], item['price'], item['quantity'])
            )
        conn.commit()
    return order_id

def get_order(order_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        row = cursor.fetchone()
        if row:
            order = dict(row)
            order['date'] = datetime.strptime(order['date'], '%Y-%m-%d %H:%M:%S')
            return order
        return None

def get_order_items(order_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
        return [dict(row) for row in cursor.fetchall()]

def update_order_status(order_id, status):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        conn.commit()

# ======= Users =======
def get_user_by_email(email):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_user(email, password):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()

# ======= Contact Messages =======
def add_contact_message(name, email, message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO contact_messages (name, email, message, created_at) VALUES (?, ?, ?, ?)',
            (name, email, message, current_time)
        )
        conn.commit()

def get_contact_messages():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contact_messages ORDER BY id DESC')
        return [dict(row) for row in cursor.fetchall()]

def delete_contact_message(msg_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contact_messages WHERE id = ?', (msg_id,))
        conn.commit()