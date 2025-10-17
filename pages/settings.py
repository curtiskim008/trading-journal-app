import streamlit as st
from utils import database as db

st.title("⚙️ Settings")

# Get current balance
current_balance = db.get_equity_balance()  # <-- use the correct function
st.write(f"Current Account Balance: **${current_balance:.2f}**")

# Reset account balance
new_balance = st.number_input("Set New Account Balance", min_value=0.0, value=float(current_balance), step=0.1, key="balance_input")
if st.button("💾 Update Balance"):
    db.update_equity_balance(new_balance)
    st.success(f"Account balance updated to ${new_balance:.2f}")

# Delete all trades
st.markdown("---")
st.write("⚠️ **Delete all trades**")
if st.button("🗑️ Delete All Trades"):
    db.delete_all_trades()
    st.success("All trades have been deleted!")
