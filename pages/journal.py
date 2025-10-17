import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from utils import database as db

# ─── Page setup ────────────────────────────────────────────────
st.set_page_config(page_title="Trading Journal", layout="wide")
st.title("📊 Trading Journal")

# ─── Load data ────────────────────────────────────────────────
db.init_db()
trades_list = db.get_trades()
df = pd.DataFrame(trades_list)

if df.empty:
    st.info("No trades recorded yet. Add a trade from the 'Add New Trade' page.")
    st.stop()

# ─── Ensure numeric columns and calculate PnL percentage ───────
df["_r"] = pd.to_numeric(df["_r"], errors="coerce").fillna(0.0)
df["risk_pct"] = pd.to_numeric(df["risk_pct"], errors="coerce").fillna(0.0)
df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0.0)

# Calculate initial equity (original capital before trades)
initial_equity = db.get_equity_balance() - df["pnl"].sum()

# Convert each trade's pnl to % of initial equity
df["pnl"] = (df["pnl"] / initial_equity * 100).round(2)

# Sort oldest to newest
df = df.sort_values(by="id", ascending=True).reset_index(drop=True)
df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")

# Remove created_at column if exists
if "created_at" in df.columns:
    df = df.drop(columns=["created_at"])

# Convert all except mistakes/comments/pnl to uppercase
for col in df.columns:
    if col not in ["mistakes", "comments", "screenshot_path", "pnl"]:
        df[col] = df[col].apply(lambda x: str(x).upper() if pd.notna(x) else "")

# ─── Summary Metrics with CSS Cards ─────────────────────────────
total_trades = len(df)
wins = len(df[df["outcome"].str.lower() == "win"])
losses = len(df[df["outcome"].str.lower() == "loss"])
breakeven = len(df[df["outcome"].str.lower() == "breakeven"])
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
total_pnl_perc = df["pnl"].sum().round(2)

st.markdown("""
<style>
.card {padding: 15px; border-radius: 12px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s; font-family:'Segoe UI', sans-serif; margin-bottom:15px;}
.card:hover {transform: translateY(-3px);}
.card-title {font-size:12px; font-weight:600; margin-bottom:5px;}
.card-value {font-size:20px; font-weight:bold;}
.card-trades {background: linear-gradient(135deg,#43A047,#66BB6A); color:white;}
.card-win {background: linear-gradient(135deg,#66BB6A,#81C784); color:white;}
.card-loss {background: linear-gradient(135deg,#E53935,#EF5350); color:white;}
.card-be {background: linear-gradient(135deg,#FDD835,#FFEE58); color:#333;}
.card-winrate {background: linear-gradient(135deg,#8E24AA,#BA68C8); color:white;}
.card-pnl {background: linear-gradient(135deg,#26A69A,#4DB6AC); color:white;}
.column-padding {padding-right:15px; padding-left:15px;}
</style>
""", unsafe_allow_html=True)

