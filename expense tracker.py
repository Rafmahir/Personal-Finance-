import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import calendar

FILENAME = "expenses.csv"

# Create the CSV file if it doesn't exist
if not os.path.exists(FILENAME):
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Category', 'Amount'])

# Add a new expense
def add_expense():
    category = category_entry.get().strip()
    amount = amount_entry.get().strip()
    date = date_entry.get().strip()

    if not category or not amount:
        messagebox.showerror("Missing Info", "Category and Amount are required.")
        return

    if not date:
        date = datetime.today().strftime('%Y-%m-%d')

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Input", "Amount must be a number.")
        return

    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount])

    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

    show_all_expenses()
    messagebox.showinfo("Success", "Expense added successfully!")

# Show all expenses (filtered by month if selected)
def show_all_expenses():
    for row in tree.get_children():
        tree.delete(row)

    selected_month = month_var.get()
    month_num = list(calendar.month_name).index(selected_month) if selected_month != "All" else None

    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            try:
                if month_num:
                    date_obj = datetime.strptime(row[0], '%Y-%m-%d')
                    if date_obj.month != month_num:
                        continue
                tree.insert('', tk.END, values=row)
            except:
                continue

    update_total_label()

# Show a pie chart of expenses by category
def show_pie_chart():
    selected_month = month_var.get()
    month_num = list(calendar.month_name).index(selected_month) if selected_month != "All" else None

    categories = defaultdict(float)
    with open(FILENAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                amt = float(row['Amount'])
                cat = row['Category']
                date_obj = datetime.strptime(row['Date'], '%Y-%m-%d')
                if month_num and date_obj.month != month_num:
                    continue
                categories[cat] += amt
            except:
                continue

    if not categories:
        messagebox.showwarning("No Data", "No expenses to display for this month.")
        return

    labels = list(categories.keys())
    values = list(categories.values())

    plt.figure(figsize=(6,6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(f'Expenses by Category - {selected_month}')
    plt.axis('equal')
    plt.show()

# Update the total monthly expense label
def update_total_label():
    selected_month = month_var.get()
    month_num = list(calendar.month_name).index(selected_month) if selected_month != "All" else None
    total = 0.0
    with open(FILENAME, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                amt = float(row['Amount'])
                date_obj = datetime.strptime(row['Date'], '%Y-%m-%d')
                if month_num and date_obj.month != month_num:
                    continue
                total += amt
            except:
                continue
    total_label.config(text=f"Total: ${total:.2f}")

# -------------------- GUI Setup --------------------
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("700x550")
root.resizable(True, True)

# -------- Input Fields --------
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Category").grid(row=0, column=0, padx=5, pady=5)
category_entry = tk.Entry(input_frame)
category_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Amount").grid(row=1, column=0, padx=5, pady=5)
amount_entry = tk.Entry(input_frame)
amount_entry.grid(row=1, column=1, padx=5)

tk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=2, column=0, padx=5, pady=5)
date_entry = tk.Entry(input_frame)
date_entry.grid(row=2, column=1, padx=5)

tk.Button(input_frame, text="Add Expense", width=20, command=add_expense).grid(row=3, column=0, columnspan=2, pady=10)

# Month Selector with auto-refresh
tk.Label(input_frame, text="Select Month").grid(row=4, column=0, pady=5)
month_var = tk.StringVar(value="All")
month_options = ["All"] + [calendar.month_name[i] for i in range(1, 13)]
month_menu = tk.OptionMenu(input_frame, month_var, *month_options, command=lambda x: show_all_expenses())
month_menu.grid(row=4, column=1, pady=5)

# -------- Treeview Table --------
tree = ttk.Treeview(root, columns=("Date", "Category", "Amount"), show='headings')
tree.heading("Date", text="Date")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount")
tree.column("Date", width=150)
tree.column("Category", width=250)
tree.column("Amount", width=100)
tree.pack(pady=10, padx=10, fill="x")

# -------- Buttons --------
button_frame = tk.Frame(root)
button_frame.pack()

tk.Button(button_frame, text="Show All Expenses", command=show_all_expenses).grid(row=0, column=0, padx=10, pady=10)
tk.Button(button_frame, text="Show Pie Chart", command=show_pie_chart).grid(row=0, column=1, padx=10)

# -------- Total Label --------
total_label = tk.Label(root, text="Total: $0.00", font=("Arial", 18))
total_label.pack(pady=5)

# Load existing data at startup
show_all_expenses()

root.mainloop()
