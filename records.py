import sqlite3


class StoredData():
    FILENAME = "task_data.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.FILENAME)
        self.data_access = self.conn.cursor()

    def get_data(self, rid):
        self.data_access.execute("SELECT * FROM tasks WHERE task_id = ?;", (rid,))
        row = self.data_access.fetchone()
        if row is None:
            return None
        return Task(title=row[1], due_date=row[2], completed=bool(row[3]), tid=row[0])

    def get_all_data(self):
        self.data_access.execute("SELECT * FROM tasks;")
        tasks = []
        for row in self.data_access:
            tasks.append(Task(title=row[1], due_date=row[2], completed=bool(row[3]), tid=row[0]))
        return tasks

    def save_data(self, task):
        if task.tid == 0:
            self.data_access.execute(
                "INSERT INTO tasks(title, due_date, completed) VALUES (?, ?, ?)",
                (task.title, task.due_date, int(task.completed))
            )
            task.tid = self.data_access.lastrowid
        else:
            self.data_access.execute(
                "UPDATE tasks SET title = ?, due_date = ?, completed = ? WHERE task_id = ?",
                (task.title, task.due_date, int(task.completed), task.tid)
            )
        self.conn.commit()

    def get_all_sorted_data(self):
        return sorted(self.get_all_data(), key=lambda x: x.tid)

    def delete_data(self, rid):
        self.data_access.execute("DELETE FROM tasks WHERE task_id = ?", (int(rid),))
        self.conn.commit()

    def cleanup(self):
        if self.data_access:
            self.conn.commit()
            self.data_access.close()


class Task():
    def __init__(self, title="", due_date="", completed=False, tid=0):
        self.tid = tid
        self.title = title
        self.due_date = due_date
        self.completed = completed

    def __str__(self):
        return f"Task#{self.tid}: {self.title} (Due: {self.due_date}, Completed: {self.completed})"
