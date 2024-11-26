import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt

# Database Connection
def create_connection():
    try:
        return mysql.connector.connect(
            host="localhost",  # Change to your MySQL server
            user="root",       # Replace with your username
            password="Antim@123",  # Replace with your password
            database="Personal_Finance"  # Updated database name
        )
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
        return None

db = create_connection()
if db is None:
    exit()

cursor = db.cursor()

# Functions
def add_income():
    source = source_var.get()
    amount = amount_var.get()
    income_type = income_type_var.get()
    income_date = date_var.get()

    if not amount.isdigit() or float(amount) <= 0:
        messagebox.showerror("Input Error", "Amount must be a positive number.")
        return

    if source and income_type and income_date:
        try:
            query = "INSERT INTO income (source, type, amount, date) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (source, income_type, float(amount), income_date))
            db.commit()
            load_data()  # Refresh treeview
            reset_fields()
            messagebox.showinfo("Success", "Income added successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add income: {e}")
    else:
        messagebox.showerror("Input Error", "All fields are required.")

def delete_income():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected to delete.")
        return

    try:
        item = tree.item(selected_item)
        record_id = item['values'][0]
        cursor.execute("DELETE FROM income WHERE id = %s", (record_id,))
        db.commit()
        load_data()  # Refresh treeview
        messagebox.showinfo("Success", "Income deleted successfully!")
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to delete income: {e}")

def reset_fields():
    source_var.set('')
    amount_var.set('')
    income_type_var.set('Salary')
    date_var.set(datetime.now().strftime('%Y-%m-%d'))  # Reset to current date

def load_data(search_query=None):
    # Clear current entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Fetch from database
    try:
        if search_query:
            cursor.execute(search_query)
        else:
            cursor.execute("SELECT id, source, type, amount, DATE_FORMAT(date, '%Y-%m-%d') FROM income")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert('', 'end', values=row)
        calculate_total_income()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load data: {e}")

def calculate_total_income():
    total_income = 0
    for child in tree.get_children():
        values = tree.item(child, 'values')
        total_income += float(values[3])

    total_income_label.config(text=f"Total Income: ₹{total_income:.2f}")

def search_by_month():
    month_year = month_var.get().strip()
    if not month_year:
        messagebox.showerror("Input Error", "Please enter a valid month (YYYY-MM).")
        return

    try:
        query = f"SELECT id, source, type, amount, DATE_FORMAT(date, '%Y-%m-%d') FROM income WHERE DATE_FORMAT(date, '%Y-%m') = '{month_year}'"
        load_data(query)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to search data: {e}")

def show_this_month():
    current_month = datetime.now().strftime('%Y-%m')
    try:
        query = f"SELECT id, source, type, amount, DATE_FORMAT(date, '%Y-%m-%d') FROM income WHERE DATE_FORMAT(date, '%Y-%m') = '{current_month}'"
        load_data(query)
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load this month's data: {e}")
        


def analyze_this_month():
    """Analyze and display this month's income distribution in a pie chart."""
    current_month = datetime.now().strftime('%Y-%m')
    try:
        query = f"SELECT type, SUM(amount) FROM income WHERE DATE_FORMAT(date, '%Y-%m') = '{current_month}' GROUP BY type"
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
            plt.title("Income Distribution for This Month")
            plt.show()
        else:
            messagebox.showinfo("Analysis", "No income data available for this month.")
    except Exception as e:
        messagebox.showerror("Analysis Error", f"Failed to analyze this month's income: {e}")

def analyze_all():
    """Analyze and display all-time income distribution in a pie chart."""
    try:
        query = "SELECT type, SUM(amount) FROM income GROUP BY type"
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
            plt.title("All-Time Income Distribution")
            plt.show()
        else:
            messagebox.showinfo("Analysis", "No income data available.")
    except Exception as e:
        messagebox.showerror("Analysis Error", f"Failed to analyze all-time income: {e}")


def exit_application():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        root.destroy()

# Main Window
root = tk.Tk()
root.title("Income Management System")
root.attributes('-fullscreen', True)  # Fullscreen mode

# Input Section
frame_input = tk.Frame(root, padx=10, pady=10)
frame_input.pack(fill='x')

tk.Label(frame_input, text="Income Source: ").grid(row=0, column=0, padx=5, pady=5)
source_var = tk.StringVar()
tk.Entry(frame_input, textvariable=source_var, width=20).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_input, text="Amount: ").grid(row=0, column=2, padx=5, pady=5)
amount_var = tk.StringVar()
tk.Entry(frame_input, textvariable=amount_var, width=20).grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_input, text="Type: ").grid(row=0, column=4, padx=5, pady=5)
income_type_var = tk.StringVar(value="Salary")
ttk.Combobox(
    frame_input,
    textvariable=income_type_var,
    values=["Salary", "Business", "Investments", "Freelancing", "Other"],
    state="readonly",
    width=15
).grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_input, text="Date (YYYY-MM-DD): ").grid(row=0, column=6, padx=5, pady=5)
date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))  # Default to current date
tk.Entry(frame_input, textvariable=date_var, width=15).grid(row=0, column=7, padx=5, pady=5)

tk.Button(frame_input, text="Add Income", command=add_income, bg="green", fg="white", width=12).grid(row=0, column=8, padx=5, pady=5)

# Search Section
frame_search = tk.Frame(root, padx=10, pady=10)
frame_search.pack(fill='x')

tk.Label(frame_search, text="Search Month (YYYY-MM): ").grid(row=0, column=0, padx=5, pady=5)
month_var = tk.StringVar()
tk.Entry(frame_search, textvariable=month_var, width=20).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_search, text="Search by Month", command=search_by_month, bg="blue", fg="white", width=15).grid(row=0, column=2, padx=5, pady=5)
tk.Button(frame_search, text="Show This Month", command=show_this_month, bg="blue", fg="white", width=15).grid(row=0, column=3, padx=5, pady=5)

tk.Button(frame_search, text="Reset", command=lambda: [month_var.set(''), load_data()], bg="grey", fg="white", width=10).grid(row=0, column=4, padx=5, pady=5)

# Output Section
frame_output = tk.Frame(root, padx=10, pady=10)
frame_output.pack(fill='both', expand=True)

columns = ('ID', 'Income Source', 'Type', 'Amount', 'Date')
tree = ttk.Treeview(frame_output, columns=columns, show='headings', height=15)
tree.heading('ID', text='ID')
tree.heading('Income Source', text='Income Source')
tree.heading('Type', text='Type')
tree.heading('Amount', text='Amount')
tree.heading('Date', text='Date')
tree.column('ID', width=50)
tree.pack(fill='both', expand=True)

# Summary Section
frame_summary = tk.Frame(root, padx=10, pady=10)
frame_summary.pack(fill='x')

total_income_label = tk.Label(frame_summary, text="Total Income: ₹0.00", font=('Arial', 12), fg="green")
total_income_label.pack(side='left', padx=10)

# Delete and Exit Buttons
tk.Button(root, text="Delete Income", command=delete_income, bg="red", fg="white", width=12).place(x=970, y=15)
tk.Button(root, text="Exit", command=exit_application, bg="black", fg="white", width=12).place(x=root.winfo_screenwidth()-110, y=10)

# Buttons for Analysis
tk.Button(frame_search, text="Analyze This Month", command=analyze_this_month, bg="purple", fg="white", width=15).grid(row=0, column=5, padx=5, pady=5)
tk.Button(frame_search, text="Analyze All", command=analyze_all, bg="purple", fg="white", width=15).grid(row=0, column=6, padx=5, pady=5)

# Load data on startup
load_data()

# Mainloop
root.mainloop()
