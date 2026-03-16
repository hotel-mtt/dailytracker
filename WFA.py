import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import plotly.graph_objects as go
import re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Task Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

/* ── PALETTE ─────────────────────────────────────────────
   Sky Blue sidebar  #0d8de0
   Light blue bg     #f0f8ff  →  surface: #ffffff
   Blue accent       #1b9cf4  /  #0d7fd6
   Orange accent     #f59e0b  /  #d97706
   Blue frost        #e6f4ff  /  #90d0ff
   Text              #0a2540  /  muted: #4d7fa3
   ─────────────────────────────────────────────────────── */
:root {
    --bg:          #f0f8ff;
    --surface:     #ffffff;
    --sidebar-bg:  #0d8de0;
    --border:      #cce5ff;
    --border-dk:   #1a6fb5;
    --blue:        #1b9cf4;
    --blue-dk:     #0d7fd6;
    --blue-lt:     #e6f4ff;
    --blue-mid:    #90d0ff;
    --orange:      #f59e0b;
    --orange-dk:   #d97706;
    --orange-lt:   #fff8e6;
    --orange-mid:  #fcd38a;
    --ok:          #1b9cf4;
    --ok-lt:       #e6f4ff;
    --warn:        #f59e0b;
    --warn-lt:     #fff8e6;
    --danger:      #e74c3c;
    --danger-lt:   #fdedec;
    --text:        #0a2540;
    --muted:       #4d7fa3;
    --faint:       #8ab8d4;
    --radius:      12px;
}

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-dk) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.2rem !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: rgba(255,255,255,.7) !important; }

