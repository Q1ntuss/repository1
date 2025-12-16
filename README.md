Простий, але функціональний веб-додаток, який демонструє роботу з фронтенд-технологіями (HTML, CSS, JavaScript), зовнішнім API та взаємодією з серверною частиною на базі MySQL. 🛠 Технології

Frontend: HTML5, CSS3, Vanilla JavaScript (ES6+)

Backend: 

База даних: MySQL

Зовнішні сервіси: REST API

📋 Функціональність

Клієнтська частина:

    Адаптивний інтерфейс з використанням CSS Flexbox/Grid

    Динамічне оновлення контенту без перезавантаження сторінки

    Валідація форм на стороні клієнта

    Взаємодія з API через JavaScript

Робота з API:

    Отримання даних із зовнішнього джерела

    Обробка JSON-відповідей

    Обробка помилок мережі та API

Робота з базою даних:

    Зберігання даних отриманих з API

    CRUD-операції з даними

    Запити з фільтрацією та сортуванням

🗂 Структура проєкту text

project/ │ ├── public/ │ ├── index.html │ ├── css/ │ │ └── style.css │ ├── js/ │ │ └── app.js │ └── images/ │ ├── server/ │ ├── server.js (або index.php) │ ├── config/ │ │ └── database.js │ ├── routes/ │ └── models/ │ ├── database/ │ ├── schema.sql │ └── sample_data.sql │ └── README.md

🔧 Налаштування БД sql

CREATE DATABASE app_database; USE app_database;

CREATE TABLE items ( id INT PRIMARY KEY AUTO_INCREMENT, title VARCHAR(255) NOT NULL, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, api_data JSON );

🌐 API ендпоінти

Зовнішнє API (приклад):

GET https://api.example.com/data - отримання даних

Власне API:

GET /api/items - отримати всі записи

POST /api/items - створити новий запис

PUT /api/items/:id - оновити запис

DELETE /api/items/:id - видалити запис

🚀 Запуск проєкту

Налаштування бази даних:

bash

mysql -u root -p < database/schema.sql

Запуск сервера:

bash

cd server npm install npm start

Відкрити в браузері: http://localhost:3000

📁 Основні файли

index.html - головна сторінка додатку

style.css - стилізація компонентів

app.js - основна логіка клієнтської частини

server.js - конфігурація сервера та маршрутизація

🔄 Типовий потік даних

Користувач відкриває веб-сторінку

JavaScript виконує запит до зовнішнього API

Отримані дані відображаються в інтерфейсі

При діях користувача дані відправляються на сервер

Сервер зберігає/оновлює дані в MySQL

Клієнт отримує підтвердження та оновлює інтерфейс

⚙️ Конфігурація

Створити файл .env у папці server: text

DB_HOST=localhost DB_USER=root DB_PASSWORD=password DB_NAME=app_database API_KEY=your_external_api_key_here PORT=3000

📝 Примітки

Проєкт використовує чисті технології без фреймворків

Підтримує CORS для безпечної комунікації

Містить базову обробку помилок

Може бути розширений додатковим функціоналом
