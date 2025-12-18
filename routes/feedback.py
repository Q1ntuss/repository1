from flask import Blueprint, request, render_template, redirect, url_for
import sqlite3
from models import get_conn

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    conn = get_conn()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name', 'Анонім')
        message = request.form.get('message', '')
        if message.strip():
            cur.execute('INSERT INTO feedback (name, message) VALUES (?, ?)', (name, message))
            conn.commit()
        conn.close()
        return redirect(url_for('feedback.feedback'))
    cur.execute('SELECT id, name, message, created_at FROM feedback ORDER BY created_at DESC')
    feedbacks = cur.fetchall()
    conn.close()
    return render_template('feedback.html', feedbacks=feedbacks)