import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="ugis"
)

class DiaryApp:

    def __init__(self):
        self.current_page = 1
        self.entries_per_page = 3
        self.root = tk.Tk()
        self.root.title("Доступ к заметкам")
        self.root.geometry("220x110")
        self.create_login_screen()

    def create_login_screen(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.grid(row=0, column=0, padx=10, pady=10)

        self.username_label = tk.Label(self.login_frame, text="Логин:")
        self.username_label.grid(row=0, column=0, )

        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(self.login_frame, text="Пароль:")
        self.password_label.grid(row=1, column=0, )

        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Войти", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)



    def login(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM vh WHERE login=%s AND password=%s", (username, password))

        if cursor.fetchone():
            messagebox.showinfo("Успешно", "Вход выполнен")
            self.open_diary_app()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


    def open_diary_app(self):
        diary_window = tk.Toplevel(self.root)
        diary_window.title("Заметки")

        entry_text = tk.Text(diary_window)
        entry_text.pack()

        confirm_button = tk.Button(diary_window, text="Подтвердить запись",
                                   command=lambda: self.confirm_entry(entry_text))
        confirm_button.pack()

        self.page_number_label = tk.Label(diary_window, text=f"Страница {self.current_page}")
        self.page_number_label.pack()

        self.entries_label = tk.Label(diary_window, text="")
        self.entries_label.pack()

        next_page_button = tk.Button(diary_window, text="Следующая страница", command=lambda: self.next_page())
        next_page_button.pack(side="top")

        previous_page_button = tk.Button(diary_window, text="Предыдущая страница", command=lambda: self.previous_page())
        previous_page_button.pack(side="top")

        self.load_entries()

        diary_window.mainloop()

    def next_page(self):
        self.current_page += 1
        self.page_number_label.config(text=f"Страница {self.current_page}")
        self.load_entries()

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.page_number_label.config(text=f"Страница {self.current_page}")
            self.load_entries()

    def load_entries(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT entry_text FROM diary_entries ORDER BY entry_date DESC LIMIT %s OFFSET %s",
                       (self.entries_per_page, (self.current_page - 1) * self.entries_per_page))

        entries = cursor.fetchall()
        entries_text = "\n\n".join([entry[0] for entry in entries])

        self.entries_label.config(text=entries_text)

    def confirm_entry(self, entry_text):
        entry_content = entry_text.get("1.0", "end-1c")

        cursor = mydb.cursor()
        cursor.execute("INSERT INTO diary_entries (entry_date, entry_text) VALUES (%s, %s)",
                       (datetime.now(), entry_content))
        mydb.commit()

        messagebox.showinfo("Успешно", "Запись сохранена")
        self.load_entries()


if __name__ == "__main__":
    diary_app = DiaryApp


app = DiaryApp()
app.root.mainloop()