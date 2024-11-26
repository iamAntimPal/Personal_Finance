import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sample in-memory list to store budget
budgets = []

# Predefined categories for the budget
categories = [
    "Rent/Mortgage",
    "Utilities (Electricity, Water, Gas, Internet, Phone)",
    "Groceries",
    "Transportation",
    "Dining Out",
    "Entertainment",
    "Healthcare",
    "Education",
    "Savings",
    "Others"
]

search_types = ["Category", "Amount", "Date"]

# Functions
def set_budget():
    category = category_var.get()
    budget_amount = budget_amount_var.get()
    date_set = date_var.get()

    if not budget_amount.isdigit():
        messagebox.showerror("Input Error", "Budget amount must be a positive number.")
        return

    if category and budget_amount and date_set:
        try:
            budget = {
                'category': category,
                'amount': float(budget_amount),
                'date': date_set
            }
            budgets.append(budget)
            load_data(budgets)  # Refresh treeview
            reset_fields()
            show_charts()  # Update the charts
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set budget: {e}")
    else:
        messagebox.showerror("Input Error", "All fields are required.")

def delete_budget():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "No item selected to delete.")
        return

    try:
        item = tree.item(selected_item)
        record_id = int(item['values'][0])  # Use ID to find budget in the list
        budgets.pop(record_id)
        load_data(budgets)  # Refresh treeview
        show_charts()  # Update the charts after deletion
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete budget: {e}")

def reset_fields():
    category_var.set(categories[0])
    budget_amount_var.set('')
    date_var.set(datetime.now().strftime("%d-%m-%Y"))  # Default to current date

def show_all():
    load_data(budgets)
    show_charts()  # Update charts for all data

def search_budgets():
    search_type = search_type_var.get()
    search_value = search_item_var.get().strip()

    if not search_value:
        messagebox.showerror("Input Error", "Search value cannot be empty.")
        return

    filtered_budgets = [
        budget for budget in budgets
        if search_value.lower() in str(budget[search_type.lower()]).lower()
    ]
    load_data(filtered_budgets)
    show_charts()  # Update charts for search results

def load_data(data):
    # Clear current entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Load data from the provided list
    for index, budget in enumerate(data):
        tree.insert('', 'end', values=(index, budget['category'], budget['amount'], budget['date']))

def show_charts():
    # Prepare data for pie chart
    categories_data = {}
    for budget in budgets:
        categories_data[budget['category']] = categories_data.get(budget['category'], 0) + budget['amount']

    # Pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(categories_data.values(), labels=categories_data.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Embed pie chart in tkinter window
    for widget in frame_charts.winfo_children():
        widget.destroy()  # Clear previous chart if any
    canvas = FigureCanvasTkAgg(fig, master=frame_charts)  # Create a canvas to embed the plot
    canvas.get_tk_widget().pack(fill='both', expand=True)
    canvas.draw()

def exit_application():
    root.destroy()

# Main Window
root = tk.Tk()
root.title("Budget Tracker")
root.geometry("1500x800")  # Set window size to 1500x800

font_style = ('Arial', 12)

# Input Section
frame_input = tk.Frame(root, padx=20, pady=20)
frame_input.pack(fill='x')

# Row 1
tk.Label(frame_input, text="Category:", font=font_style).grid(row=0, column=0, padx=10, pady=10, sticky='w')
category_var = tk.StringVar(value=categories[0])  # Default to the first category
ttk.Combobox(frame_input, textvariable=category_var, values=categories, font=font_style, width=35, state="readonly").grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame_input, text="Budget Amount:", font=font_style).grid(row=0, column=2, padx=10, pady=10, sticky='w')
budget_amount_var = tk.StringVar()
tk.Entry(frame_input, textvariable=budget_amount_var, font=font_style, width=15).grid(row=0, column=3, padx=10, pady=10)

# Row 2
tk.Label(frame_input, text="Date (DD-MM-YYYY):", font=font_style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))  # Default to current date
tk.Entry(frame_input, textvariable=date_var, font=font_style, width=20).grid(row=1, column=1, padx=10, pady=10)

