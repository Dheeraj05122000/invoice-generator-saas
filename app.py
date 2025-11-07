import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import os
import csv
import uuid

# ----------------------------------------
# 💡 App Configuration
# ----------------------------------------
st.set_page_config(page_title="Invoice Generator SaaS", page_icon="🧾", layout="centered")

# ----------------------------------------
# 🔐 Simple Login System
# ----------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Invoice Generator")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("✅ Login successful! Click Continue below.")
        else:
            st.error("❌ Invalid username or password")

    if st.session_state.logged_in:
        if st.button("Continue to App"):
            pass

    st.stop()  # Stop rest of app if not logged in

    # ----------------------------------------
# 🚪 Logout Button
# ----------------------------------------
st.sidebar.title("Account")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()


# ----------------------------------------
# 🎨 Styling (CSS)
# ----------------------------------------
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    h1 {
        color: #2E8B57;
        text-align: center;
    }
    .stButton>button {
        background-color: #2E8B57;
        color: white;
        border-radius: 8px;
        height: 40px;
        width: 200px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# 💲 Currency Selector
# ----------------------------------------
currency = st.selectbox("Select Currency", ["USD ($)", "INR (₹)"])
symbol = "$" if "USD" in currency else "₹"

# ----------------------------------------
# 🧾 App Title
# ----------------------------------------
st.title("🧾 Invoice Generator SaaS")
st.write("Create invoices instantly with GST and download them as PDFs.")

# ----------------------------------------
# 👤 Client Details
# ----------------------------------------
st.header("Client Details")
client_name = st.text_input("Client Name")
client_email = st.text_input("Client Email")

# ----------------------------------------
# 📦 Invoice Items
# ----------------------------------------
st.header("Invoice Items")
num_items = st.number_input("Number of items", min_value=1, max_value=10, step=1)
items = []

for i in range(int(num_items)):
    st.subheader(f"Item {i+1}")
    desc = st.text_input(f"Description {i+1}")
    qty = st.number_input(f"Quantity {i+1}", min_value=0.0, key=f"qty_{i}")
    price = st.number_input(f"Price {i+1}", min_value=0.0, key=f"price_{i}")
    items.append({"Description": desc, "Quantity": qty, "Price": price})

# ----------------------------------------
# 🧮 Calculate Totals
# ----------------------------------------
df = pd.DataFrame(items)
if not df.empty:
    df["Total"] = df["Quantity"] * df["Price"]
    subtotal = df["Total"].sum()
    gst = subtotal * 0.18
    grand_total = subtotal + gst

    st.subheader("Invoice Summary")
    st.dataframe(df)
    st.write(f"**Subtotal:** {symbol}{subtotal:.2f}")
    st.write(f"**GST (18%):** {symbol}{gst:.2f}")
    st.write(f"**Grand Total:** {symbol}{grand_total:.2f}")

    # ----------------------------------------
    # 📄 Generate PDF Invoice
    # ----------------------------------------
    if st.button("Generate PDF Invoice"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="INVOICE", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Client: {client_name}", ln=True)
        pdf.cell(200, 10, txt=f"Email: {client_email}", ln=True)
        pdf.ln(10)

        pdf.cell(60, 10, "Description", 1)
        pdf.cell(30, 10, "Qty", 1)
        pdf.cell(40, 10, "Price", 1)
        pdf.cell(40, 10, "Total", 1)
        pdf.ln()

        for _, row in df.iterrows():
            pdf.cell(60, 10, row["Description"][:25], 1)
            pdf.cell(30, 10, str(row["Quantity"]), 1)
            pdf.cell(40, 10, f"{symbol}{row['Price']:.2f}", 1)
            pdf.cell(40, 10, f"{symbol}{row['Total']:.2f}", 1)
            pdf.ln()

        pdf.ln(5)
        pdf.cell(200, 10, f"Subtotal: {symbol}{subtotal:.2f}", ln=True)
        pdf.cell(200, 10, f"GST (18%): {symbol}{gst:.2f}", ln=True)
        pdf.cell(200, 10, f"Grand Total: {symbol}{grand_total:.2f}", ln=True)

        pdf.output("invoice.pdf")

        with open("invoice.pdf", "rb") as f:
            st.download_button("⬇️ Download Invoice", f, file_name="invoice.pdf", mime="application/pdf")

        # ----------------------------------------
        # 💾 Save Invoice Data to CSV
        # ----------------------------------------
        invoice_data = {
            "Client Name": client_name,
            "Client Email": client_email,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Subtotal": subtotal,
            "GST": gst,
            "Grand Total": grand_total
        }

        file_path = "invoices.csv"
        file_exists = os.path.isfile(file_path)

        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=invoice_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(invoice_data)

        st.success("💾 Invoice saved successfully to history!")

    # ----------------------------------------
    # 📜 View Invoice History
    # ----------------------------------------
    if st.button("📜 View Invoice History"):
        if os.path.exists("invoices.csv"):
            history_df = pd.read_csv("invoices.csv")
            st.dataframe(history_df)
        else:
            st.warning("No invoices saved yet.")
else:
    st.warning("Please add at least one item to generate invoice.")
