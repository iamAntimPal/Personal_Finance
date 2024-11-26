import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import mysql.connector

# MySQL Connection Setup
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="Antim@123", 
            database="Personal_Finance"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {err}")
        return None

# Sample in-memory list to store expenses (for reference, data will be pulled from MySQL)
expenses = []

# Predefined categories
categories = [
     "Groceries","Fixed Expenses", "Rent Payments", "Utilities (Electricity, Water, Gas, Internet, Phone)",
    "Insurance Premiums (Health, Auto, Life, Home)", "Subscription Services (Streaming platforms, Gym memberships, Magazines)",
    "Variable Expenses", "Transportation (Fuel, Public Transport, Ride-sharing)", "Dining Out",
    "Entertainment (Movies, Concerts, Hobbies)", "Clothing and Accessories", "Healthcare (Doctor visits, Medicines, Therapies)",
    "Education (Books, Tuition Fees, Courses)", "Gifts and Celebrations (Birthdays, Weddings)", "Irregular/One-time Expenses",
    "Vacations/Travel", "Home Repairs and Maintenance", "Large Purchases (Appliances, Furniture, Electronics)", "Emergencies (Medical, Vehicle Repairs)"
]

search_types = ["Item", "Category", "Payment Mode", "Date", "Amount"]

# Functions
def add_expense():
    category = category_var.get()
    item = item_var.get()
    amount = amount_var.get()
    quantity = quantity_var.get()
    expense_date = date_var.get()
    payment_mode = payment_mode_var.get()

    if not amount.isdigit() or not quantity.isdigit():
        messagebox.showerror("Input Error", "Amount and Quantity must be positive numbers.")
        return

    if category and item and expense_date and payment_mode:
        try:
            # Convert the date from DD-MM-YYYY to YYYY-MM-DD
            try:
                expense_date = datetime.strptime(expense_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Date Error", "Incorrect date format. Please use DD-MM-YYYY format.")
                return

            # Add expense to the database
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                query = """
                    INSERT INTO expenses (category, item, amount, quantity, date, payment_mode)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (category, item, float(amount), int(quantity), expense_date, payment_mode))
                connection.commit()
                connection.close()
                load_data()  # Refresh the data
                reset_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add expense: {e}")
    else:
        messagebox.showerror("Input Error", "All fields are required.")

# Create the database analysis
def show_analysis_pie():
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            # Query to fetch total expenses grouped by category
            query = """
                SELECT category, SUM(amount * quantity) AS total_expense
                FROM expenses
                GROUP BY category
                ORDER BY total_expense DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            if not results:
                messagebox.showinfo("No Data", "No data available for analysis.")
                return

            # Prepare data for plotting
            categories = [row[0] for row in results]
            total_expenses = [float(row[1]) for row in results]

            # Create the pie chart
            plt.figure(figsize=(8, 6))
            plt.pie(
                total_expenses, 
                labels=categories, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=plt.cm.Paired.colors
            )
            plt.title('Expense Distribution by Category', fontsize=16)
            plt.axis('equal')  # Equal aspect ratio to make the pie chart circular
            plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating analysis: {e}")
        
        
def show_analysis_this_month():
    try:
        # Get the current year and month
        current_month = datetime.now().strftime("%Y-%m")

        # Establish database connection
        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()

        # Query to fetch expenses grouped by category for the current month
        query = """
            SELECT category, SUM(amount * quantity) AS total_expense
            FROM expenses
            WHERE DATE_FORMAT(date, '%Y-%m') = %s
            GROUP BY category
            ORDER BY total_expense DESC
        """
        cursor.execute(query, (current_month,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        if not results:
            messagebox.showinfo("No Data", "No expenses found for this month.")
            return

        # Prepare data for the pie chart
        categories = [row[0] for row in results]
        total_expenses = [float(row[1]) for row in results]

        # Create the pie chart
        plt.figure(figsize=(8,6))
        plt.pie(
            total_expenses,
            labels=categories,
            autopct='%1.1f%%',
            startangle=140,
            colors=plt.cm.Paired.colors
        )
        plt.title('Expense Distribution for This Month', fontsize=16)
        plt.axis('equal')  # Ensure the pie chart is a circle
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating analysis: {e}")



def delete_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected to delete.")
        return

    try:
        item = tree.item(selected_item)
        record_id = int(item['values'][0])  # Use ID to find expense in the list
        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        query = "DELETE FROM expenses WHERE id = %s"
        cursor.execute(query, (record_id,))
        conn.commit()
        cursor.close()
        conn.close()

        load_data()  # Refresh table data

    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete expense: {e}")

def reset_fields():
    category_var.set(categories[0])
    item_var.set('')
    amount_var.set('')
    quantity_var.set('1')  # Default quantity
    date_var.set(datetime.now().strftime("%d-%m-%Y"))  # Default to current date
    payment_mode_var.set('Offline')

from datetime import datetime

def show_this_month():
    current_month = datetime.now().strftime("%Y-%m")  # Get the current year-month (e.g., '2024-11')
    
    # Establish database connection
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Query to fetch expenses for the current month
        query = """
            SELECT id, category, item, amount, quantity, date, payment_mode
            FROM expenses
            WHERE DATE_FORMAT(date, '%Y-%m') = %s
        """
        
        # Execute the query with the current month
        cursor.execute(query, (current_month,))
        records = cursor.fetchall()

        # Clear current entries in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Load data from the database
        for record in records:
            tree.insert('', 'end', values=record)

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data for this month: {e}")


def show_all():
    try:
        # Connect to the database
        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()

        # Query to fetch all expenses
        query = """
            SELECT id, category, item, amount, quantity, date, payment_mode
            FROM expenses
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Clear the current data in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # If no results found, show a message
        if not results:
            messagebox.showinfo("No Results", "No expenses found.")
            return

        # Insert the results into the treeview
        for record in results:
            tree.insert('', 'end', values=record)

        # Close the database connection
        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching all expenses: {e}")


def show_by_month():
    # Get the selected month from the input field (e.g., MM-YYYY)
    selected_month = month_var.get().strip()

    if not selected_month:
        messagebox.showerror("Input Error", "Please select a month in MM-YYYY format.")
        return

    # Validate if the entered month is in the correct MM-YYYY format
    try:
        datetime.strptime(selected_month, "%m-%Y")  # Check if the month format is valid
    except ValueError:
        messagebox.showerror("Format Error", "Invalid month format. Please use MM-YYYY format.")
        return

    # SQL query to fetch expenses where the date matches the selected month
    query = """
        SELECT id, category, item, amount, quantity, date, payment_mode
        FROM expenses
        WHERE DATE_FORMAT(date, '%m-%Y') = %s
    """

    try:
        conn = create_connection()
        if conn is None:
            return

        cursor = conn.cursor()
        cursor.execute(query, (selected_month,))
        results = cursor.fetchall()

        # Clear the current data in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # If no results found, show a message
        if not results:
            messagebox.showinfo("No Results", f"No expenses found for {selected_month}.")
            return

        # Insert the results into the treeview
        for record in results:
            tree.insert('', 'end', values=record)

        # Close the database connection
        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching data for {selected_month}: {e}")


def search_expenses():
    search_type = search_type_var.get()  # Get selected search criteria
    search_value = search_item_var.get().strip()  # Get search term from user input
    
    if not search_value:
        messagebox.showerror("Input Error", "Search value cannot be empty.")
        return
    
    # Map the search type to the corresponding column in the database
    column_map = {
        "Item": "item",
        "Category": "category",
        "Payment Mode": "payment_mode",
        "Date": "date",
        "Amount": "amount"
    }
    
    # Check if the selected search type is valid
    if search_type not in column_map:
        messagebox.showerror("Input Error", "Invalid search type.")
        return
    
    # Get the database column for the selected search type
    search_column = column_map[search_type]
    
    # SQL query based on search type
    query = f"SELECT id, category, item, amount, quantity, date, payment_mode FROM expenses WHERE {search_column} LIKE %s"
    
    # Prepare search term with wildcards for SQL LIKE query
    search_value = f"%{search_value}%"
    
    # Connect to the database and perform the search
    try:
        conn = create_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        cursor.execute(query, (search_value,))
        results = cursor.fetchall()
        
        # Clear the current data in the treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # If no results found, show a message
        if not results:
            messagebox.showinfo("No Results", "No records found matching your search.")
            return
        
        # Insert the search results into the treeview
        for record in results:
            tree.insert('', 'end', values=record)
        
        # Close the database connection
        cursor.close()
        conn.close()
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while searching: {e}")


def load_data():
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    query = "SELECT id, category, item, amount, quantity, date, payment_mode FROM expenses"
    cursor.execute(query)
    records = cursor.fetchall()

    # Clear current entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Load data from the database
    for record in records:
        tree.insert('', 'end', values=record)

    cursor.close()
    conn.close()

def exit_application():
    root.destroy()

# Main Window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("1500x800")  # Set window size to 1500x800

font_style = ('Arial', 12)

# Input Section
frame_input = tk.Frame(root, padx=20, pady=20)
frame_input.pack(fill='x')

# Row 1
tk.Label(frame_input, text="Category:", font=font_style).grid(row=0, column=0, padx=10, pady=10, sticky='w')
category_var = tk.StringVar(value=categories[0])  # Default to the first category
ttk.Combobox(frame_input, textvariable=category_var, values=categories, font=font_style, width=35, state="readonly").grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame_input, text="Item:", font=font_style).grid(row=0, column=2, padx=10, pady=10, sticky='w')
item_var = tk.StringVar()
tk.Entry(frame_input, textvariable=item_var, font=font_style, width=20).grid(row=0, column=3, padx=10, pady=10)

tk.Label(frame_input, text="Amount:", font=font_style).grid(row=0, column=4, padx=10, pady=10, sticky='w')
amount_var = tk.StringVar()
tk.Entry(frame_input, textvariable=amount_var, font=font_style, width=15).grid(row=0, column=5, padx=10, pady=10)

# Row 2
tk.Label(frame_input, text="Quantity:", font=font_style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
quantity_var = tk.StringVar(value="1")  # Default to 1
tk.Entry(frame_input, textvariable=quantity_var, font=font_style, width=15).grid(row=1, column=1, padx=10, pady=10)

tk.Label(frame_input, text="Date (DD-MM-YYYY):", font=font_style).grid(row=1, column=2, padx=10, pady=10, sticky='w')
date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))  # Default to current date
tk.Entry(frame_input, textvariable=date_var, font=font_style, width=20).grid(row=1, column=3, padx=10, pady=10)

tk.Label(frame_input, text="Payment Mode:", font=font_style).grid(row=1, column=4, padx=10, pady=10, sticky='w')
payment_mode_var = tk.StringVar(value="Offline")
ttk.Combobox(frame_input, textvariable=payment_mode_var, values=["Offline", "Online"], state="readonly", font=font_style, width=15).grid(row=1, column=5, padx=10, pady=10)

tk.Button(frame_input, text="Add Expense", command=add_expense, bg="green",cursor="hand2", fg="white", font=font_style, width=15).grid(row=1, column=6, padx=10, pady=10)

# Search Section
frame_search = tk.Frame(root, padx=20, pady=20)
frame_search.pack(fill='x')

tk.Label(frame_search, text="Search By:", font=font_style).grid(row=0, column=0, padx=10, pady=10, sticky='w')
search_type_var = tk.StringVar(value=search_types[0])
search_type_cb = ttk.Combobox(frame_search, textvariable=search_type_var, values=search_types, state="readonly", font=font_style, width=20)
search_type_cb.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame_search, text="Search Item:", font=font_style).grid(row=0, column=2, padx=10, pady=10, sticky='w')
search_item_var = tk.StringVar()
tk.Entry(frame_search, textvariable=search_item_var, font=font_style, width=30).grid(row=0, column=3, padx=10, pady=10)

tk.Button(frame_search, text="Search", command=search_expenses,cursor="hand2", bg="blue", fg="white", font=font_style, width=15).grid(row=0, column=4, padx=10, pady=10)

# Month Selection
tk.Label(frame_search, text="Select Month (MM-YYYY):", font=font_style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
month_var = tk.StringVar()
tk.Entry(frame_search, textvariable=month_var, font=font_style, width=20).grid(row=1, column=1, padx=10, pady=10)

tk.Button(frame_search, text="Show Month", command=show_by_month, bg="purple",cursor="hand2", fg="white", font=font_style, width=15).grid(row=1, column=2, padx=10, pady=10)
tk.Button(frame_search, text="Show All", command=show_all, bg="dark orange",cursor="hand2", fg="white", font=font_style, width=15).grid(row=1, column=3, padx=10, pady=10)

# Table Section
frame_table = tk.Frame(root)
frame_table.pack(fill='both', expand=True)

columns = ("ID", "Category", "Item", "Amount", "Quantity", "Date", "Payment Mode")
tree = ttk.Treeview(frame_table, columns=columns, show='headings', selectmode='browse')

# Set column headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100 if col == "ID" else 150)

tree.pack(fill='both', expand=True)

# Action Buttons Section
frame_actions = tk.Frame(root, padx=20, pady=20)
frame_actions.pack(fill='x')


# Add Analyze Expenses Button
# Action Buttons Section
frame_actions = tk.Frame(root, padx=30, pady=30)
frame_actions.pack(fill='x')

# Left-side buttons
tk.Button(frame_actions, text="Delete Expense", command=delete_expense, bg="red", fg="white", font=font_style, width=15, cursor="hand2").pack(side='left', padx=20)
tk.Button(frame_actions, text="Show This Month", command=show_this_month, bg="orange", fg="white", font=font_style, width=15, cursor="hand2").pack(side='left', padx=20)

# Buttons to the right of "Show This Month"
tk.Button(frame_actions, text="Analyze This Month", command=show_analysis_this_month, bg="purple", fg="white", font=font_style, width=15, cursor="hand2").pack(side='left', padx=10)
tk.Button(frame_actions, text="Analyze Expenses", command=show_analysis_pie, bg="blue", fg="white", font=font_style, width=15, cursor="hand2").pack(side='left', padx=10)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_application, bg="red", fg="white", font=font_style,cursor="hand2")
exit_button.place(relx=0.9, rely=0.02)

# Action Buttons
frame_actions = tk.Frame(root, padx=20, pady=20)
frame_actions.pack(fill='x')

#tk.Button(frame_actions, text="Delete Expense", command=delete_expense, bg="red", fg="white", font=font_style, width=15,cursor="hand2").pack(side='left', padx=20)
#tk.Button(frame_actions, text="Show This Month", command=show_this_month, bg="orange", fg="white", font=font_style, width=15,cursor="hand2").pack(side='left', padx=20)

# Load data on startup
load_data()

# Mainloop
root.mainloop()