tk.Button(frame_input, text="Set Budget", command=set_budget, bg="green", fg="white", font=font_style, width=15).grid(row=1, column=2, padx=10, pady=10)

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

tk.Button(frame_search, text="Search", command=search_budgets, bg="blue", fg="white", font=font_style, width=15).grid(row=0, column=4, padx=10, pady=10)

# Month Selection
tk.Label(frame_search, text="Select Month (MM-YYYY):", font=font_style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
month_var = tk.StringVar()
tk.Entry(frame_search, textvariable=month_var, font=font_style, width=20).grid(row=1, column=1, padx=10, pady=10)

tk.Button(frame_search, text="Show All", command=show_all, bg="dark orange", fg="white", font=font_style, width=15).grid(row=1, column=2, padx=10, pady=10)

# Table Section
frame_table = tk.Frame(root)
frame_table.pack(fill='both', expand=True)

columns = ("ID", "Category", "Budget Amount", "Date")
tree = ttk.Treeview(frame_table, columns=columns, show='headings', selectmode='browse')

# Set column headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100 if col == "ID" else 150)

tree.pack(fill='both', expand=True)

# Action Buttons (Delete Budget)
frame_actions = tk.Frame(root, padx=20, pady=20)
frame_actions.pack(fill='x')

tk.Button(frame_actions, text="Delete Budget", command=delete_budget, bg="red", fg="white", font=font_style, width=15).pack(side='left', padx=20)

# Chart Section
frame_charts = tk.Frame(root, padx=20, pady=20)
frame_charts.pack(side="bottom", fill='both', expand=True)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_application, bg="red", fg="white", font=font_style)
exit_button.place(relx=0.9, rely=0.02)

# Load data on startup
load_data(budgets)

# Mainloop
root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sample in-memory list to store budgets
budgets = []

# Predefined categories
categories = [
    "Fixed Expenses",
    "Rent/Mortgage Payments",
    "Utilities (Electricity, Water, Gas, Internet, Phone)",
    "Insurance Premiums (Health, Auto, Life, Home)",
    "Subscription Services (Streaming platforms, Gym memberships, Magazines)",
    "Variable Expenses",
    "Groceries",
    "Transportation (Fuel, Public Transport, Ride-sharing)",
    "Dining Out",
    "Entertainment (Movies, Concerts, Hobbies)",
    "Clothing and Accessories",
    "Healthcare (Doctor visits, Medicines, Therapies)",
    "Education (Books, Tuition Fees, Courses)",
    "Gifts and Celebrations (Birthdays, Weddings)",
    "Irregular/One-time Expenses",
    "Vacations/Travel",
    "Home Repairs and Maintenance",
    "Large Purchases (Appliances, Furniture, Electronics)",
    "Emergencies (Medical, Vehicle Repairs)",
]

search_types = ["Category", "Amount", "Date"]

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
            budget = {
                'category': category,
                'amount': float(amount),
                'date': expense_date
            }
            budgets.append(budget)
            load_data(budgets)  # Refresh treeview
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
        record_id = int(item['values'][0])  # Use ID to find budget in the list
        budgets.pop(record_id)
        load_data(budgets)  # Refresh treeview
        update_charts()  # Update charts after deleting a budget
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete budget: {e}")

def reset_fields():
    category_var.set(categories[0])
    amount_var.set('')
    date_var.set(datetime.now().strftime("%d-%m-%Y"))  # Default to current date

def show_all():
    load_data(budgets)
    update_charts()  # Update charts when showing all

def search_budgets():
    search_type = search_type_var.get()
    search_value = search_item_var.get().strip()

    if not search_value:
        messagebox.showerror("Input Error", "Search value cannot be empty.")
        return

    filtered_budgets = [
        budget for budget in budgets
        if search_value.lower() in str(budget[search_type.lower()]).lower()
    ]
    load_data(filtered_budgets)
    update_charts()  # Update charts based on search