/* brand */
.app-brand {
    display: flex; align-items: center; gap: 11px;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: var(--radius); padding: 13px 15px; margin-bottom: 18px;
}
.app-brand-icon {
    width: 38px; height: 38px;
    background: var(--orange);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 19px; flex-shrink: 0;
}
.app-brand-name { font-size: 13px; font-weight: 700; color: #ffffff !important; line-height: 1.2; }
.app-brand-sub  { font-size: 11px; color: rgba(255,255,255,.65) !important; }

.sb-section {
    font-size: 9px; font-weight: 700; letter-spacing: 1.3px;
    text-transform: uppercase; color: rgba(255,255,255,.45) !important;
    padding: 0 4px 5px; margin-top: 6px;
}

/* sidebar mini cards */
.mini-card {
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 10px; padding: 11px 13px; margin-bottom: 7px;
}
.mini-card .mc-lbl {
    font-size: 9px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .7px; color: rgba(255,255,255,.6) !important; margin-bottom: 3px;
}
.mini-card .mc-val { font-size: 22px; font-weight: 700; color: #ffffff !important; }
.mini-card .mc-sub { font-size: 10px; color: rgba(255,255,255,.4) !important; margin-top: 1px; }
.mini-card.ok    { background: rgba(245,158,11,.2); border-color: rgba(252,211,138,.5); }
.mini-card.ok    .mc-val { color: var(--orange-mid) !important; }
.mini-card.danger{ background: rgba(231,76,60,.15); border-color: rgba(253,237,236,.3); }
.mini-card.danger .mc-val { color: #fca5a5 !important; }

/* sidebar Refresh button — static white */
.stButton > button {
    background: #DCDCDC !important;
    color: var(--blue-dk) !important;
    border: 1px solid var(--blue-mid) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 9px 20px !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #2E3135 !important;
    opacity: 1 !important;
    border-color: var(--blue-mid) !important;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(27,156,244,.12) !important;
    outline: none !important;
}
label[data-testid="stWidgetLabel"] > div > p,
.stDateInput label, .stSelectbox label,
.stTextInput label, .stNumberInput label, .stTextArea label {
    color: var(--muted) !important;
    font-size: 11px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: .5px !important;
}

/* ── FORM SUBMIT BUTTON ── */
.stFormSubmitButton > button {
    width: 100% !important; padding: 13px !important;
    font-size: 14px !important; font-weight: 700 !important;
    background: linear-gradient(135deg, var(--blue) 0%, var(--blue-dk) 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; letter-spacing: .3px !important;
}
.stFormSubmitButton > button:hover { opacity: .88 !important; }

/* ── METRICS ── */
div[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 16px 18px !important;
    border-top: 3px solid var(--blue) !important;
}
div[data-testid="metric-container"]:nth-child(even) {
    border-top-color: var(--orange) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--muted) !important; font-size: 10px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: .7px !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--blue-dk) !important; font-size: 26px !important; font-weight: 700 !important;
}

/* ── FORM CARD ── */
.stForm {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; padding: 22px !important;
}

/* ── PAGE HEADER ── */
.pg-header {
    padding-bottom: 14px;
    border-bottom: 3px solid var(--orange);
    margin-bottom: 22px;
}
.pg-header h1 {
    font-size: 20px !important; font-weight: 700 !important;
    color: var(--text) !important; margin: 0 0 3px !important;
    letter-spacing: -.3px !important;
}
.pg-header p { color: var(--muted); font-size: 13px; margin: 0; }

/* ── SECTION LABEL ── */
.sec-label {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: var(--blue-dk);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px; margin: 18px 0 12px;
    display: flex; align-items: center; gap: 6px;
}
.sec-label::before {
    content: '';
    display: inline-block;
    width: 3px; height: 12px;
    background: linear-gradient(180deg, var(--blue), var(--orange));
    border-radius: 2px;
}

/* ── TASK CARD ── */
.task-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--blue);
    border-radius: var(--radius);
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex; align-items: flex-start; gap: 14px;
}
.task-time {
    font-size: 11px; font-weight: 700; color: var(--blue-dk);
    min-width: 40px; padding-top: 2px;
    font-variant-numeric: tabular-nums; flex-shrink: 0;
}
.task-body { flex: 1; min-width: 0; }
.task-title {
    font-size: 13px; font-weight: 600; color: var(--text);
    margin-bottom: 3px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
}
.task-meta  { font-size: 11px; color: var(--muted); }
.task-badge {
    font-size: 10px; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; white-space: nowrap;
    align-self: flex-start; flex-shrink: 0;
}
.badge-done    { background: #d5f5e3; color: #1e8449; border: 1px solid #82e0aa; }
.badge-prog    { background: var(--blue-lt); color: var(--blue-dk); border: 1px solid var(--blue-mid); }
.badge-pending { background: var(--orange-lt); color: var(--orange-dk); border: 1px solid var(--orange-mid); }
.badge-cancel  { background: #fdedec; color: #cb4335; border: 1px solid #f1948a; }
.badge-other   { background: #f0f8ff; color: var(--muted); border: 1px solid var(--border); }

/* ── NOTIF ── */
.notif {
    border-radius: 10px; padding: 13px 16px; margin-bottom: 18px;
    display: flex; align-items: flex-start; gap: 12px; border: 1px solid;
}
.notif.danger  { background: var(--danger-lt); border-color: #f1948a; }
.notif.ok      { background: var(--orange-lt); border-color: var(--orange-mid); }
.notif .ni     { font-size: 16px; line-height: 1.4; flex-shrink: 0; }
.notif .nb     { flex: 1; }
.notif .nt     { font-size: 13px; font-weight: 700; margin-bottom: 2px; }
.notif.danger .nt { color: var(--danger); }
.notif.ok     .nt { color: var(--orange-dk); }
.notif .nd    { font-size: 12px; color: var(--muted); margin-bottom: 7px; }
.pills        { display: flex; flex-wrap: wrap; gap: 5px; }
.pill {
    font-size: 11px; font-weight: 600; padding: 2px 9px;
    border-radius: 20px; background: #fdedec; color: var(--danger);
    border: 1px solid #f1948a;
}

/* ── PASSWORD GATE ── */
.pw-gate { max-width: 360px; margin: 60px auto 0; text-align: center; }
.pw-gate .pw-icon { font-size: 40px; margin-bottom: 14px; }
.pw-gate h2 { font-size: 18px; font-weight: 700; margin-bottom: 6px; color: var(--blue-dk); }
.pw-gate p  { font-size: 13px; color: var(--muted); margin-bottom: 22px; }

/* ── EDIT BUTTON (small) ── */
.stButton > button[title="Update status"],
.stButton > button[title="Update status task ini"] {
    width: auto !important; padding: 5px 10px !important;
    font-size: 12px !important;
    background: var(--blue-lt) !important;
    color: var(--blue-dk) !important;
    border: 1px solid var(--blue-mid) !important;
}
.stButton > button[title="Update status"]:hover,
.stButton > button[title="Update status task ini"]:hover {
    background: var(--blue-lt) !important; opacity: 1 !important;
}

/* ── DATAFRAME ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 10px !important; }
.stDataFrame iframe { border-radius: 10px !important; }

/* ── MISC ── */
hr { border-color: var(--border) !important; margin: 18px 0 !important; }
.stSuccess { background: var(--blue-lt) !important; border: 1px solid var(--blue-mid) !important; border-radius: 10px !important; }
.stWarning { background: var(--warn-lt) !important; border: 1px solid var(--orange-mid) !important; border-radius: 10px !important; }
.stError   { background: var(--danger-lt) !important; border: 1px solid #f1948a !important; border-radius: 10px !important; }
.stInfo    { background: var(--blue-lt) !important; border: 1px solid var(--blue-mid) !important; border-radius: 10px !important; }
.stDownloadButton > button {
    background: var(--blue-lt) !important; color: var(--blue-dk) !important;
    border: 1px solid var(--blue-mid) !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important; width: auto !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--blue-mid); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)




# ─────────────────────────────────────────────
# GOOGLE SHEETS
# ─────────────────────────────────────────────
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client  = gspread.authorize(creds)
SHEET_ID = "1PvdyLJ3DRVHnd2zScnTICOSaX1pYNxzYjZ_g9ktui9o"
sheet    = client.open_by_key(SHEET_ID).sheet1

HEADERS = [
    "Date","Hour","Staff","Division","Category","Detail",
    "Booking ID","Hotel","Supplier","Quantity",
    "Status","Total Komunikasi","Detail Komunikasi","Notes","Timestamp"
]
existing = sheet.row_values(1)
if existing != HEADERS:
    sheet.clear()
    sheet.insert_row(HEADERS, 1)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
ALL_STAFF = sorted([
    "Vial","Fandi","Geraldi","Riega","Farras","Baldy",
    "Vero","Yati","Ade","Selvy","Firda","Meiji","Rida"
])

WORK_HOURS = [f"{h:02d}:00" for h in range(0, 25)]  # 00:00–24:00

CATEGORY_LIST = [
    "Booking","Voucher Issued","Follow Up Hotel","Follow Up Supplier",
    "Void","Refund","Rename Guest","Takeover Payment",
    "Inject Debit DTM","Complaint Handling","Rekap Tagihan",
]
DETAIL_LIST = sorted([
    "New Hotel Booking","Booking Amendment","Booking Cancellation","Booking Confirmation",
    "Voucher Issued","Voucher Resend","Voucher Correction",
    "Follow Up Hotel","Follow Up Supplier","Follow Up Guest",
    "Special Request Handling","Room Request Handling",
    "Rename Guest","Add Guest Name","Takeover Payment Process","Credit Card Charge",
    "Inject Debit DTM","Refund Process","Void Transaction","Dispute Handling",
    "Complaint Handling","Rate Checking","Supplier Price Verification",
    "Manual Booking","Direct Hotel Booking","Data Correction","Other"
])
STATUS_LIST = [
    "Done","In Progress","Pending",
    "Waiting Hotel Confirmation","Waiting Supplier Confirmation","Waiting Guest Response",
    "On Hold","Refund Process","Void Process","Cancelled","Escalated","Rejected"
]
SUPPLIER_LIST = ["DOTW","WebBeds","MG Holiday","Kliknbook","Direct Hotel"]

MANAGER_PASSWORD = "789789"

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False
if "pw_error" not in st.session_state:
    st.session_state.pw_error = False
if "editing_ts" not in st.session_state:
    st.session_state.editing_ts = None   # timestamp of the task being edited

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    data = sheet.get_all_records()
    df   = pd.DataFrame(data)
    return df

def get_absent_staff(df, target_date=None):
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    if df.empty or "Staff" not in df.columns or "Date" not in df.columns:
        return ALL_STAFF, target_date
    present = df[df["Date"] == target_date]["Staff"].unique().tolist()
    return [s for s in ALL_STAFF if s not in present], target_date

def badge_class(status):
    s = str(status).lower()
    if s == "done":       return "badge-done"
    if "progress" in s:   return "badge-prog"
    if "pending" in s or "waiting" in s or "hold" in s: return "badge-pending"
    if "cancel" in s or "reject" in s: return "badge-cancel"
    return "badge-other"

def find_row_number(timestamp_val):
    """Find the 1-based row number in the sheet by matching Timestamp column."""
    try:
        ts_col = sheet.col_values(HEADERS.index("Timestamp") + 1)
        for i, val in enumerate(ts_col):
            if val == str(timestamp_val):
                return i + 1   # 1-based
    except Exception:
        pass
    return None

def update_status_in_sheet(timestamp_val, new_status, new_notes):
    """Update only the Status and Notes cells for the row matching the timestamp."""
    row_num = find_row_number(timestamp_val)
    if row_num is None:
        return False
    status_col = HEADERS.index("Status") + 1
    notes_col  = HEADERS.index("Notes")  + 1
    sheet.update_cell(row_num, status_col, new_status)
    sheet.update_cell(row_num, notes_col,  new_notes)
    return True

def parse_kom(s):
    """Parse komunikasi detail — new format: 'Email, WhatsApp' or old 'Email:N WA:N Telp:N'"""
    s = str(s)
    # new format: comma-separated channel names
    if ":" not in s:
        channels = [c.strip() for c in s.split(",") if c.strip() and c.strip() != "-"]
        email = sum(1 for c in channels if "Email" in c)
        wa    = sum(1 for c in channels if "WhatsApp" in c or "WA" in c)
        telp  = sum(1 for c in channels if "Telepon" in c or "Telp" in c)
        return email, wa, telp
    # legacy format: Email:N WA:N Telp:N
    try:
        e = int(re.search(r'Email:(\d+)', s).group(1))
        w = int(re.search(r'WA:(\d+)',    s).group(1))
        t = int(re.search(r'Telp:(\d+)',  s).group(1))
        return e, w, t
    except:
        return 0, 0, 0

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="app-brand">
        <div class="app-brand-icon">📋</div>
        <div>
            <div class="app-brand-name">Daily Task Tracker</div>
            <div class="app-brand-sub">Hotel Reservation Team</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Menu</div>', unsafe_allow_html=True)
    menu = st.selectbox("Menu", ["✏️  Input Task", "📊  Manager Dashboard"],
                        label_visibility="collapsed")

    st.markdown("---")
    if st.button("🔄  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")

    # quick stats
    absent_list, chk_date = get_absent_staff(df)
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_df  = df[df["Date"] == today_str] if not df.empty and "Date" in df.columns else pd.DataFrame()
    absent_cls = "danger" if absent_list else "ok"

    st.markdown('<div class="sb-section">Hari Ini</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mini-card">
        <div class="mc-lbl">Total Task</div>
        <div class="mc-val">{len(today_df)}</div>
        <div class="mc-sub">{today_str}</div>
    </div>
    <div class="mini-card {absent_cls}">
        <div class="mc-lbl">Belum Input</div>
        <div class="mc-val">{len(absent_list)}</div>
        <div class="mc-sub">dari {len(ALL_STAFF)} staff</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PAGE: INPUT TASK
# ═══════════════════════════════════════════════
if "Input" in menu:

    st.markdown("""
    <div class="pg-header">
        <h1>✏️ Input Task Harian</h1>
        <p>Catat setiap task yang dikerjakan beserta jam mulainya.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── My Tasks Today (per staff) ─────────────────
    # Staff selector outside form so we can show their timeline
    sel_staff = st.selectbox("👤 Pilih nama Anda", ALL_STAFF, key="staff_selector")

    # Show today's timeline for selected staff
    my_tasks = today_df[today_df["Staff"] == sel_staff] if not today_df.empty and "Staff" in today_df.columns else pd.DataFrame()

    if not my_tasks.empty:
        st.markdown('<div class="sec-label">Timeline Anda Hari Ini</div>', unsafe_allow_html=True)
        for idx, row in my_tasks.sort_values("Hour").iterrows():
            cat       = row.get("Category","")
            det       = row.get("Detail","")
            stat      = row.get("Status","")
            hotel     = row.get("Hotel","")
            bid       = row.get("Booking ID","")
            hour      = row.get("Hour","--:--")
            row_notes = row.get("Notes","")
            ts_val    = row.get("Timestamp","")
            bc        = badge_class(stat)
            meta_parts = [x for x in [hotel, bid] if x]
            meta = " · ".join(meta_parts) if meta_parts else cat

            card_col, btn_col = st.columns([10, 1])
            with card_col:
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-time">{hour}</div>
                    <div class="task-body">
                        <div class="task-title">{cat} — {det}</div>
                        <div class="task-meta">{meta}</div>
                    </div>
                    <div class="task-badge {bc}">{stat}</div>
                </div>
                """, unsafe_allow_html=True)
            with btn_col:
                st.markdown("<div style='padding-top:10px'></div>", unsafe_allow_html=True)
                if st.button("✏️", key=f"inp_edit_{ts_val}_{idx}", help="Update status"):
                    st.session_state.editing_ts = ts_val

            # Inline edit form
            if st.session_state.editing_ts == ts_val:
                with st.form(key=f"inp_update_{ts_val}_{idx}", clear_on_submit=True):
                    st.markdown(
                        f"<div style='font-size:12px;font-weight:600;color:#1b9cf4;"
                        f"margin-bottom:8px;'>Update: {hour} — {cat} · {det}</div>",
                        unsafe_allow_html=True
                    )
                    uf1, uf2 = st.columns(2)
                    with uf1:
                        new_status = st.selectbox(
                            "Status baru",
                            STATUS_LIST,
                            index=STATUS_LIST.index(stat) if stat in STATUS_LIST else 0
                        )
                    with uf2:
                        new_notes = st.text_area(
                            "Catatan",
                            value=row_notes,
                            height=70,
                            placeholder="Tambah / edit catatan..."
                        )
                    sb1, sb2 = st.columns(2)
                    with sb1:
                        save_ok = st.form_submit_button("💾  Simpan", use_container_width=True)
                    with sb2:
                        cancel_ok = st.form_submit_button("✖  Batal", use_container_width=True)

                    if save_ok:
                        ok = update_status_in_sheet(ts_val, new_status, new_notes)
                        if ok:
                            st.success(f"✅ Status → **{new_status}**")
                            st.session_state.editing_ts = None
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Gagal update. Coba refresh.")
                    if cancel_ok:
                        st.session_state.editing_ts = None
                        st.rerun()

    st.markdown('<div class="sec-label">Tambah Task Baru</div>', unsafe_allow_html=True)

    with st.form("task_form", clear_on_submit=True):

        # ── Baris 1: Tanggal · Jam · Zona Waktu · Divisi ──
        r1a, r1b, r1c, r1d = st.columns([2, 1.5, 2.5, 2])
        with r1a:
            task_date = st.date_input("📅 Tanggal", value=date.today())
        with r1b:
            _now_hour    = datetime.now().hour
            _default_idx = min(_now_hour, len(WORK_HOURS) - 1)
            task_hour = st.selectbox("🕐 Jam", WORK_HOURS, index=_default_idx)
        with r1c:
            TIMEZONE_OPTIONS = {
                "WIB — Jakarta (UTC+7)":      "Asia/Jakarta",
                "WITA — Makassar (UTC+8)":    "Asia/Makassar",
                "WIT — Jayapura (UTC+9)":     "Asia/Jayapura",
                "MYT — Kuala Lumpur (UTC+8)": "Asia/Kuala_Lumpur",
                "SGT — Singapura (UTC+8)":    "Asia/Singapore",
                "THA — Bangkok (UTC+7)":      "Asia/Bangkok",
            }
            tz_label = st.selectbox("🌏 Zona Waktu", list(TIMEZONE_OPTIONS.keys()), index=0)
        with r1d:
            division = st.selectbox("🏢 Divisi", [
                "Hotel Reservation", "Admin Reservation", "Finance"
            ])

        # ── Baris 2: Kategori · Detail Aktivitas ──────────
        r2a, r2b = st.columns(2)
        with r2a:
            category = st.selectbox("🏷️ Kategori", CATEGORY_LIST)
        with r2b:
            detail = st.selectbox("📋 Detail Aktivitas", DETAIL_LIST)

        # ── Baris 3: Booking ID · Hotel · Supplier ────────
        r3a, r3b, r3c = st.columns(3)
        with r3a:
            booking_id = st.text_input("🔖 Booking ID", placeholder="e.g. VAGHB2603842454")
        with r3b:
            hotel = st.text_input("🏩 Hotel", placeholder="e.g. Grand Hyatt Jakarta")
        with r3c:
            supplier = st.selectbox("🤝 Supplier", SUPPLIER_LIST)

        # ── Baris 4: Status · Qty · Jalur Komunikasi ──────
        r4a, r4b, r4c = st.columns([2, 1, 3])
        with r4a:
            status = st.selectbox("📌 Status", STATUS_LIST)
        with r4b:
            qty = st.number_input("🔢 Qty", min_value=1, value=1)
        with r4c:
            kom_channels = st.multiselect(
                "📡 Jalur Komunikasi",
                options=["📧 Email", "💬 WhatsApp", "📞 Telepon", "🖥️ Sistem/Portal", "📠 Fax"],
                default=[],
                placeholder="Pilih jalur komunikasi..."
            )

        # ── Baris 5: Catatan ──────────────────────────────
        notes = st.text_area("📝 Catatan", placeholder="Opsional — isi jika ada hal penting...", height=75)

        submitted = st.form_submit_button("✅  Simpan Task", use_container_width=True)

        if submitted:
            import pytz
            tz_name   = TIMEZONE_OPTIONS[tz_label]
            tz_obj    = pytz.timezone(tz_name)
            now_local = datetime.now(tz_obj)
            tz_abbr   = tz_label.split(" — ")[0]
            ts = now_local.strftime("%Y-%m-%d %H:%M:%S") + f" {tz_abbr}"

            kom_detail = ", ".join([c.split(" ", 1)[1] for c in kom_channels]) if kom_channels else "-"
            kom_total  = len(kom_channels)
            new_row = [
                str(task_date), task_hour, sel_staff, division,
                category, detail, booking_id, hotel, supplier,
                qty, status, kom_total, kom_detail, notes,
                ts
            ]
            sheet.append_row(new_row)
            st.cache_data.clear()
            st.success(f"✅ Task **{task_hour} — {category}** berhasil disimpan!")
            st.rerun()

# ═══════════════════════════════════════════════
# PAGE: MANAGER DASHBOARD (password gated)
# ═══════════════════════════════════════════════
if "Dashboard" in menu:

    # ── PASSWORD GATE ──────────────────────────────
    if not st.session_state.dashboard_unlocked:
        st.markdown("""
        <div class="pg-header">
            <h1>📊 Manager Dashboard</h1>
            <p>Halaman ini membutuhkan autentikasi.</p>
        </div>
        """, unsafe_allow_html=True)

        col_c = st.columns([1, 2, 1])[1]
        with col_c:
            st.markdown("""
            <div style="background:var(--surface);border:1px solid var(--border);
                        border-radius:14px;padding:32px 28px;text-align:center;margin-top:20px;">
                <div style="font-size:36px;margin-bottom:12px;">🔒</div>
                <div style="font-size:17px;font-weight:600;margin-bottom:6px;">Manager Only</div>
                <div style="font-size:13px;color:var(--muted);margin-bottom:22px;">
                    Masukkan password untuk mengakses dashboard.
                </div>
            </div>
            """, unsafe_allow_html=True)
            pw_input = st.text_input("Password", type="password",
                                     placeholder="Masukkan password...",
                                     label_visibility="collapsed")
            if st.button("🔓  Masuk", use_container_width=True):
                if pw_input == MANAGER_PASSWORD:
                    st.session_state.dashboard_unlocked = True
                    st.session_state.pw_error = False
                    st.rerun()
                else:
                    st.session_state.pw_error = True
                    st.rerun()
            if st.session_state.pw_error:
                st.error("❌ Password salah. Silakan coba lagi.")
        st.stop()

    # ── DASHBOARD CONTENT ──────────────────────────
    header_c, logout_c = st.columns([5, 1])
    with header_c:
        st.markdown("""
        <div class="pg-header">
            <h1>📊 Manager Dashboard</h1>
            <p>Pantau aktivitas tim reservasi secara real-time.</p>
        </div>
        """, unsafe_allow_html=True)
    with logout_c:
        st.markdown("<div style='padding-top:28px'></div>", unsafe_allow_html=True)
        if st.button("🔒 Keluar", use_container_width=True):
            st.session_state.dashboard_unlocked = False
            st.rerun()

    # ── Absent Notification ────────────────────────
    absent_list, chk_date = get_absent_staff(df)
    if absent_list:
        pills = "".join([f'<span class="pill">{s}</span>' for s in absent_list])
        st.markdown(f"""
        <div class="notif danger">
            <div class="ni">🔔</div>
            <div class="nb">
                <div class="nt">{len(absent_list)} staff belum input hari ini
                    <span style="font-size:11px;font-weight:400;color:var(--muted);margin-left:6px;">{chk_date}</span>
                </div>
                <div class="nd">Silakan ingatkan staff berikut.</div>
                <div class="pills">{pills}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="notif ok">
            <div class="ni">✅</div>
            <div class="nb">
                <div class="nt">Semua staff sudah input!</div>
                <div class="nd" style="margin-bottom:0">
                    Seluruh {len(ALL_STAFF)} staff telah mencatat aktivitas hari ini ({chk_date}).
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ Belum ada data. Silakan input aktivitas terlebih dahulu.")
        st.stop()

    # ── Date filter ────────────────────────────────
    st.markdown('<div class="sec-label">Filter Tampilan</div>', unsafe_allow_html=True)
    fa, fb, fc, _ = st.columns([2,2,2,4])
    with fa:
        sel_date_filter = st.selectbox("Periode", ["Hari Ini","7 Hari Terakhir","Semua"])
    with fb:
        sel_staff_filter = st.selectbox("Staff",
            ["Semua"] + ALL_STAFF)
    with fc:
        sel_div_filter = st.selectbox("Divisi",
            ["Semua","Hotel Reservation","Admin Reservation","Finance"])

    fdf = df.copy()
    if "Date" in fdf.columns:
        fdf["Date"] = fdf["Date"].astype(str)
        today_str = datetime.now().strftime("%Y-%m-%d")
        if sel_date_filter == "Hari Ini":
            fdf = fdf[fdf["Date"] == today_str]
        elif sel_date_filter == "7 Hari Terakhir":
            fdf["_d"] = pd.to_datetime(fdf["Date"], errors="coerce")
            fdf = fdf[fdf["_d"] >= pd.Timestamp.now() - pd.Timedelta(days=7)].drop(columns="_d")
    if sel_staff_filter != "Semua" and "Staff" in fdf.columns:
        fdf = fdf[fdf["Staff"] == sel_staff_filter]
    if sel_div_filter != "Semua" and "Division" in fdf.columns:
        fdf = fdf[fdf["Division"] == sel_div_filter]

    # ── KPIs ───────────────────────────────────────
    st.markdown('<div class="sec-label">Ringkasan</div>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.metric("📋 Total Task", len(fdf))
    with k2: st.metric("👥 Aktif Staff", fdf["Staff"].nunique() if "Staff" in fdf.columns else 0)
    with k3: st.metric("🔢 Total Qty",   int(fdf["Quantity"].sum()) if "Quantity" in fdf.columns else 0)
    with k4:
        done = len(fdf[fdf["Status"]=="Done"]) if "Status" in fdf.columns else 0
        st.metric("✅ Done", done)
    with k5:
        total_kom = int(fdf["Total Komunikasi"].sum()) if "Total Komunikasi" in fdf.columns else 0
        st.metric("💬 Komunikasi", total_kom)

    st.divider()

    # ── Hourly Activity Heatmap (today or filtered) ─
    st.markdown('<div class="sec-label">Aktivitas per Jam</div>', unsafe_allow_html=True)
    if "Hour" in fdf.columns and not fdf.empty:
        hour_counts = fdf.groupby("Hour").size().reset_index(name="n")
        all_hours_df = pd.DataFrame({"Hour": WORK_HOURS})
        hour_counts = all_hours_df.merge(hour_counts, on="Hour", how="left").fillna(0)
        hour_counts["n"] = hour_counts["n"].astype(int)

        fig_h = go.Figure(go.Bar(
            x=hour_counts["Hour"],
            y=hour_counts["n"],
            marker=dict(
                color=hour_counts["n"],
                colorscale=[[0,"#e0f7f4"],[0.4,"#5eead4"],[1,"#1b9cf4"]],
                line=dict(width=0)
            ),
            text=hour_counts["n"].apply(lambda v: str(v) if v > 0 else ""),
            textposition="outside",
            textfont=dict(color="#6b7280", size=12)
        ))
        fig_h.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#6b7280", family="DM Sans"),
            margin=dict(l=0,r=0,t=8,b=0), height=200,
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#374151")),
            yaxis=dict(showgrid=True, gridcolor="#e6f4ff", showticklabels=False, zeroline=False),
            bargap=0.25,
        )
        st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

    # ── Charts row ─────────────────────────────────
    ca, cb = st.columns([3,2])
    with ca:
        st.markdown('<div class="sec-label">Task per Staff</div>', unsafe_allow_html=True)
        if "Staff" in fdf.columns and not fdf.empty:
            sc = fdf.groupby("Staff").size().reset_index(name="n").sort_values("n")
            fig_s = go.Figure(go.Bar(
                x=sc["n"], y=sc["Staff"], orientation="h",
                marker=dict(color="#1b9cf4", line=dict(width=0)),
                text=sc["n"], textposition="outside",
                textfont=dict(color="#6b7280", size=12)
            ))
            fig_s.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                margin=dict(l=0,r=36,t=8,b=0), height=320,
                xaxis=dict(showgrid=True, gridcolor="#e6f4ff", showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#374151")),
                bargap=0.38,
            )
            st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})

    with cb:
        st.markdown('<div class="sec-label">Kategori</div>', unsafe_allow_html=True)
        if "Category" in fdf.columns and not fdf.empty:
            cc = fdf.groupby("Category").size().reset_index(name="n")
            colors = ["#1b9cf4","#0d7fd6","#16a34a","#d97706","#dc2626",
                      "#7c3aed","#1b9cf4","#9333ea","#ea580c","#65a30d","#be185d"]
            fig_c = go.Figure(go.Pie(
                labels=cc["Category"], values=cc["n"], hole=0.52,
                marker=dict(colors=colors[:len(cc)], line=dict(color="#fff",width=2)),
                textinfo="percent",
                textfont=dict(size=11, color="white"),
                hovertemplate="<b>%{label}</b><br>%{value} task<br>%{percent}<extra></extra>"
            ))
            fig_c.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                legend=dict(font=dict(size=10, color="#6b7280"), bgcolor="rgba(0,0,0,0)",
                            orientation="h", x=0, y=-0.18),
                margin=dict(l=0,r=0,t=8,b=60), height=320,
                annotations=[dict(
                    text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>tasks</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=15, color="#1a1d23", family="DM Sans")
                )]
            )
            st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})

    # ── Row 2 charts ───────────────────────────────
    cd, ce = st.columns(2)
    with cd:
        st.markdown('<div class="sec-label">Supplier</div>', unsafe_allow_html=True)
        if "Supplier" in fdf.columns and not fdf.empty:
            sp = fdf.groupby("Supplier").size().reset_index(name="n").sort_values("n", ascending=False)
            fig_sp = go.Figure(go.Bar(
                x=sp["Supplier"], y=sp["n"],
                marker=dict(color="#0d7fd6", line=dict(width=0)),
                text=sp["n"], textposition="outside",
                textfont=dict(color="#6b7280", size=13)
            ))
            fig_sp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                margin=dict(l=0,r=0,t=8,b=0), height=240,
                xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#374151")),
                yaxis=dict(showgrid=True, gridcolor="#e6f4ff", showticklabels=False, zeroline=False),
                bargap=0.42,
            )
            st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})

    with ce:
        st.markdown('<div class="sec-label">Komunikasi per Channel</div>', unsafe_allow_html=True)
        if "Detail Komunikasi" in fdf.columns and not fdf.empty:
            parsed   = fdf["Detail Komunikasi"].apply(parse_kom)
            t_email  = sum(x[0] for x in parsed)
            t_wa     = sum(x[1] for x in parsed)
            t_telp   = sum(x[2] for x in parsed)
            fig_k = go.Figure(go.Bar(
                x=["Email","WhatsApp","Telepon"],
                y=[t_email, t_wa, t_telp],
                marker=dict(color=["#1b9cf4","#0d7fd6","#374151"], line=dict(width=0)),
                text=[t_email, t_wa, t_telp], textposition="outside",
                textfont=dict(color="#6b7280", size=13)
            ))
            fig_k.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#6b7280", family="DM Sans"),
                margin=dict(l=0,r=0,t=8,b=0), height=240,
                xaxis=dict(showgrid=False, tickfont=dict(size=13, color="#374151")),
                yaxis=dict(showgrid=True, gridcolor="#e6f4ff", showticklabels=False, zeroline=False),
                bargap=0.45,
            )
            st.plotly_chart(fig_k, use_container_width=True, config={"displayModeBar": False})

    # ── Tren harian ────────────────────────────────
    if "Date" in fdf.columns and fdf["Date"].nunique() > 1:
        st.markdown('<div class="sec-label">Tren Harian</div>', unsafe_allow_html=True)
        daily = fdf.groupby("Date").size().reset_index(name="n")
        daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
        daily = daily.dropna().sort_values("Date")
        fig_t = go.Figure(go.Scatter(
            x=daily["Date"], y=daily["n"],
            mode="lines+markers",
            line=dict(color="#1b9cf4", width=2.5),
            marker=dict(size=6, color="#1b9cf4", line=dict(color="white", width=1.5)),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.06)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y} task<extra></extra>"
        ))
        fig_t.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#6b7280", family="DM Sans"),
            margin=dict(l=0,r=0,t=8,b=0), height=200,
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#6b7280")),
            yaxis=dict(showgrid=True, gridcolor="#e6f4ff", tickfont=dict(size=11, color="#6b7280"), zeroline=False),
        )
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

    # ── Timeline detail (per-hour breakdown) ───────
    st.divider()
    st.markdown('<div class="sec-label">Timeline Detail Hari Ini per Staff</div>', unsafe_allow_html=True)
    today_all = df[df["Date"] == today_str] if not df.empty and "Date" in df.columns else pd.DataFrame()
    if today_all.empty:
        st.info("Belum ada task yang diinput hari ini.")
    else:
        for staff_name in ALL_STAFF:
            staff_tasks = today_all[today_all["Staff"] == staff_name] if "Staff" in today_all.columns else pd.DataFrame()
            if staff_tasks.empty:
                continue
            with st.expander(f"👤 {staff_name}  ({len(staff_tasks)} task)", expanded=False):
                for idx, row in staff_tasks.sort_values("Hour").iterrows():
                    cat       = row.get("Category","")
                    det       = row.get("Detail","")
                    stat      = row.get("Status","")
                    hotel     = row.get("Hotel","")
                    bid       = row.get("Booking ID","")
                    hour      = row.get("Hour","--:--")
                    row_notes = row.get("Notes","")
                    ts_val    = row.get("Timestamp","")
                    bc        = badge_class(stat)
                    meta_parts = [x for x in [hotel, bid] if x]
                    meta = " · ".join(meta_parts) if meta_parts else ""

                    # task card + edit button in same row
                    card_col, btn_col = st.columns([10, 1])
                    with card_col:
                        st.markdown(f"""
                        <div class="task-card">
                            <div class="task-time">{hour}</div>
                            <div class="task-body">
                                <div class="task-title">{cat} — {det}</div>
                                <div class="task-meta">{meta}{' · ' + row_notes if row_notes else ''}</div>
                            </div>
                            <div class="task-badge {bc}">{stat}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with btn_col:
                        st.markdown("<div style='padding-top:10px'></div>", unsafe_allow_html=True)
                        edit_key = f"edit_{ts_val}_{idx}"
                        if st.button("✏️", key=edit_key, help="Update status task ini"):
                            st.session_state.editing_ts = ts_val

                    # ── Inline edit form (shown when this task is selected) ──
                    if st.session_state.editing_ts == ts_val:
                        with st.form(key=f"update_form_{ts_val}_{idx}", clear_on_submit=True):
                            st.markdown(
                                f"<div style='font-size:12px;font-weight:600;color:#1b9cf4;"
                                f"margin-bottom:8px;'>Update task: {hour} — {cat} · {det}</div>",
                                unsafe_allow_html=True
                            )
                            uf1, uf2 = st.columns(2)
                            with uf1:
                                new_status = st.selectbox(
                                    "Status baru",
                                    STATUS_LIST,
                                    index=STATUS_LIST.index(stat) if stat in STATUS_LIST else 0
                                )
                            with uf2:
                                new_notes = st.text_area(
                                    "Catatan (opsional)",
                                    value=row_notes,
                                    height=70,
                                    placeholder="Tambah / edit catatan..."
                                )
                            sb1, sb2 = st.columns(2)
                            with sb1:
                                save_btn = st.form_submit_button("💾  Simpan Update", use_container_width=True)
                            with sb2:
                                cancel_btn = st.form_submit_button("✖  Batal", use_container_width=True)

                            if save_btn:
                                ok = update_status_in_sheet(ts_val, new_status, new_notes)
                                if ok:
                                    st.success(f"✅ Status diperbarui → **{new_status}**")
                                    st.session_state.editing_ts = None
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal menemukan task di sheet. Coba refresh terlebih dahulu.")
                            if cancel_btn:
                                st.session_state.editing_ts = None
                                st.rerun()

    # ── Data Table ─────────────────────────────────
    st.divider()
    st.markdown('<div class="sec-label">Tabel Data Lengkap</div>', unsafe_allow_html=True)
    st.dataframe(fdf, use_container_width=True, height=360, hide_index=True)

    dl1, _ = st.columns([1,5])
    with dl1:
        csv = fdf.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "task_report.csv", mime="text/csv")
