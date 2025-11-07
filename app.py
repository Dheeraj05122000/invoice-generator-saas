import streamlit as st
import pandas as pd
from fpdf import FPDF
import uuid

# --- Simple Login System ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Invoice Generator")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()  # stop here until logged in

# --- Logout Sidebar ---
with st.sidebar:
    st.title("Account")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- Page Config ---
st.set_page_config(page_title="Invoice Generator SaaS", page_icon="💼", layout="centered")

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("💼 Invoice Generator SaaS")
st.write("Create professional invoices with auto GST calculation and PDF download!")

# --- Currency Selection ---
currency = st.selectbox("Select Currency", ["INR (₹)", "USD ($)"])
symbol = "₹" if "INR" in currency else "$"

# --- Client Details ---
st.subheader("🧾 Client Details")
client_name = st.text_input("Client Name")
client_email = st.text_input("Client Email")

# --- Add Invoice Items ---
st.subheader("📦 Add Invoice Items")
num_items = st.number_input("Number of Items", min_value=1, max_value=10, value=1)

data = []
for i in range(num_items):
    col1, col2, col3 = st.columns(3)
    with col1:
        desc = st.text_input(f"Description {i+1}", key=f"desc_{i}")
    with col2:
        qty = st.number_input(f"Qty {i+1}", min_value=1, value=1, key=f"qty_{i}")
    with col3:
        price = st.number_input(f"Price {i+1}", min_value=0.0, value=0.0, key=f"price_{i}")
    data.append({"Description": desc, "Quantity": qty, "Price": price})

df = pd.DataFrame(data)
df["Total"] = df["Quantity"] * df["Price"]

# --- Calculations ---
subtotal = df["Total"].sum()
gst = subtotal * 0.18
grand_total = subtotal + gst

st.write("### 🧮 Invoice Summary")
st.write(f"**Subtotal:** {symbol}{subtotal:,.2f}")
st.write(f"**GST (18%)**: {symbol}{gst:,.2f}")
st.write(f"**Grand Total:** {symbol}{grand_total:,.2f}")

# --- Generate PDF ---
if st.button("Generate PDF Invoice"):
    pdf = FPDF()
    pdf.add_page()

    # Use Unicode font (for ₹)
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

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
        pdf.cell(60, 10, row["Description"], 1)
        pdf.cell(30, 10, str(row["Quantity"]), 1)
        pdf.cell(40, 10, f"{symbol}{row['Price']:.2f}", 1)
        pdf.cell(40, 10, f"{symbol}{row['Total']:.2f}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.cell(200, 10, f"Subtotal: {symbol}{subtotal:,.2f}", ln=True)
    pdf.cell(200, 10, f"GST (18%): {symbol}{gst:,.2f}", ln=True)
    pdf.cell(200, 10, f"Grand Total: {symbol}{grand_total:,.2f}", ln=True)

    pdf.output("invoice.pdf")

    with open("invoice.pdf", "rb") as file:
        st.download_button(
            label="📄 Download Invoice",
            data=file,
            file_name=f"Invoice_{client_name}.pdf",
            mime="application/pdf"
        )

st.success("✅ All set! Generate and download your invoice easily.")
