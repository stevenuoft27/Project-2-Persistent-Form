import sqlite3


def connect_database():
    global conn, cur
    conn = sqlite3.connect('task_data.db')
    cur = conn.cursor()


def create_database():
    cur.execute('DROP TABLE IF EXISTS contacts;')
    cur.execute('DROP TABLE IF EXISTS tasks;')
    cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        due_date TEXT,
        completed INTEGER NOT NULL DEFAULT 0
    );''')


def close_database():
    conn.commit()
    conn.close()


if __name__ == '__main__':
    connect_database()
    create_database()
    close_database()
