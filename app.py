from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect("activity.db") as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL
            )
        ''')

@app.route('/')
def index():
    with sqlite3.connect("activity.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM activities ORDER BY timestamp DESC")
        activities = cur.fetchall()
    return render_template('index.html', activities=activities)

@app.route('/add', methods=['POST'])
def add_activity():
    title = request.form['title']
    description = request.form['description']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect("activity.db") as conn:
        conn.execute("INSERT INTO activities (title, description, timestamp) VALUES (?, ?, ?)",
                     (title, description, timestamp))
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_activity(id):
    with sqlite3.connect("activity.db") as conn:
        conn.execute("DELETE FROM activities WHERE id = ?", (id,))
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    with sqlite3.connect("activity.db") as conn:
        cur = conn.cursor()

        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not title:
                return "Title is required!", 400  # Prevent IntegrityError

            cur.execute("""
                UPDATE activities
                SET title = ?, description = ?, timestamp = ?
                WHERE id = ?
            """, (title, description, timestamp, id))
            conn.commit()
            return redirect(url_for('index'))

        else:
            cur.execute("SELECT * FROM activities WHERE id = ?", (id,))
            activity = cur.fetchone()
            if activity is None:
                return "Activity not found", 404
            return render_template('edit.html', activity=activity)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