def load_data(data):
    # Clear current entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Load data from the provided list
    for index, budget in enumerate(data):
        tree.insert('', 'end', values=(index, budget['category'], budget['amount'], budget['date']))

def update_charts():
    # Update the Pie Chart
    categories_data = {}
    for budget in budgets:
        category = budget['category']
        amount = budget['amount']
        if category not in categories_data:
            categories_data[category] = 0
        categories_data[category] += amount

    # Pie Chart
    pie_labels = list(categories_data.keys())
    pie_values = list(categories_data.values())

    ax_pie.clear()
    ax_pie.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', startangle=90)
    ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    canvas_pie.draw()

    # Stacked Bar Chart
    monthly_data = {}
    for budget in budgets:
        month = budget['date'][:7]  # Get YYYY-MM (just month-year)
        category = budget['category']
        amount = budget['amount']
        if month not in monthly_data:
            monthly_data[month] = {}
        if category not in monthly_data[month]:
            monthly_data[month][category] = 0
        monthly_data[month][category] += amount

    months = sorted(monthly_data.keys())
    stacked_data = {category: [] for category in categories}
    for month in months:
        for category in categories:
            stacked_data[category].append(monthly_data[month].get(category, 0))

    ax_bar.clear()
    for i, category in enumerate(categories):
        ax_bar.bar(months, stacked_data[category], label=category, bottom=sum([stacked_data[c][i] for c in categories[:i]]))
    
    ax_bar.set_xlabel("Month")
    ax_bar.set_ylabel("Amount")
    ax_bar.set_title("Budget Allocation Over Time")
    ax_bar.legend(loc="upper left", bbox_to_anchor=(1, 1))
    canvas_bar.draw()

def exit_application():
    root.destroy()

# Main Window
root = tk.Tk()
root.title("Budget Tracker")
root.geometry("1500x800")  # Set window size to 1500x800

font_style = ('Arial', 12)

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
tk.Label(frame_input, text="Date (DD-MM-YYYY):", font=font_style).grid(row=1, column=0, padx=10, pady=10, sticky='w')
date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))  # Default to current date
tk.Entry(frame_input, textvariable=date_var, font=font_style, width=20).grid(row=1, column=1, padx=10, pady=10)

tk.Button(frame_input, text="Add Budget", command=add_budget, bg="green", fg="white", font=font_style, width=15).grid(row=1, column=2, padx=10, pady=10)

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

tk.Button(frame_search, text="Search", command=search_budgets, bg="blue", fg="white", font=font_style, width=15).grid(row=0, column=4, padx=10, pady=10)

# Table Section
frame_table = tk.Frame(root)
frame_table.pack(fill='both', expand=True)

columns = ("ID", "Category", "Amount", "Date")
tree = ttk.Treeview(frame_table, columns=columns, show='headings', selectmode='browse')

# Set column headings
for col in columns:
    tree.heading(col, text=col)

tree.pack(fill='both', expand=True, padx=20, pady=20)

# Button Section
frame_buttons = tk.Frame(root, padx=20, pady=20)
frame_buttons.pack(fill='x')

tk.Button(frame_buttons, text="Show All", command=show_all, font=font_style, width=15).grid(row=0, column=0, padx=10, pady=10)
tk.Button(frame_buttons, text="Delete Budget", command=delete_budget, font=font_style, width=15).grid(row=0, column=1, padx=10, pady=10)

tk.Button(frame_buttons, text="Exit", command=exit_application, bg="red", fg="white", font=font_style, width=15).grid(row=0, column=2, padx=10, pady=10)

# Charts Section
frame_charts = tk.Frame(root)
frame_charts.pack(fill='both', expand=True, padx=20, pady=20)

fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(15, 7))

# Pie Chart (Right-bottom)
canvas_pie = FigureCanvasTkAgg(fig, master=frame_charts)
canvas_pie.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Stacked Bar Chart
canvas_bar = FigureCanvasTkAgg(fig, master=frame_charts)
canvas_bar.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()
