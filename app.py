"""
LoanGuard AI — Premium Fintech Dashboard
Streamlit frontend: loan agreement risk analysis, cost calculator, safety report.
"""

import html
import streamlit as st

from modules.cost_calculator import CostResult, calculate_true_cost
from modules.pdf_processor import process_pdf_upload
from modules.report_generator import generate_safety_report
from modules.risk_analyzer import RiskAnalysisResult, analyze_loan_text

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LoanGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS — dark premium fintech theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ── */
:root { color-scheme: dark; }
html, body, [data-testid="stApp"] {
    background: #060d1a !important;
    color: #e2e8f0;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stSidebar"] { background: #080f20 !important; border-right: 1px solid rgba(255,255,255,0.07); }
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 8px 24px rgba(14,165,233,0.25) !important;
    transition: all 0.2s !important;
}
button[kind="primary"]:hover { transform: translateY(-1px); box-shadow: 0 12px 32px rgba(14,165,233,0.35) !important; }
button[kind="secondary"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}
.stTextArea textarea, .stNumberInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 0.92rem !important;
}
.stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: rgba(14,165,233,0.5) !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.12) !important;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
[data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 800 !important; }
div[data-testid="stFileUploaderDropzone"] {
    background: rgba(14,165,233,0.05) !important;
    border: 2px dashed rgba(14,165,233,0.3) !important;
    border-radius: 16px !important;
}
.stDivider { border-color: rgba(255,255,255,0.08) !important; }
.stCaption { color: #64748b !important; }

/* ── Hero header ── */
.main-header {
    background: linear-gradient(135deg, #0a1628 0%, #0f2044 45%, #091428 100%);
    padding: 2.2rem 2.4rem;
    border-radius: 28px;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(14,165,233,0.18);
    box-shadow: 0 32px 80px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(14,165,233,0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.main-header h1 {
    margin: 0 0 0.5rem;
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #f8fafc 0%, #7dd3fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.main-header .subtitle { color: #94a3b8; margin: 0 0 1.6rem; font-size: 1.05rem; line-height: 1.6; max-width: 600px; }
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(14,165,233,0.14);
    border: 1px solid rgba(14,165,233,0.28);
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.8rem;
    color: #7dd3fc;
    font-weight: 600;
    margin: 0 0.4rem 0.5rem 0;
    letter-spacing: 0.03em;
}

/* ── Sidebar ── */
.sidebar-brand { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.6rem; padding: 0 0.5rem; }
.sidebar-brand .brand-text h2 { margin: 0; font-size: 1.3rem; font-weight: 800; color: #f8fafc; }
.sidebar-brand .brand-text p { margin: 0; color: #64748b; font-size: 0.8rem; }
.sidebar-section-title { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #475569; margin: 1.2rem 0 0.5rem 0.5rem; font-weight: 600; }
.nav-btn-wrapper button {
    width: 100%;
    text-align: left !important;
    justify-content: flex-start !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 14px !important;
    color: #94a3b8 !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    transition: all 0.18s !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
}
.nav-btn-wrapper button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #e2e8f0 !important;
    border-color: rgba(255,255,255,0.08) !important;
}
.nav-btn-active button {
    background: rgba(14,165,233,0.14) !important;
    border-color: rgba(14,165,233,0.28) !important;
    color: #7dd3fc !important;
    font-weight: 600 !important;
}
.sidebar-status {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1rem 1rem;
    margin: 1rem 0;
}
.sidebar-status p { margin: 0.3rem 0; color: #94a3b8; font-size: 0.82rem; }
.sidebar-status .status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 0.45rem;
    vertical-align: middle;
}
.dot-done { background: #10b981; }
.dot-wait { background: #475569; }
.dot-act  { background: #f59e0b; animation: pulse-dot 1.4s ease-in-out infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Section heading ── */
.section-head {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1.1rem;
}
.section-head h2 { margin: 0; font-size: 1.2rem; font-weight: 700; color: #f8fafc; }
.section-head .badge {
    background: rgba(14,165,233,0.14);
    border: 1px solid rgba(14,165,233,0.24);
    border-radius: 999px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    color: #7dd3fc;
    font-weight: 600;
    letter-spacing: 0.06em;
}

/* ── Score card ── */
.score-banner {
    padding: 1.6rem 1.8rem;
    border-radius: 24px;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.score-banner.low  { background: linear-gradient(135deg,#052e16,#064e3b); border: 1px solid #059669; }
.score-banner.medium { background: linear-gradient(135deg,#1c1404,#3d2000); border: 1px solid #d97706; }
.score-banner.high { background: linear-gradient(135deg,#1c0505,#3d0000); border: 1px solid #dc2626; }
.score-big { font-size: 4rem; font-weight: 900; margin: 0; line-height: 1; }
.score-banner.low  .score-big { color: #34d399; }
.score-banner.medium .score-big { color: #fbbf24; }
.score-banner.high .score-big { color: #f87171; }
.score-label { font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase; color: #94a3b8; margin: 0 0 0.3rem; }
.score-category {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-top: 0.8rem;
}
.score-category.low    { background: rgba(16,185,129,0.18); color: #34d399; border: 1px solid rgba(16,185,129,0.35); }
.score-category.medium { background: rgba(245,158,11,0.18); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); }
.score-category.high   { background: rgba(239,68,68,0.18);  color: #f87171; border: 1px solid rgba(239,68,68,0.35); }
.score-summary { color: #cbd5e1; font-size: 0.93rem; line-height: 1.65; margin-top: 0.9rem; }

/* ── Metric grid ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.85rem;
    margin: 1.2rem 0;
}
.metric-tile {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.1rem 1.15rem;
    position: relative;
    overflow: hidden;
}
.metric-tile::after {
    content: attr(data-icon);
    position: absolute;
    right: -6px; bottom: -10px;
    font-size: 3.5rem;
    opacity: 0.08;
    pointer-events: none;
}
.metric-tile .mt-label { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #64748b; margin: 0 0 0.4rem; }
.metric-tile .mt-value { font-size: 1.9rem; font-weight: 800; color: #f8fafc; margin: 0; }
.metric-tile .mt-note  { font-size: 0.78rem; color: #94a3b8; margin: 0.4rem 0 0; }

/* ── Risk cards ── */
.risk-list { display: grid; gap: 1rem; margin: 1rem 0; }
.risk-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.4rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s;
}
.risk-card:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(0,0,0,0.25); }
.risk-card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}
.risk-card-icon { font-size: 1.4rem; margin-right: 0.5rem; }
.risk-card-title { font-size: 1.02rem; font-weight: 700; color: #f8fafc; margin: 0; display: flex; align-items: center; }
.risk-card-subtitle { font-size: 0.8rem; color: #64748b; margin: 0.2rem 0 0; }
.severity-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    white-space: nowrap;
    flex-shrink: 0;
}
.sev-high   { background: rgba(127,29,29,0.7);  color: #fecaca; border: 1px solid #ef4444; }
.sev-medium { background: rgba(120,53,15,0.7);  color: #fde68a; border: 1px solid #f59e0b; }
.sev-low    { background: rgba(6,78,59,0.7);    color: #a7f3d0; border: 1px solid #10b981; }
.risk-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin: 0 0 0.4rem;
}
.risk-clause {
    background: rgba(0,0,0,0.3);
    border-left: 3px solid rgba(255,255,255,0.15);
    border-radius: 0 10px 10px 0;
    padding: 0.65rem 0.9rem;
    font-size: 0.85rem;
    color: #cbd5e1;
    font-style: italic;
    margin: 0 0 1rem;
    line-height: 1.6;
}
.risk-why {
    color: #94a3b8;
    font-size: 0.88rem;
    line-height: 1.65;
    margin: 0 0 1rem;
}
.risk-recommendation {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 12px;
    padding: 0.6rem 0.9rem;
    font-size: 0.85rem;
    color: #6ee7b7;
    margin: 0;
    line-height: 1.55;
}

/* ── Cost calculator ── */
.calc-section {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 24px;
    padding: 1.5rem 1.6rem;
    margin-top: 1.5rem;
}
.cost-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
    margin: 1rem 0;
}
.cost-tile {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px;
    padding: 1.1rem 1.2rem;
}
.cost-tile .ct-label { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #64748b; margin: 0 0 0.35rem; }
.cost-tile .ct-value { font-size: 1.7rem; font-weight: 800; color: #f8fafc; margin: 0; }
.cost-tile .ct-value.green { color: #34d399; }
.cost-tile .ct-value.red   { color: #f87171; }
.cost-tile .ct-value.amber { color: #fbbf24; }
.cost-insight {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-top: 0.9rem;
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.65;
}

/* ── Report ── */
.report-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 1.6rem 1.8rem;
    margin-top: 1.8rem;
}
.report-preview {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.7;
    max-height: 420px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3.5rem 1rem;
    color: #475569;
}
.empty-state .es-icon { font-size: 3rem; margin-bottom: 0.9rem; display: block; opacity: 0.5; }
.empty-state h3 { color: #64748b; margin: 0 0 0.5rem; font-size: 1.05rem; }
.empty-state p  { color: #475569; font-size: 0.88rem; margin: 0; line-height: 1.6; }

/* ── Workflow steps ── */
.workflow {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.6rem;
    margin: 1rem 0;
}
.wf-step {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.8rem 0.9rem;
    text-align: center;
}
.wf-step .wf-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px; height: 26px;
    background: rgba(14,165,233,0.18);
    border: 1px solid rgba(14,165,233,0.3);
    border-radius: 50%;
    font-size: 0.72rem;
    font-weight: 700;
    color: #7dd3fc;
    margin: 0 auto 0.5rem;
}
.wf-step p { margin: 0; font-size: 0.78rem; color: #94a3b8; line-height: 1.4; }

/* ── Success / info banners ── */
.banner-success {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 14px;
    padding: 0.75rem 1rem;
    color: #6ee7b7;
    font-size: 0.88rem;
    margin: 0.8rem 0;
}
.banner-warning {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 14px;
    padding: 0.75rem 1rem;
    color: #fde68a;
    font-size: 0.88rem;
    margin: 0.8rem 0;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 999px; }

@media (max-width: 900px) {
    .metric-grid { grid-template-columns: repeat(2, 1fr); }
    .cost-grid   { grid-template-columns: 1fr; }
    .workflow    { grid-template-columns: repeat(2, 1fr); }
}
//* ==================================
   LOANGUARD AI FINAL UI FIX
   ================================== */


/* MAIN APP BACKGROUND */
.stApp {
    background: #020617 !important;
    color: #f8fafc !important;
}


/* STREAMLIT HEADER FIX */
header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background: transparent !important;
}


/* TEXT INPUT + TEXTAREA + NUMBER INPUT */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #0f172a !important;

    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;

    border: 1px solid rgba(56,189,248,0.35) !important;
    border-radius: 14px !important;

    box-shadow: none !important;
}


/* PLACEHOLDER */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}


/* NUMBER INPUT PLUS MINUS */
.stNumberInput button {
    background-color: #1e293b !important;

    color: #ffffff !important;

    border-radius: 10px !important;

    border: 1px solid rgba(56,189,248,0.35) !important;
}


/* MAIN BUTTONS */
.stButton button,
.stDownloadButton button {

    background: linear-gradient(
        90deg,
        #06b6d4,
        #0284c7
    ) !important;

    color: white !important;

    font-weight: 700 !important;

    border: none !important;

    border-radius: 14px !important;
}


/* LABELS + NORMAL TEXT */
label,
p,
.stMarkdown {
    color: #e5e7eb !important;
}


/* SIDEBAR */
[data-testid="stSidebar"] {

    background-color: #020617 !important;

}


/* CARDS */
[data-testid="stVerticalBlockBorderWrapper"] {

    background: rgba(15,23,42,0.85) !important;

    border: 1px solid rgba(255,255,255,0.12) !important;

    border-radius: 18px !important;

}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_AGREEMENT = (
    "This Loan Agreement is entered into between FastCash Lenders Pvt. Ltd. (\"Lender\") "
    "and the undersigned borrower. A processing fee shall be deducted from the disbursed amount before transfer. "
    "Late payment penalty of 5% per month shall apply on outstanding balance. "
    "The lender may access your phone contacts and call your references for recovery purposes. "
    "Personal data including contact details may be shared with third party partners and affiliates. "
    "Recovery agents may visit your home or workplace without prior notice. "
    "Repayment terms may vary at the lender's sole discretion without prior intimation to the borrower. "
    "Interest rate subject to change as determined by lender."
)

RISK_CARD_META = {
    "Hidden Fees":                {"icon": "🕵️", "rec": "Ask lender for a complete fee schedule in writing before signing."},
    "Processing Charges":         {"icon": "💰", "rec": "Compare processing fees across lenders and confirm the net disbursal amount."},
    "High Penalty":               {"icon": "⚠️", "rec": "Negotiate penalty caps; ensure you can afford the EMI even with a short delay."},
    "Contact Access Permission":  {"icon": "📱", "rec": "Request removal of contact access clauses — they are not required for legitimate lending."},
    "Data Sharing":               {"icon": "🔒", "rec": "Insist on a data-protection clause limiting sharing to strictly necessary parties."},
    "Aggressive Recovery Terms":  {"icon": "🚨", "rec": "Check RBI Fair Practice Code; lenders cannot harass or visit without proper notice."},
    "Unclear Repayment Terms":    {"icon": "📄", "rec": "Request a fixed EMI schedule with total interest amount stated clearly in writing."},
}

SEV_CLASS = {"high": "sev-high", "medium": "sev-medium", "low": "sev-low"}
SEV_ICON  = {"high": "🔴", "medium": "🟡", "low": "🟢"}

# ─────────────────────────────────────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "page":               "overview",
    "agreement_text":     "",
    "analysis":           None,
    "cost_result":        None,
    "report":             "",
    "input_source":       "",
    "pdf_meta":           None,
    "last_pdf_sig":       "",
    "calc_triggered":     False,
    "show_report":        False,
}
for k, v in _DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────
def _pdf_sig(f) -> str:
    return f"{f.name}:{f.size}"

def _run_analysis(text: str, source: str) -> None:
    st.session_state.agreement_text = text
    st.session_state.input_source   = source
    with st.spinner("🧠 Analyzing agreement for risky clauses..."):
        st.session_state.analysis = analyze_loan_text(text)
    st.session_state.report      = ""
    st.session_state.show_report = False
    st.session_state.page        = "analytics"

def _nav(page: str):
    st.session_state.page = page

def _score_class(category: str) -> str:
    return category.lower()  # low / medium / high

def render_risk_card(finding) -> str:
    meta = RISK_CARD_META.get(finding.category, {
        "icon": "⚠️",
        "rec":  "Ask the lender to explain this clause clearly in writing.",
    })
    sev_cls  = SEV_CLASS.get(finding.severity, "sev-medium")
    sev_icon = SEV_ICON.get(finding.severity, "🟡")
    name    = html.escape(finding.category)
    clause  = html.escape(finding.snippet)
    why     = html.escape(finding.explanation)
    rec     = html.escape(meta["rec"])
    sev_txt = html.escape(finding.severity.upper())
    icon    = meta["icon"]
    return f"""
<div class="risk-card">
  <div class="risk-card-header">
    <div>
      <p class="risk-card-title"><span class="risk-card-icon">{icon}</span> {name}</p>
      <p class="risk-card-subtitle">Clause detected · Action recommended</p>
    </div>
    <span class="severity-badge {sev_cls}">{sev_icon} {sev_txt}</span>
  </div>
  <div class="risk-section-label">Detected Clause</div>
  <blockquote class="risk-clause">{clause}</blockquote>
  <div class="risk-section-label">Why This Is Risky</div>
  <p class="risk-why">{why}</p>
  <div class="risk-section-label">Recommended Action</div>
  <p class="risk-recommendation">✅ {rec}</p>
</div>"""

def _status_row(done: bool, active: bool, label: str) -> str:
    cls = "dot-done" if done else ("dot-act" if active else "dot-wait")
    return f"<p><span class='status-dot {cls}'></span>{label}</p>"

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <span style="font-size:2rem;">🛡️</span>
      <div class="brand-text">
        <h2>LoanGuard AI</h2>
        <p>Fintech agreement intelligence</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons
    page = st.session_state.page
    st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)

    nav_items = [
        ("overview",   "🏠", "Overview"),
        ("agreement",  "📄", "Agreement"),
        ("analytics",  "📊", "Analytics"),
        ("reports",    "📥", "Reports"),
    ]
    for page_id, icon, label in nav_items:
        active_cls = "nav-btn-active" if page == page_id else "nav-btn-wrapper"
        with st.container():
            st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{page_id}", use_container_width=True):
                _nav(page_id)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Progress status
    has_text  = bool(st.session_state.agreement_text.strip())
    has_anal  = st.session_state.analysis is not None
    has_cost  = st.session_state.cost_result is not None
    has_rep   = bool(st.session_state.report)

    st.markdown('<div class="sidebar-section-title">Session Progress</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-status">
      {_status_row(has_text, not has_text, "Agreement loaded")}
      {_status_row(has_anal, has_text and not has_anal, "Risk analysis done")}
      {_status_row(has_cost, has_anal and not has_cost, "Cost calculated")}
      {_status_row(has_rep,  has_anal and not has_rep,  "Report generated")}
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="sidebar-section-title">Demo Tools</div>', unsafe_allow_html=True)

    if st.button("⚡ Load Sample Agreement", use_container_width=True):
        st.session_state.agreement_text = SAMPLE_AGREEMENT
        st.session_state.input_source   = "demo"
        st.session_state.analysis       = None
        st.session_state.cost_result    = None
        st.session_state.report         = ""
        st.session_state.show_report    = False
        st.session_state.page           = "agreement"
        st.rerun()

    if st.button("🔄 Reset Workspace", use_container_width=True):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

    st.divider()
    st.caption("🔒 Built for hackathon demos · Not legal advice · Text-based PDFs only")


# ─────────────────────────────────────────────────────────────────────────────
# Page router
# ─────────────────────────────────────────────────────────────────────────────
current_page = st.session_state.page


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if current_page == "overview":
    st.markdown("""
    <div class="main-header">
      <h1>🛡️ LoanGuard AI</h1>
      <p class="subtitle">
        Premium fintech intelligence that protects borrowers from predatory loan agreements —
        risky clause detection, hidden fee analysis, and true cost calculation in seconds.
      </p>
      <div>
        <span class="hero-pill">⚡ Instant Analysis</span>
        <span class="hero-pill">🔍 7 Risk Categories</span>
        <span class="hero-pill">💰 True Cost Engine</span>
        <span class="hero-pill">📥 PDF Reports</span>
        <span class="hero-pill">🇮🇳 Rupee-Ready</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Workflow
    st.markdown("""
    <div class="section-head"><h2>How It Works</h2><span class="badge">4 STEPS</span></div>
    <div class="workflow">
      <div class="wf-step"><div class="wf-num">1</div><p>Upload PDF or paste agreement text</p></div>
      <div class="wf-step"><div class="wf-num">2</div><p>AI scans 7 risk categories instantly</p></div>
      <div class="wf-step"><div class="wf-num">3</div><p>Enter loan amounts for cost breakdown</p></div>
      <div class="wf-step"><div class="wf-num">4</div><p>Download your full safety report</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("""
        <div class="section-head"><h2>Risk Categories Detected</h2></div>
        """, unsafe_allow_html=True)
        risks = [
            ("🕵️", "Hidden Fees",               "HIGH",   "Undisclosed charges buried in terms"),
            ("💰", "Processing Charges",         "MEDIUM", "Upfront fees reducing disbursal"),
            ("⚠️", "High Penalty",               "HIGH",   "Excessive late payment penalties"),
            ("📱", "Contact Access",             "HIGH",   "Permission to access your phonebook"),
            ("🔒", "Data Sharing",               "MEDIUM", "Sharing data with third parties"),
            ("🚨", "Aggressive Recovery",        "HIGH",   "Threats of doorstep visits or calls"),
            ("📄", "Unclear Repayment",          "MEDIUM", "Lender can change terms anytime"),
        ]
        for icon, name, sev, desc in risks:
            sev_cls = {"HIGH": "sev-high", "MEDIUM": "sev-medium", "LOW": "sev-low"}[sev]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.8rem;padding:0.65rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">
              <span style="font-size:1.2rem;">{icon}</span>
              <div style="flex:1;"><span style="color:#e2e8f0;font-size:0.9rem;font-weight:600;">{name}</span>
              <br><span style="color:#64748b;font-size:0.78rem;">{desc}</span></div>
              <span class="severity-badge {sev_cls}">{sev}</span>
            </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""<div class="section-head"><h2>Why LoanGuard AI?</h2></div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);border-radius:20px;padding:1.4rem 1.5rem;">
          <p style="color:#cbd5e1;font-size:0.93rem;line-height:1.75;margin:0;">
            Millions of borrowers in India sign predatory loan agreements they don't fully understand.
            Hidden processing fees, aggressive recovery clauses, and variable interest rates trap borrowers
            in debt cycles.<br><br>
            <strong style="color:#f8fafc;">LoanGuard AI</strong> is the first line of defence —
            scanning agreements in seconds, surfacing what matters, and helping borrowers ask the right
            questions before they sign.<br><br>
            Built on rule-based NLP tuned for Indian lending practices and RBI Fair Practice guidelines.
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Start Analysis →", type="primary", use_container_width=True):
            _nav("agreement")
            st.rerun()

        st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)

        if st.button("⚡ Try with Sample Agreement", use_container_width=True):
            st.session_state.agreement_text = SAMPLE_AGREEMENT
            st.session_state.input_source   = "demo"
            st.session_state.analysis       = None
            st.session_state.page           = "agreement"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGREEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "agreement":
    st.markdown("""
    <div class="section-head">
      <h2>📄 Agreement Input</h2>
      <span class="badge">STEP 1 OF 4</span>
    </div>
    """, unsafe_allow_html=True)

    input_mode = st.radio(
        "Input method",
        ["📋 Paste Text", "📎 Upload PDF"],
        horizontal=True,
        label_visibility="collapsed",
    )

    agreement_text = st.session_state.agreement_text

    if input_mode == "📋 Paste Text":
        initial_val = agreement_text if st.session_state.input_source != "pdf" else ""
        pasted = st.text_area(
            "Paste your loan agreement text here",
            value=initial_val,
            height=340,
            placeholder=(
                "Paste the full loan agreement text here…\n\n"
                "Tip: Include all clauses — even fine print — for best detection.\n"
                "Or click '⚡ Load Sample Agreement' in the sidebar to test instantly."
            ),
        )
        if pasted != agreement_text:
            st.session_state.agreement_text = pasted
            st.session_state.input_source   = "paste"
            st.session_state.pdf_meta       = None
            agreement_text = pasted

        if agreement_text.strip():
            word_count = len(agreement_text.split())
            st.markdown(f"""
            <div class="banner-success">
              ✅ Agreement loaded — <strong>{word_count:,} words</strong> ready for analysis.
            </div>""", unsafe_allow_html=True)

    else:  # PDF upload
        uploaded = st.file_uploader(
            "Upload PDF agreement",
            type=["pdf"],
            help="Text-based PDFs work best. Scanned/image PDFs may not extract correctly.",
            label_visibility="collapsed",
        )

        if uploaded:
            sig = _pdf_sig(uploaded)
            if sig != st.session_state.last_pdf_sig:
                with st.spinner("📄 Extracting text from PDF…"):
                    result = process_pdf_upload(uploaded)
                st.session_state.last_pdf_sig = sig

                if result.success:
                    st.session_state.agreement_text = result.text
                    st.session_state.input_source   = "pdf"
                    st.session_state.pdf_meta       = {
                        "filename":  result.filename,
                        "pages":     result.page_count,
                        "chars":     result.char_count,
                        "words":     result.word_count,
                    }
                    st.session_state.analysis  = None
                    st.session_state.report    = ""
                    agreement_text = result.text
                else:
                    st.session_state.agreement_text = ""
                    st.session_state.pdf_meta       = None
                    agreement_text = ""
                    st.error(f"❌ {result.error}")

            meta = st.session_state.pdf_meta
            if meta and st.session_state.input_source == "pdf":
                st.markdown(f"""
                <div class="banner-success">
                  ✅ <strong>{html.escape(meta['filename'])}</strong> extracted —
                  {meta['pages']} pages · {meta['words']:,} words · {meta['chars']:,} characters
                </div>""", unsafe_allow_html=True)

                preview = agreement_text[:3000]
                if len(agreement_text) > 3000:
                    preview += "\n\n… [truncated — full text will be analyzed]"

                with st.expander("📖 Preview extracted text", expanded=False):
                    st.text_area("", value=preview, height=200, disabled=True, label_visibility="collapsed")

                agreement_text = st.session_state.agreement_text

        else:
            st.markdown("""
            <div class="empty-state">
              <span class="es-icon">📎</span>
              <h3>No PDF selected</h3>
              <p>Upload a loan agreement PDF above.<br>Text-based PDFs extract best. Scanned docs may fail.</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        analyze_clicked = st.button("🔍 Analyze Agreement", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("Clear", use_container_width=True):
            st.session_state.agreement_text = ""
            st.session_state.input_source   = ""
            st.session_state.pdf_meta       = None
            st.session_state.analysis       = None
            st.session_state.report         = ""
            st.session_state.last_pdf_sig   = ""
            st.rerun()

    if analyze_clicked:
        text = st.session_state.agreement_text.strip()
        if not text:
            st.warning("⚠️ Please paste text or upload a PDF first.")
        else:
            src = st.session_state.input_source or ("pdf" if input_mode == "📎 Upload PDF" else "paste")
            _run_analysis(text, src)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "analytics":
    analysis = st.session_state.analysis

    st.markdown("""
    <div class="section-head">
      <h2>📊 Risk Analytics</h2>
      <span class="badge">STEP 2 OF 4</span>
    </div>
    """, unsafe_allow_html=True)

    if analysis is None:
        st.markdown("""
        <div class="empty-state">
          <span class="es-icon">📊</span>
          <h3>No analysis yet</h3>
          <p>Go to the Agreement tab, load your agreement text, and click Analyze Agreement.</p>
        </div>""", unsafe_allow_html=True)

        if st.button("→ Go to Agreement Tab", type="primary"):
            _nav("agreement")
            st.rerun()
    else:
        src_label = {"pdf": "PDF upload", "paste": "Pasted text", "demo": "Sample agreement"}.get(
            st.session_state.input_source, "Agreement"
        )
        cat = analysis.category.lower()
        cat_disp = analysis.category

        # ── Score banner ──
        st.markdown(f"""
        <div class="score-banner {cat}">
          <div style="display:flex;align-items:flex-start;gap:2rem;flex-wrap:wrap;">
            <div>
              <p class="score-label">Loan Safety Score</p>
              <p class="score-big">{analysis.score}<span style="font-size:1.6rem;opacity:0.5;">/10</span></p>
              <span class="score-category {cat}">{SEV_ICON.get(cat,'⚪')} {cat_disp} RISK</span>
            </div>
            <div style="flex:1;min-width:220px;">
              <p style="color:#94a3b8;font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;margin:0 0 0.5rem;">Analysis Summary</p>
              <p class="score-summary">{html.escape(analysis.summary)}</p>
              <p style="color:#475569;font-size:0.78rem;margin-top:0.8rem;">Source: {src_label}</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Metric tiles ──
        risks_found = len(analysis.findings)
        trust = "High" if analysis.score >= 7 else "Moderate" if analysis.score >= 4 else "Low"
        high_cnt = sum(1 for f in analysis.findings if f.severity == "high")
        med_cnt  = sum(1 for f in analysis.findings if f.severity == "medium")

        st.markdown(f"""
        <div class="metric-grid">
          <div class="metric-tile" data-icon="🛡️">
            <p class="mt-label">Safety Score</p>
            <p class="mt-value">{analysis.score}<span style="font-size:1rem;opacity:0.5;">/10</span></p>
            <p class="mt-note">Higher = safer agreement</p>
          </div>
          <div class="metric-tile" data-icon="⚠️">
            <p class="mt-label">Risks Found</p>
            <p class="mt-value">{risks_found}</p>
            <p class="mt-note">{high_cnt} high · {med_cnt} medium</p>
          </div>
          <div class="metric-tile" data-icon="🤝">
            <p class="mt-label">Trust Level</p>
            <p class="mt-value">{trust}</p>
            <p class="mt-note">Lender trustworthiness signal</p>
          </div>
          <div class="metric-tile" data-icon="📋">
            <p class="mt-label">Risk Category</p>
            <p class="mt-value">{cat_disp}</p>
            <p class="mt-note">Overall agreement risk level</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Risk cards ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-head">
          <h2>Detected Risk Clauses</h2>
        </div>
        <p style="color:#64748b;font-size:0.88rem;margin:-0.5rem 0 1rem;">
          Each card shows the original clause, why it matters, and what to do.
        </p>
        """, unsafe_allow_html=True)

        if analysis.findings:
            for finding in analysis.findings:
                st.markdown(render_risk_card(finding), unsafe_allow_html=True)
                st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="banner-success">
              ✅ <strong>No risky clauses matched our checks.</strong>
              This agreement appears cleaner than most — but always have a lawyer review before signing.
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("→ Calculate True Cost", type="primary"):
            _nav("reports")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REPORTS (Cost Calculator + Report)
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "reports":
    st.markdown("""
    <div class="section-head">
      <h2>📥 Cost Calculator & Reports</h2>
      <span class="badge">STEPS 3 & 4</span>
    </div>
    """, unsafe_allow_html=True)

    # ── True Cost Calculator ──
    st.markdown("""
    <div class="calc-section">
      <div class="section-head" style="margin-bottom:1rem;">
        <h2>💰 True Cost Calculator</h2>
      </div>
      <p style="color:#64748b;font-size:0.88rem;margin:0 0 1.2rem;">
        Enter the three key loan amounts to expose hidden charges and the real cost of borrowing.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        promised = st.number_input("💬 Promised Amount (₹)", min_value=0.0, value=10000.0, step=500.0,
                                    help="The loan amount the lender said you would receive")
    with c2:
        received = st.number_input("✅ Actually Received (₹)", min_value=0.0, value=8500.0, step=500.0,
                                    help="The amount actually deposited to your account")
    with c3:
        repayment = st.number_input("📤 Total Repayment (₹)", min_value=0.0, value=15000.0, step=500.0,
                                     help="Total you must repay including all principal, interest, and fees")

    calc_clicked = st.button("🧮 Calculate True Cost", type="primary", use_container_width=True)

    if calc_clicked:
        st.session_state.cost_result  = calculate_true_cost(promised, received, repayment)
        st.session_state.show_report  = False
        st.session_state.report       = ""

    cost = st.session_state.cost_result
    if cost:
        hc_pct = round((cost.hidden_charges / promised * 100), 1) if promised > 0 else 0
        rec_color = "red" if cost.hidden_charges > 0 else "green"
        extra_color = "red" if cost.extra_repayment > received * 0.3 else "amber"
        eff_color = "red" if cost.effective_cost_pct > 40 else ("amber" if cost.effective_cost_pct > 20 else "green")

        st.markdown(f"""
        <div style="margin-top:1.2rem;">
          <div class="cost-grid">
            <div class="cost-tile">
              <p class="ct-label">💬 Promised Amount</p>
              <p class="ct-value">₹{cost.promised_amount:,.0f}</p>
            </div>
            <div class="cost-tile">
              <p class="ct-label">✅ Money Received</p>
              <p class="ct-value {rec_color}">₹{cost.received_amount:,.0f}</p>
            </div>
            <div class="cost-tile">
              <p class="ct-label">🕵️ Hidden Charges</p>
              <p class="ct-value red">₹{cost.hidden_charges:,.0f}
                <span style="font-size:1rem;opacity:0.6;">({hc_pct}%)</span>
              </p>
            </div>
            <div class="cost-tile">
              <p class="ct-label">📤 Extra Repayment</p>
              <p class="ct-value {extra_color}">₹{cost.extra_repayment:,.0f}</p>
            </div>
            <div class="cost-tile">
              <p class="ct-label">📊 Effective Cost</p>
              <p class="ct-value {eff_color}">{cost.effective_cost_pct}%</p>
            </div>
            <div class="cost-tile">
              <p class="ct-label">📤 Total Repayment</p>
              <p class="ct-value">₹{cost.total_repayment:,.0f}</p>
            </div>
          </div>
          <div class="cost-insight">
            💡 <strong>Cost Insight:</strong> {html.escape(cost.risk_message)}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Plain language summary
        st.markdown(f"""
        <div class="banner-warning" style="margin-top:0.8rem;">
          📢 <strong>In plain language:</strong>
          You were promised <strong>₹{cost.promised_amount:,.0f}</strong>,
          received <strong>₹{cost.received_amount:,.0f}</strong>,
          but must repay <strong>₹{cost.total_repayment:,.0f}</strong> —
          an effective extra cost of <strong>{cost.effective_cost_pct}%</strong> above what you actually got.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Report section ──
    st.markdown("""
    <div class="section-head" style="margin-top:1rem;">
      <h2>📄 Safety Report</h2>
      <span class="badge">STEP 4</span>
    </div>
    <p style="color:#64748b;font-size:0.88rem;margin:0 0 1.2rem;">
      Generate a complete downloadable safety report combining risk analysis and cost breakdown.
    </p>
    """, unsafe_allow_html=True)

    analysis = st.session_state.analysis

    if analysis is None:
        st.markdown("""
        <div class="empty-state">
          <span class="es-icon">📊</span>
          <h3>Analysis required first</h3>
          <p>Run the Agreement Analysis before generating a report.</p>
        </div>""", unsafe_allow_html=True)

        if st.button("→ Go to Agreement", type="primary"):
            _nav("agreement")
            st.rerun()
    else:
        col_gen, col_dl = st.columns([3, 1])
        with col_gen:
            gen_clicked = st.button("📄 Generate Safety Report", type="primary", use_container_width=True)
        with col_dl:
            if st.session_state.report:
                st.download_button(
                    label="⬇️ Download .md",
                    data=st.session_state.report,
                    file_name="loanguard_safety_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        if gen_clicked:
            with st.spinner("📝 Compiling your safety report…"):
                st.session_state.report = generate_safety_report(
                    analysis,
                    st.session_state.cost_result,
                    st.session_state.agreement_text,
                )
            st.session_state.show_report = True
            st.markdown('<div class="banner-success">✅ Report generated! Scroll down to preview or download.</div>', unsafe_allow_html=True)

        if st.session_state.report:
            with st.expander("📖 Preview Safety Report", expanded=st.session_state.show_report):
                st.markdown(f"""
                <div class="report-preview">{html.escape(st.session_state.report)}</div>
                """, unsafe_allow_html=True)
                st.download_button(
        label="📥 Download Safety Report",
        data=st.session_state.report,
        file_name="LoanGuard_AI_Report.md",
        mime="text/markdown",
        use_container_width=True
    )    