import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",        # Change this if your database is not on localhost
    user="root",             # Assuming 'root' is the username
    password="Antim@123",    # Provided MySQL password
    database="Personal_Finance"  # Provided database name
)
cursor = db.cursor()

# Create budgets table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(255) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        date DATE NOT NULL
    )
''')

# Predefined categories
categories = [
    "Fixed Expenses",
    "Rent/Mortgage Payments",
    "Utilities",
    "Groceries",
    "Transportation",
    "Entertainment",
    "Healthcare",
    "Education",
    "Savings"
]

# Functions
def add_budget():
    category = category_var.get()
    amount = amount_var.get()
    expense_date = date_var.get()

    if not amount.isdigit():
        messagebox.showerror("Input Error", "Amount must be a positive number.")
        return

    if category and amount and expense_date:
        try:
            cursor.execute('INSERT INTO budgets (category, amount, date) VALUES (%s, %s, %s)', 
                           (category, float(amount), expense_date))
            db.commit()
            load_data()  # Refresh treeview
            reset_fields()
            update_charts()  # Update charts after adding a budget
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add budget: {e}")
    else:
        messagebox.showerror("Input Error", "All fields are required.")

def delete_budget():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected to delete.")
        return

    try:
        item = tree.item(selected_item)
        record_id = item['values'][0]  # Get ID from treeview
        cursor.execute('DELETE FROM budgets WHERE id = %s', (record_id,))
        db.commit()
        load_data()  # Refresh treeview
        update_charts()  # Update charts after deleting a budget
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete budget: {e}")

def reset_fields():
    category_var.set(categories[0])
    amount_var.set('')
    date_var.set(datetime.now().strftime("%Y-%m-%d"))  # Default to current date

def show_all():
    load_data()
    update_charts()  # Update charts when showing all

def search_budgets():
    search_type = search_type_var.get()
    search_value = search_item_var.get().strip()

    if not search_value:
        messagebox.showerror("Input Error", "Search value cannot be empty.")
        return

    query = f"SELECT * FROM budgets WHERE {search_type.lower()} LIKE %s"
    cursor.execute(query, (f"%{search_value}%",))
    filtered_budgets = cursor.fetchall()
    load_treeview(filtered_budgets)
    update_charts(filtered_budgets)  # Update charts based on search

def load_data():
    cursor.execute("SELECT * FROM budgets")
    all_budgets = cursor.fetchall()
    load_treeview(all_budgets)

def load_treeview(data):
    # Clear current entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Load data into the treeview
    for row in data:
        tree.insert('', 'end', values=row)

def update_charts(data=None):
    if data is None:
        cursor.execute("SELECT category, SUM(amount) FROM budgets GROUP BY category")
        data = cursor.fetchall()

    categories_data = {row[0]: row[1] for row in data}

    # Pie Chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(categories_data.values(), labels=categories_data.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    # Clear and embed pie chart
    for widget in frame_charts.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_charts)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.draw()

def save_to_file():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv")],
                                            title="Save as")
    if filepath:
        try:
            cursor.execute("SELECT * FROM budgets")
            rows = cursor.fetchall()
            with open(filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Category", "Amount", "Date"])  # Write header
                writer.writerows(rows)  # Write rows
            messagebox.showinfo("Export Successful", f"Data saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save file: {e}")

def import_from_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], title="Select a CSV file")
    if filepath:
        try:
            with open(filepath, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    cursor.execute('INSERT INTO budgets (category, amount, date) VALUES (%s, %s, %s)', 
                                   (row[1], float(row[2]), row[3]))
            db.commit()
            load_data()  # Refresh treeview
            update_charts()  # Update charts after importing data
            messagebox.showinfo("Import Successful", f"Data imported from {filepath}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file: {e}")


# Add this function to handle the delete functionality
def delete_budget():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a record to delete.")
        return

    # Get the selected item's ID
    item = tree.item(selected_item)
    record_id = item['values'][0]  # Assuming ID is the first column

    try:
        # Delete the record from the database
        cursor.execute("DELETE FROM budgets WHERE id = %s", (record_id,))
        db.commit()

        # Remove the record from the Treeview
        tree.delete(selected_item)

        # Update charts after deletion
        update_charts()

        messagebox.showinfo("Success", f"Record with ID {record_id} has been deleted.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete record: {e}")



def exit_application():
    db.close()
    root.destroy()

# Main Window
root = tk.Tk()
root.title("Budget Tracker")
root.geometry("1500x800")  # Set window size to 1500x800

font_style = ('Arial', 12)

# Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save File", command=save_to_file)
file_menu.add_command(label="Import File", command=import_from_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_application)

# Input Section
frame_input = tk.Frame(root, padx=20, pady=20)
frame_input.pack(fill='x')

# Row 1
tk.Label(frame_input, text="Category:", font=font_style).grid(row=0, column=0, padx=10, pady=10, sticky='w')
category_var = tk.StringVar(value=categories[0])  # Default to the first category
ttk.Combobox(frame_input, textvariable=category_var, values=categories, font=font_style, width=35, state="readonly").grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame_input, text="Amount:", font=font_style).grid(row=0, column=2, padx=10, pady=10, sticky='w')
amount_var = tk.StringVar()
tk.Entry(frame_input, textvariable=amount_var, font=font_style, width=20).grid(row=0, column=3, padx=10, pady=10)

# Row 2
tk.Label(frame_input, text="Date (YYYY-MM-DD):", font=font_style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))  # Default to current date
tk.Entry(frame_input, textvariable=date_var, font=font_style, width=20).grid(row=1, column=1, padx=10, pady=10)

tk.Button(frame_input, text="Add Budget", command=add_budget, bg="green", fg="white", font=font_style, width=15).grid(row=1, column=2, padx=10, pady=10)

# Search Section
frame_search = tk.Frame(root, padx=20, pady=20)
frame_search.pack(fill='x')

tk.Label(frame_search, text="Search By:", font=font_style).grid(row=0, column=0, padx=10, pady=10, sticky='w')
search_type_var = tk.StringVar(value="category")
search_type_cb = ttk.Combobox(frame_search, textvariable=search_type_var, values=["category", "amount", "date"], state="readonly", font=font_style, width=20)
search_type_cb.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame_search, text="Search Value:", font=font_style).grid(row=0, column=2, padx=10, pady=10, sticky='w')
search_item_var = tk.StringVar()
tk.Entry(frame_search, textvariable=search_item_var, font=font_style, width=30).grid(row=0, column=3, padx=10, pady=10)

tk.Button(frame_search, text="Search", command=search_budgets, bg="blue", fg="white", font=font_style, width=15).grid(row=0, column=4, padx=10, pady=10)

# Table Section
frame_table = tk.Frame(root)
frame_table.pack(fill='both', expand=True)

columns = ("ID", "Category", "Amount", "Date")
tree = ttk.Treeview(frame_table, columns=columns, show='headings', selectmode='browse')

# Set column headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill='both', expand=True)

# Chart Section
frame_charts = tk.Frame(root, padx=20, pady=20)
frame_charts.pack(side="bottom", fill='both', expand=True)


# Add the Delete Button to the frame_input
tk.Button(frame_input, text="Delete Selected", command=delete_budget, bg="red", fg="white", font=font_style, width=15).grid(row=1, column=3, padx=10, pady=10)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_application, bg="red", fg="white", font=font_style)
exit_button.place(relx=0.9, rely=0.02)

# Load data on startup
load_data()

# Mainloop
root.mainloop()
