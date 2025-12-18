# Звіт з лабораторної роботи 4

## Реалізація бази даних для вебпроєкту

### Інформація про команду
- Назва команди:

- Учасники:
  ПІБ  Семенов Владислав Олександрович 
- ПІБ  Сасін Павло Васильович 
- ПІБ  Бондарук Владислав Анатолійович 
- ПІБ  Жук Максим Сергійович
## Завдання

### Обрана предметна область
редметна область вебзастосунку — інтернет-магазин із системою відгуків.
Необхідно зберігати такі дані:

Відгуки користувачів (ім’я, email, текст повідомлення, дата створення)

Товари (назва, опис, ціна, кількість на складі, дата додавання)

Замовлення (ім’я покупця, email, загальна сума, статус замовлення, дата створення)

Елементи замовлення (товар, кількість, ціна)

### Реалізовані вимоги

Вкажіть, які рівні завдань було виконано:

- [+] Рівень 1: Створено базу даних SQLite з таблицею для відгуків, реалізовано базові CRUD операції, створено адмін-панель для перегляду та видалення відгуків, додано функціональність магазину з таблицями для товарів та замовлень
- [+] Рівень 2: Створено додаткову таблицю, релевантну предметній області, реалізовано роботу з новою таблицею через адмін-панель, інтегровано функціональність у застосунок
- [+] Рівень 3: Розширено функціональність двома додатковими функціями, що суттєво покращують користувацький досвід

## Хід виконання роботи

### Підготовка середовища розробки

Опишіть процес налаштування:

- Версія Python
- Встановлені бібліотеки (Flask, SQLite3 тощо)
- Інші використані інструменти та розширення

### Структура проєкту

Наведіть структуру файлів та директорій вашого проєкту:

```
project/
├── app.py
├── models.py
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── feedback.py
│   └── shop.py
├── templates/
│   ├── base.html
│   ├── admin/
│   ├── feedback/
│   └── shop/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── db.sqlite
└── lab-reports/
    └── lab04-report-student-id.md
```

### Проектування бази даних

#### Схема бази даних

Опишіть структуру вашої бази даних:

```
Таблиця "feedback":
- id (INTEGER, PRIMARY KEY)
- name (TEXT, NOT NULL)
- email (TEXT, NOT NULL)
- message (TEXT, NOT NULL)
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Таблиця "products":
- id (INTEGER, PRIMARY KEY)
- name (TEXT, NOT NULL)
- description (TEXT)
- price (REAL, NOT NULL)
- stock (INTEGER, DEFAULT 0)
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

Таблиця "orders":
- id (INTEGER, PRIMARY KEY)
- customer_name (TEXT, NOT NULL)
- customer_email (TEXT, NOT NULL)
- total_amount (REAL, NOT NULL)
- status (TEXT, DEFAULT 'pending')
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

[Додайте інші таблиці, якщо реалізовано]
```



### Опис реалізованої функціональності

#### Система відгуків
Користувачі можуть залишати відгуки через форму зворотного зв’язку

Всі відгуки зберігаються в таблиці feedback

Адмін може переглядати та видаляти відгуки

#### Магазин

Опишіть функціональність магазину:

- Відображення каталогу товарів
- Додавання товарів до кошика
- Оформлення замовлення
- Управління товарами через адмін-панель

#### Адміністративна панель

Опишіть можливості адмін-панелі:

- Перегляд відгуків
- Управління товарами
- Управління замовленнями
- Інші функції

#### Додаткова функціональність (якщо реалізовано)
Таблиця order_items для відстеження конкретних товарів у замовленнях

Функції обчислення загальної суми замовлення та перегляду деталей замовлення через JOIN

## Ключові фрагменти коду

### Ініціалізація бази даних

Наведіть код створення таблиць у файлі `models.py`:

```python
import sqlite3

def init_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    # Створення таблиці feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Створення інших таблиць...

    conn.commit()
    conn.close()
```

### CRUD операції

Наведіть приклади реалізації CRUD операцій:

#### Створення (Create)

```python
def add_feedback(name, email, message):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)',
        (name, email, message)
    )
    conn.commit()
    conn.close()
```

#### Читання (Read)

```python
def get_all_feedback():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
    feedback = cursor.fetchall()
    conn.close()
    return feedback
```

#### Оновлення (Update)

```python
def update_order_status(order_id, status):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE orders SET status = ? WHERE id = ?',
        (status, order_id)
    )
    conn.commit()
    conn.close()
```

#### Видалення (Delete)

```python
def delete_feedback(feedback_id):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    conn.commit()
    conn.close()
```

### Маршрутизація

Наведіть приклади маршрутів для роботи з базою даних:

```python
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        add_feedback(name, email, message)
        flash('Дякуємо за ваш відгук!', 'success')
        return redirect(url_for('feedback'))
    return render_template('feedback.html')
```

### Робота зі зв'язками між таблицями

Наведіть приклад запиту з використанням JOIN для отримання пов'язаних даних:

```python
def get_order_details(order_id):
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.*, oi.quantity, p.name, p.price
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.id = ?
    ''', (order_id,))
    details = cursor.fetchall()
    conn.close()
    return details
```

## Розподіл обов'язків у команді

Опишіть внесок кожного учасника команди:

- ПІБ учасника 1: Семенов Владислав Олександрович (реалізація маршрутів)
- ПІБ учасника 2: Сасін Павло Васильович (адмін панель)
- ПІБ учасника 3: Бондарук Владислав Анатолійович (створення шаблонів)
- ПІБ учасника 4: Жук Максим Сергійович (тестування)

## Скріншоти

Додайте скріншоти основних функцій вашого вебзастосунку:

### Форма зворотного зв'язку

<img width="891" height="806" alt="image" src="https://github.com/user-attachments/assets/48ca4578-ae71-45b1-868d-0826ca801a99" />


### Каталог товарів

<img width="1896" height="859" alt="image" src="https://github.com/user-attachments/assets/7ca88276-7bc6-4c3c-abcc-02c8f53e1fe1" />


### Адміністративна панель

<img width="1437" height="834" alt="image" src="https://github.com/user-attachments/assets/bfcf756b-40f1-4af1-8f2d-2870cfc7dcbd" />


### Управління замовленнями

<img width="1920" height="868" alt="image" src="https://github.com/user-attachments/assets/7643a07c-baab-4a57-9cdf-c099617e3caf" />


### Додаткова функціональність

<img width="1917" height="869" alt="image" src="https://github.com/user-attachments/assets/746cb94c-c5b5-477e-a909-4612d72623d4" />


## Тестування 

### Сценарії тестування

Опишіть, які сценарії ви тестували:

Додавання нового відгуку та перевірка його відображення в адмін-панелі
Створення товару, додавання його до кошика та оформлення замовлення
Зміна статусу замовлення через адмін-панель
Видалення записів з бази даних
Перевірка валідації даних


## Висновки

Опишіть:

Успішно реалізовано систему відгуків та інтернет-магазин з базою даних
Отримані практичні навички роботи з SQLite та Flask
Труднощі: нормалізація таблиць, робота з JOIN
Командна робота організована через Git і розподіл обов’язків
Можливі покращення: система рейтингів, фільтри та пошук товарів

Очікувана оцінка: 7-9

Обґрунтування: Робота повністю відповідає вимогам рівнів 1 та 2, всі CRUD операції реалізовано, функціональність протестована, адмін-панель працює коректно.
