import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import calendar

FILENAME = "expenses.csv"

if not os.path.exists(FILENAME):
    df_init = pd.DataFrame(columns=["Date", "Description", "Category", "Amount", "Currency"])
    df_init.to_csv(FILENAME, index=False)

# -----Auto Categorization --------
def predict_category(description):
    desc = description.lower()
    if "grocery" in desc or "supermarket" in desc:
        return "Groceries"
    elif "uber" in desc or "taxi" in desc:
        return "Transport"
    elif "rent" in desc:
        return "Rent"
    elif "restaurant" in desc or "food" in desc:
        return "Dining"
    elif "gas" in desc or "fuel" in desc:
        return "Car"
    else:
        return "Other"

# -------------Add Expense --------------
def add_expense(description, category, amount, currency, date):
    if not category:
        category = predict_category(description)
    new_row = {
        "Date": date,
        "Description": description,
        "Category": category,
        "Amount": amount,
        "Currency": currency,
    }
    df = pd.read_csv(FILENAME)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FILENAME, index=False)
    st.success("Expense added successfully!")

# ---Show Expenses -----------
def filter_expenses(month):
    df = pd.read_csv(FILENAME)
    if month != "All":
        month_num = list(calendar.month_name).index(month)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df[df["Date"].dt.month == month_num]
    return df

# -------Pie Chart ----------------
def plot_pie_chart(df, month):
    if df.empty:
        st.warning("No expenses to display for this month.")
        return
    categories = df.groupby("Category")["Amount"].sum()
    fig, ax = plt.subplots()
    ax.pie(categories, labels=categories.index, autopct='%1.1f%%', startangle=90)
    ax.set_title(f"Expenses by Category - {month}")
    st.pyplot(fig)

# --------Streamlit UI ----------
st.title("Smart Personal Finance Tracker")

st.sidebar.header("Add New Expense")

description = st.sidebar.text_input("Description")
category = st.sidebar.text_input("Category (optional)")
amount = st.sidebar.text_input("Amount")
currency = st.sidebar.text_input("Currency (default USD)", value="USD")
date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Add Expense"):
    if not description or not amount:
        st.sidebar.error("Description and Amount are required.")
    else:
        try:
            amt = float(amount)
            add_expense(description, category, amt, currency, date.strftime("%Y-%m-%d"))
        except ValueError:
            st.sidebar.error("Amount must be a valid number.")

month_options = ["All"] + [calendar.month_name[i] for i in range(1, 13)]
selected_month = st.selectbox("Select Month", month_options)

df_filtered = filter_expenses(selected_month)
st.subheader(f"Expenses ({selected_month})")
st.dataframe(df_filtered[["Date", "Description", "Category", "Amount", "Currency"]])

total = df_filtered["Amount"].sum()
st.metric("Total Expenses", f"{total:.2f} (mixed currencies)")

if st.button("Show Pie Chart"):
    plot_pie_chart(df_filtered, selected_month)
