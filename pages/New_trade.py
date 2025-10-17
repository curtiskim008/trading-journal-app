import streamlit as st
from datetime import datetime
from utils import database as db
from utils import files
from pathlib import Path

st.title("➕ Add New Trade")

# Initialize DB
db.init_db()

# Directories
data_dir = Path("data")
screenshot_dir = data_dir / "screenshots"
screenshot_dir.mkdir(parents=True, exist_ok=True)

# --- Trade Entry Form ---
with st.form("add_trade_form"):
    st.subheader("📝 New Trade Entry")

    trade_date = st.date_input("Date", value=datetime.now().date())
    pair = st.selectbox("Pair", ["EU", "GU", "XAU", "NAS100"])
    session = st.selectbox("Session", ["London", "New York", "Asia"])
    direction = st.selectbox("Direction", ["Buy", "Sell"])
    entry_time = st.text_input("Entry Time (HH:MM)")
    exit_time = st.text_input("Exit Time (HH:MM)")

    # Editable with constraints
    risk_pct = st.number_input(
        "Risk per Trade (%)",
        min_value=0.0,
        max_value=1.0,  # maximum allowed is 1%
        step=0.1,
        value=1.0
    )
    r_mult = st.number_input(
        "R Multiple (_r)",
        min_value=2.0,  # minimum allowed is 2
        max_value=20.0,
        step=0.1,
        value=2.0
    )

    outcome = st.selectbox("Outcome", ["Win", "Loss", "Breakeven"])
    mistakes = st.text_area("Mistakes")
    comments = st.text_area("Comments")
    screenshot = st.file_uploader("Upload Screenshot (optional)", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("💾 Save Trade")

    if submitted:
        trade = {
            "trade_date": trade_date.isoformat(),
            "pair": pair,
            "session": session,
            "direction": direction,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "risk_pct": risk_pct,
            "_r": r_mult,
            "outcome": outcome,
            "mistakes": mistakes,
            "comments": comments,
            "screenshot_path": None,
            "created_at": datetime.now().isoformat()
        }

        # Save screenshot if uploaded
        if screenshot:
            screenshot_path = files.save_uploaded_file(screenshot, screenshot_dir)
            trade["screenshot_path"] = screenshot_path

        db.insert_trade(trade)
        st.success("✅ Trade added successfully!")
        st.balloons()
