import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Database setup
DB_NAME = "tasks.db"


def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'To Do'
        )
    ''')
    conn.commit()
    conn.close()


class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.geometry("700x700")

        # Task List
        self.tree = ttk.Treeview(self, columns=("ID", "Title", "Description", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Status", text="Status")
        self.tree.column("ID", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)

        self.add_button = tk.Button(self.button_frame, text="Add Task", command=self.open_add_task_window)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit Task", command=self.open_edit_task_window)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.load_tasks()

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def open_add_task_window(self):
        TaskEditor(self, "Add Task", None)

    def open_edit_task_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return

        task_id = self.tree.item(selected_item)["values"][0]
        TaskEditor(self, "Edit Task", task_id)

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        task_id = self.tree.item(selected_item)["values"][0]
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        self.load_tasks()


class TaskEditor(tk.Toplevel):
    def __init__(self, parent, title, task_id):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("350x350")
        self.task_id = task_id

        # Title
        tk.Label(self, text="Title:").pack(pady=5)
        self.title_entry = tk.Entry(self)
        self.title_entry.pack(fill=tk.X, padx=10)

        # Description
        tk.Label(self, text="Description:").pack(pady=5)
        self.description_entry = tk.Entry(self)
        self.description_entry.pack(fill=tk.X, padx=10)

        # Status
        tk.Label(self, text="Status:").pack(pady=5)
        self.status_var = tk.StringVar(value="To Do")
        self.status_combo = ttk.Combobox(self, textvariable=self.status_var, values=["To Do", "In Progress", "Done"])
        self.status_combo.pack(fill=tk.X, padx=10)

        # Buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_task)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        if task_id:
            self.load_task()

    def load_task(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (self.task_id,))
        task = cursor.fetchone()
        conn.close()

        if task:
            self.title_entry.insert(0, task[1])
            self.description_entry.insert(0, task[2])
            self.status_var.set(task[3])

    def save_task(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        status = self.status_var.get()

        if not title:
            messagebox.showwarning("Validation Error", "Title cannot be empty.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if self.task_id:
            cursor.execute(
                "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?",
                (title, description, status, self.task_id),
            )
        else:
            cursor.execute(
                "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
                (title, description, status),
            )

        conn.commit()
        conn.close()

        self.parent.load_tasks()
        self.destroy()


if __name__ == "__main__":
    initialize_database()
    app = TaskManagerApp()
    app.mainloop()
