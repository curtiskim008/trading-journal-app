import streamlit as st

# ─── Page setup ───────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Journal App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
/* Center title and add gradient text */
.title {
    text-align: center;
    font-size: 48px;
    font-weight: bold;
    background: linear-gradient(90deg, #1E90FF, #32CD32);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Cards for buttons */
.card {
    background-color: #f4f4f9;
    border-radius: 12px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.card:hover {
    transform: scale(1.05);
}

/* Button styling inside cards */
.card button {
    font-size: 18px;
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    background-color: #1E90FF;
    color: white;
    cursor: pointer;
    transition: background 0.3s;
}
.card button:hover {
    background-color: #32CD32;
}

/* About section styling */
.stExpander {
    background-color: #f9f9f9;
    border-left: 4px solid #1E90FF;
    border-radius: 8px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ─── Page Title ──────────────────────────────────────────────
st.markdown('<h1 class="title">📈 Welcome to Your Trading Journal App</h1>', unsafe_allow_html=True)
st.markdown(
    """
    <p style="text-align:center; font-size:20px; color:#555;">
    Track your trades, analyze performance, and improve your trading discipline.
    </p>
    """, unsafe_allow_html=True
)

st.markdown("---")

# ─── Navigation Cards ────────────────────────────────────────
st.subheader("Navigate to:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <button onclick="window.location.href='#'">📊 Journal</button>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <button onclick="window.location.href='#'">➕ Add Trade</button>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <button onclick="window.location.href='#'">⚙️ Settings</button>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── About Section ──────────────────────────────────────────
with st.expander("ℹ️ About This App", expanded=True):
    st.markdown("""
    <ul style="font-size:16px; color:#333;">
        <li>📝 Add new trades with entry/exit, risk, R-multiple, outcome, and notes.</li>
        <li>📊 View your trading journal with filters and %PnL metrics.</li>
        <li>📈 Track your total trades, wins, losses, break-even trades, and win rate.</li>
        <li>💾 Download your trades as CSV for backup or analysis.</li>
        <li>🎨 Color-coded metrics for quick analysis of trades and outcomes.</li>
    </ul>
    <p style="font-size:16px; color:#555;">
    Use the buttons above or the sidebar to navigate between pages.
    </p>
    """, unsafe_allow_html=True)
