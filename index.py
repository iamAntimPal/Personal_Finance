import tkinter as tk
import subprocess


def open_income_gui():
    subprocess.Popen(["python", "income.py"])

def open_expense_gui():
    subprocess.Popen(["python", "Expence.py"])

def open_budget_gui():
    subprocess.Popen(["python", "Budget.py"])

# Main Home Window
root = tk.Tk()
root.title("Home Window")
root.geometry("1650x900")

# Title
tk.Label(root, text="Financial Management System", font=("Arial", 18, "bold")).pack(pady=20)

# Buttons
tk.Button(root, text="Income Management", command=open_income_gui, font=("Arial", 14), bg="green", fg="white", width=20).pack(pady=10)
tk.Button(root, text="Expense Management", command=open_expense_gui, font=("Arial", 14), bg="blue", fg="white", width=20).pack(pady=10)
tk.Button(root, text="Budget Planning", command=open_budget_gui, font=("Arial", 14), bg="orange", fg="white", width=20).pack(pady=10)

# Mainloop
root.mainloop()
