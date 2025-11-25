import tkinter as tk
from tkinter import font as tkfont, messagebox
import tkinter.ttk as ttk
import text_fields
from records import StoredData, Task
from datetime import datetime


def validate_task_input(title: str, due: str) -> bool:
    """Simple validation for task title and due date.

    - title: not empty
    - due: not empty and formatted as YYYY-MM-DD
    """
    title = title.strip()
    due = due.strip()

    if not title:
        messagebox.showerror("Validation Error", "Title cannot be empty.")
        return False

    if not due:
        messagebox.showerror(
            "Validation Error",
            "Due date cannot be empty.\nPlease use the format YYYY-MM-DD."
        )
        return False

    try:
        datetime.strptime(due, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Validation Error",
            "Due date must be in the format YYYY-MM-DD,\nfor example: 2025-03-15."
        )
        return False

    return True


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dark_bg = "#1e1e1e"
        panel_bg = "#2a2a2a"
        text_color = "#ffffff"
        accent = "#4e8cff"
        accent_hover = "#6ba0ff"

        self.configure(bg=dark_bg)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=panel_bg,
            fieldbackground=panel_bg,
            foreground=text_color,
            rowheight=40,
            borderwidth=0
        )
        style.layout("Treeview", [
            ("Treeview.treearea", {"sticky": "nswe"})
        ])

        style.configure(
            "Treeview.Heading",
            background="#333333",
            foreground=text_color,
            font=("Times New Roman", 13, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", accent)],
            foreground=[("selected", "#ffffff")]
        )

        style.configure(
            "TButton",
            background=panel_bg,
            foreground=text_color,
            padding=10,
            font=("Times New Roman", 12),
            borderwidth=0
        )
        style.map(
            "TButton",
            background=[("active", accent_hover)],
            foreground=[("active", "#ffffff")]
        )

        style.configure(
            "Danger.TButton",
            background="#b22222",
            foreground="#ffffff",
            padding=10,
            font=("Times New Roman", 12),
            borderwidth=0
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#ff4d4d")],
            foreground=[("active", "#ffffff")]
        )

        style.configure("TFrame", background=dark_bg)
        style.configure("TLabel", background=dark_bg, foreground=text_color)
        style.configure("TCheckbutton", background=dark_bg, foreground=text_color)

        self.data = StoredData()

        self.title_font = tkfont.Font(family="Times New Roman", size=22, weight="bold")

        container = tk.Frame(self, bg=dark_bg)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (TaskListPage, TaskEditPage, TaskCreatePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self, persist=self.data, bg=dark_bg)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("TaskListPage")

    def show_frame(self, page_name, tid=0):
        frame = self.frames[page_name]
        if page_name == "TaskEditPage" and tid != 0:
            frame.update(tid)
        elif hasattr(frame, "update"):
            frame.update()
        frame.tkraise()


class TaskListPage(tk.Frame):
    def __init__(self, parent, controller, persist=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.persist = persist

        header = tk.Label(
            self,
            text="To Do List",
            font=controller.title_font,
            fg="white",
            bg=self["bg"]
        )
        header.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)

        card = tk.Frame(self, bg="#252525", bd=0, highlightthickness=0)
        card.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        table_frame = tk.Frame(card, bg="#252525")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbarx = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbary = tk.Scrollbar(table_frame, orient=tk.VERTICAL)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "title", "due", "done"),
            selectmode="extended",
            yscrollcommand=scrollbary.set,
            xscrollcommand=scrollbarx.set,
            show="headings"
        )

        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Task")
        self.tree.heading("due", text="Due Date (YYYY-MM-DD)")
        self.tree.heading("done", text="Completed")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("title", width=320, anchor="w")
        self.tree.column("due", width=180, anchor="center")
        self.tree.column("done", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.selected = []

        btn_card = tk.Frame(self, bg="#252525", bd=0, highlightthickness=0)
        btn_card.grid(row=2, column=0, pady=(10, 20), padx=20, sticky="ew")

        btn_frame = tk.Frame(btn_card, bg="#252525")
        btn_frame.pack(padx=10, pady=10)

        ttk.Button(
            btn_frame,
            text="Add Task",
            command=lambda: controller.show_frame("TaskCreatePage")
        ).grid(row=0, column=0, padx=6)

        ttk.Button(
            btn_frame,
            text="Edit Task",
            command=self.edit_selected
        ).grid(row=0, column=1, padx=6)

        ttk.Button(
            btn_frame,
            text="Delete Task",
            style="Danger.TButton",
            command=self.delete_selected
        ).grid(row=0, column=2, padx=6)

        self.update()

    def on_select(self, event):
        self.selected = event.widget.selection()

    def edit_selected(self):
        if not self.selected:
            messagebox.showinfo("No Selection", "Please select a task to edit.")
            return
        tid = self.tree.item(self.selected[0])["values"][0]
        self.controller.show_frame("TaskEditPage", tid)

    def delete_selected(self):
        if not self.selected:
            messagebox.showinfo("No Selection", "Please select at least one task to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected task(s)?"
        )
        if not confirm:
            return

        for item in self.selected:
            tid = self.tree.item(item)["values"][0]
            try:
                self.persist.delete_data(tid)
                self.tree.delete(item)
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to delete task.\n{e}")

        self.selected = []

    def update(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            for task in self.persist.get_all_sorted_data():
                done_str = "Yes" if task.completed else "No"
                self.tree.insert("", "end", values=(task.tid, task.title, task.due_date, done_str))
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load tasks.\n{e}")


class TaskEditPage(tk.Frame):
    def __init__(self, parent, controller, persist=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.persist = persist

        title = tk.Label(
            self,
            text="Edit Task",
            font=controller.title_font,
            fg="white",
            bg=self["bg"]
        )
        title.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        card = tk.Frame(self, bg="#252525", bd=0, highlightthickness=0)
        card.grid(row=1, column=0, padx=20, pady=10, sticky="nw")

        form_frame = tk.Frame(card, bg="#252525")
        form_frame.pack(padx=20, pady=20)

        self.data = {}
        self.data["Title"] = text_fields.TextField(form_frame, label="Title")
        self.data["Title"].grid(row=0, column=0, pady=5)

        self.data["Due"] = text_fields.TextField(form_frame, label="Due Date (YYYY-MM-DD)")
        self.data["Due"].grid(row=1, column=0, pady=5)

        self.completed_var = tk.IntVar()
        tk.Checkbutton(
            form_frame,
            text="Completed",
            variable=self.completed_var,
            fg="white",
            bg=form_frame["bg"]
        ).grid(row=2, column=0, pady=5, sticky="w")

        btn_frame = tk.Frame(card, bg="#252525")
        btn_frame.pack(padx=20, pady=(0, 20))

        ttk.Button(
            btn_frame,
            text="Update Task",
            command=self.submit
        ).grid(row=0, column=0, padx=6, pady=5)

        ttk.Button(
            btn_frame,
            text="Back to List",
            command=lambda: controller.show_frame("TaskListPage")
        ).grid(row=0, column=1, padx=6, pady=5)

        self.task = None

    def update(self, tid):
        task = self.controller.data.get_data(tid)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return
        self.data["Title"].text_entry.set(task.title)
        self.data["Due"].text_entry.set(task.due_date)
        self.completed_var.set(1 if task.completed else 0)
        self.task = task

    def submit(self):
        if not self.task:
            messagebox.showerror("Error", "No task loaded.")
            return

        title = self.data["Title"].get()
        due = self.data["Due"].get()

        if not validate_task_input(title, due):
            return

        self.task.title = title.strip()
        self.task.due_date = due.strip()
        self.task.completed = bool(self.completed_var.get())

        try:
            self.persist.save_data(self.task)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update task.\n{e}")
            return

        self.controller.show_frame("TaskListPage")


class TaskCreatePage(tk.Frame):
    def __init__(self, parent, controller, persist=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.persist = persist

        title = tk.Label(
            self,
            text="Add New Task",
            font=controller.title_font,
            fg="white",
            bg=self["bg"]
        )
        title.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        card = tk.Frame(self, bg="#252525", bd=0, highlightthickness=0)
        card.grid(row=1, column=0, padx=20, pady=10, sticky="nw")

        form_frame = tk.Frame(card, bg="#252525")
        form_frame.pack(padx=20, pady=20)

        self.data = {}
        self.data["Title"] = text_fields.TextField(form_frame, label="Title")
        self.data["Title"].grid(row=0, column=0, pady=5)

        self.data["Due"] = text_fields.TextField(form_frame, label="Due Date (YYYY-MM-DD)")
        self.data["Due"].grid(row=1, column=0, pady=5)

        self.completed_var = tk.IntVar()
        tk.Checkbutton(
            form_frame,
            text="Completed",
            variable=self.completed_var,
            fg="white",
            bg=form_frame["bg"]
        ).grid(row=2, column=0, pady=5, sticky="w")

        btn_frame = tk.Frame(card, bg="#252525")
        btn_frame.pack(padx=20, pady=(0, 20))

        ttk.Button(
            btn_frame,
            text="Submit",
            command=self.submit
        ).grid(row=0, column=0, padx=6, pady=5)

        ttk.Button(
            btn_frame,
            text="Back to List",
            command=lambda: controller.show_frame("TaskListPage")
        ).grid(row=0, column=1, padx=6, pady=5)

    def reset(self):
        for key in self.data:
            self.data[key].reset()
        self.completed_var.set(0)

    def update(self):
        self.reset()

    def submit(self):
        title = self.data["Title"].get()
        due = self.data["Due"].get()

        if not validate_task_input(title, due):
            return

        t = Task(
            title=title.strip(),
            due_date=due.strip(),
            completed=bool(self.completed_var.get())
        )
        try:
            self.persist.save_data(t)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save task.\n{e}")
            return

        self.reset()
        self.controller.show_frame("TaskListPage")


if __name__ == "__main__":
    app = App()
    app.title("To Do List")
    app.geometry("720x520")
    app.mainloop()