with st.expander("📊 Summary Metrics", expanded=True):
    cols = st.columns(6)
    metrics = [
        ("Total Trades", total_trades, "card-trades"),
        ("Wins", wins, "card-win"),
        ("Break Even", breakeven, "card-be"),
        ("Losses", losses, "card-loss"),
        ("Win Rate", f"{win_rate:.2f}%", "card-winrate"),
        ("%PnL", f"{total_pnl_perc:.2f}%", "card-pnl")
    ]
    for i, (title, value, css) in enumerate(metrics):
        with cols[i % 6]:
            st.markdown(f"""
                <div class="card {css}">
                    <div class="card-title">{title}</div>
                    <div class="card-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ─── Filters ───────────────────────────────────────────────
with st.expander("🔍 FILTER TRADES", expanded=False):
    c1, c2, c3, c4, c5 = st.columns(5)
    pairs = ["ALL"] + sorted(df["pair"].unique().tolist())
    sessions = ["ALL"] + sorted(df["session"].unique().tolist())
    outcomes = ["ALL"] + sorted(df["outcome"].unique().tolist())
    directions = ["ALL"] + sorted(df["direction"].unique().tolist())

    pair_filter = c1.selectbox("PAIR", pairs)
    session_filter = c2.selectbox("SESSION", sessions)
    outcome_filter = c3.selectbox("OUTCOME", outcomes)
    direction_filter = c4.selectbox("DIRECTION", directions)
    date_range = c5.date_input("DATE RANGE", [])

filtered_df = df.copy()
if pair_filter != "ALL":
    filtered_df = filtered_df[filtered_df["pair"] == pair_filter]
if session_filter != "ALL":
    filtered_df = filtered_df[filtered_df["session"] == session_filter]
if outcome_filter != "ALL":
    filtered_df = filtered_df[filtered_df["outcome"] == outcome_filter]
if direction_filter != "ALL":
    filtered_df = filtered_df[filtered_df["direction"] == direction_filter]
if len(date_range) == 2:
    start, end = date_range
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df["trade_date"]) >= pd.to_datetime(start))
        & (pd.to_datetime(filtered_df["trade_date"]) <= pd.to_datetime(end))
    ]

st.caption(f"SHOWING **{len(filtered_df)}** OF **{len(df)}** TRADES")

# ─── Styling & Grid ─────────────────────────────────────────────
cell_style_jscode = JsCode("""
function(params) {
    let col = params.colDef.field;
    let val = (params.value || '').toString().toLowerCase();
    let style = { fontWeight:'bold', padding:'8px', borderRight:'1px solid #ddd',
                  whiteSpace:'normal', lineHeight:'1.4' };
    if (col !== 'mistakes' && col !== 'comments' && col !== 'screenshot_path' && col !== 'pnl')
        style.textTransform='uppercase';

    if (col==='pair'){ if(val.includes('eu')) style.color='#1E90FF';
        else if(val.includes('gu')) style.color='#32CD32';
        else if(val.includes('xau')) style.color='#FFD700';
        else if(val.includes('nas100')) style.color='#FF69B4';
        else style.color='#616161'; }
    if (col==='session'){ if(val.includes('london')) style.color='#6A5ACD';
        else if(val.includes('new york')) style.color='#FF8C00';
        else if(val.includes('asia')) style.color='#20B2AA';
        else style.color='#616161'; }
    if (col==='outcome'){ if(val.includes('win')) style.color='#1B5E20';
        else if(val.includes('loss')) style.color='#B71C1C';
        else if(val.includes('break')) style.color='#616161'; }
    if (col==='direction'){ if(val.includes('buy')) style.color='#2E8B57';
        else if(val.includes('sell')) style.color='#C62828';
        else style.color='#616161'; }
    if (col==='pnl'){ let p=parseFloat(val);
        if(p>0) style.color='#1B5E20';
        else if(p<0) style.color='#B71C1C';
        else style.color='#616161'; }
    if (col==='risk_pct'){ let r=parseFloat(val);
        if(r<1) style.color='#2E8B57';
        else if(r>=1 && r<=2) style.color='#FFA500';
        else style.color='#C62828'; }
    if (col==='_r'){ let r=parseFloat(val);
        if(r<0) style.color='#B71C1C';
        else if(r===0) style.color='#616161';
        else style.color='#1B5E20'; }
    return style;
}
""")

row_style_jscode = JsCode("""
function(params) {
    let outcome = (params.data.outcome || '').toLowerCase();
    let base = { borderBottom:'1px solid #ccc' };
    if(outcome.includes('win')) base.backgroundColor='#E8F8EC';
    else if(outcome.includes('loss')) base.backgroundColor='#FCE8E6';
    else if(outcome.includes('break')) base.backgroundColor='#FFF9E6';
    return base;
}
""")

st.markdown("""
<style>
.ag-header-cell-label { font-weight:bold !important; text-transform:uppercase;
    background-color:#f4f4f4 !important; border-bottom:2px solid #888 !important;
    border-right:1px solid #ddd !important; padding:8px; }
.ag-cell { white-space:normal !important; line-height:1.4 !important; }
</style>
""", unsafe_allow_html=True)

gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_default_column(
    resizable=True, sortable=True, filter=True, wrapText=True, autoHeight=True,
    cellStyle=cell_style_jscode
)
gb.configure_grid_options(rowHeight=50, getRowStyle=row_style_jscode, suppressHorizontalScroll=False)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
gridOptions = gb.build()

st.markdown("### 💼 Journal Entries")
AgGrid(
    filtered_df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.NO_UPDATE,
    theme="balham",
    height=750,
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True,
)

# ─── Download CSV ─────────────────────────────────────────────
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 DOWNLOAD CSV",
    data=csv,
    file_name=f"filtered_trades_{datetime.now().date()}.csv",
    mime="text/csv",
)
