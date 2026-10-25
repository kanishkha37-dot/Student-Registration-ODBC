import os
import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc
from dotenv import load_dotenv

load_dotenv()

# Database connection
def connect_db():
    dsn = os.getenv("ODBC_DSN", "StudentDB")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")

    if not password:
        raise ValueError("Please configure DB_PASSWORD in the .env file.")

    connection_string = (
        f"DSN={dsn};"
        f"UID={user};"
        f"PWD={password};"
    )

    return pyodbc.connect(connection_string)


# Create the database table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.student_registration (
            student_id INTEGER PRIMARY KEY,
            student_name VARCHAR(100) NOT NULL,
            department VARCHAR(50) NOT NULL,
            year_of_study INTEGER NOT NULL,
            email VARCHAR(100),
            phone_no VARCHAR(15)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# Register a student
def register_student():
    student_id = id_entry.get().strip()
    name = name_entry.get().strip()
    department = department_box.get()
    year = year_box.get()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()

    if not student_id or not name:
        messagebox.showerror(
            "Validation Error",
            "Please enter Student ID and Student Name."
        )
        return

    if not student_id.isdigit() or int(student_id) < 1:
        messagebox.showerror(
            "Validation Error",
            "Student ID must be a positive integer."
        )
        return

    if not year:
        messagebox.showerror(
            "Validation Error",
            "Please select the year of study."
        )
        return

    if phone and (not phone.isdigit() or len(phone) > 15):
        messagebox.showerror(
            "Validation Error",
            "Phone number must contain up to 15 digits."
        )
        return

    conn = None
    cursor = None

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO public.student_registration
            (student_id, student_name, department,
             year_of_study, email, phone_no)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(student_id),
            name,
            department,
            int(year),
            email or None,
            phone or None
        ))

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Student registered successfully!"
        )

        clear_fields()
        display_students()

    except pyodbc.Error as error:
        if conn:
            conn.rollback()

        messagebox.showerror(
            "Database Error",
            f"Could not register student.\n\n{error}"
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Display registered students
def display_students():
    for item in student_table.get_children():
        student_table.delete(item)

    conn = None
    cursor = None

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT student_id, student_name, department,
                   year_of_study, email, phone_no
            FROM public.student_registration
            ORDER BY student_id
        """)

        for row in cursor.fetchall():
            student_table.insert("", tk.END, values=tuple(row))

        count_label.config(
            text=f"Total Registered Students: {len(student_table.get_children())}"
        )

    except Exception as error:
        messagebox.showerror(
            "Database Error",
            f"Could not retrieve student records.\n\n{error}"
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Clear input fields
def clear_fields():
    id_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    department_box.set("")
    year_box.set("")
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)


# Delete selected student
def delete_student():
    selected = student_table.selection()

    if not selected:
        messagebox.showwarning(
            "Selection Required",
            "Please select a student to delete."
        )
        return

    values = student_table.item(selected[0], "values")
    student_id = values[0]

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Delete student ID {student_id}?"
    )

    if not confirm:
        return

    conn = None
    cursor = None

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM public.student_registration
            WHERE student_id = ?
        """, (student_id,))

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Student record deleted successfully."
        )

        display_students()

    except Exception as error:
        if conn:
            conn.rollback()

        messagebox.showerror(
            "Database Error",
            str(error)
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Main application window
root = tk.Tk()
root.title("Student Registration System")
root.geometry("1050x650")
root.minsize(850, 550)

title_label = tk.Label(
    root,
    text="STUDENT REGISTRATION SYSTEM",
    font=("Arial", 18, "bold")
)
title_label.pack(pady=15)

form_frame = ttk.LabelFrame(
    root,
    text="Student Details",
    padding=15
)
form_frame.pack(fill="x", padx=20, pady=10)

ttk.Label(form_frame, text="Student ID").grid(
    row=0, column=0, padx=10, pady=8, sticky="w"
)
id_entry = ttk.Entry(form_frame, width=30)
id_entry.grid(row=0, column=1, padx=10, pady=8)

ttk.Label(form_frame, text="Student Name").grid(
    row=0, column=2, padx=10, pady=8, sticky="w"
)
name_entry = ttk.Entry(form_frame, width=30)
name_entry.grid(row=0, column=3, padx=10, pady=8)

ttk.Label(form_frame, text="Department").grid(
    row=1, column=0, padx=10, pady=8, sticky="w"
)
department_box = ttk.Combobox(
    form_frame,
    values=["AI & DS", "CSE", "IT", "ECE", "EEE"],
    state="readonly",
    width=27
)
department_box.grid(row=1, column=1, padx=10, pady=8)

ttk.Label(form_frame, text="Year of Study").grid(
    row=1, column=2, padx=10, pady=8, sticky="w"
)
year_box = ttk.Combobox(
    form_frame,
    values=["1", "2", "3", "4"],
    state="readonly",
    width=27
)
year_box.grid(row=1, column=3, padx=10, pady=8)

ttk.Label(form_frame, text="Email").grid(
    row=2, column=0, padx=10, pady=8, sticky="w"
)
email_entry = ttk.Entry(form_frame, width=30)
email_entry.grid(row=2, column=1, padx=10, pady=8)

ttk.Label(form_frame, text="Phone Number").grid(
    row=2, column=2, padx=10, pady=8, sticky="w"
)
phone_entry = ttk.Entry(form_frame, width=30)
phone_entry.grid(row=2, column=3, padx=10, pady=8)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(
    button_frame,
    text="Register Student",
    command=register_student
).grid(row=0, column=0, padx=8)

ttk.Button(
    button_frame,
    text="Clear Fields",
    command=clear_fields
).grid(row=0, column=1, padx=8)

ttk.Button(
    button_frame,
    text="Refresh Records",
    command=display_students
).grid(row=0, column=2, padx=8)

ttk.Button(
    button_frame,
    text="Delete Selected",
    command=delete_student
).grid(row=0, column=3, padx=8)

table_frame = ttk.LabelFrame(
    root,
    text="Registered Students",
    padding=10
)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

columns = (
    "ID", "Name", "Department",
    "Year", "Email", "Phone"
)

student_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    student_table.heading(column, text=column)
    student_table.column(column, width=140, anchor="center")

student_table.pack(fill="both", expand=True)

count_label = ttk.Label(
    root,
    text="Total Registered Students: 0"
)
count_label.pack(pady=8)


# Start the application
try:
    create_table()
    display_students()
except Exception as error:
    messagebox.showerror(
        "Connection Error",
        f"Could not connect to PostgreSQL.\n\n{error}"
    )

root.mainloop()