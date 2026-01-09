import streamlit as st
import altair as alt
import pandas as pd
import os
import json
import pickle
from ml.pipeline import MLPipeline
from rules.engine import RuleEngine, AuditLogger
from datetime import datetime

# Page config
st.set_page_config(
    page_title="DCA-ControlOS Dashboard", 
    layout="wide",
    menu_items={}
)

# Hide Streamlit UI elements for a neutral internal dashboard look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize Backend
@st.cache_resource
def init_backend():
    pipeline = MLPipeline()
    if not os.path.exists("ml/recovery_model.pkl"):
        pipeline.train()
    
    # Load models
    with open("ml/recovery_model.pkl", "rb") as f:
        pipeline.recovery_model = pickle.load(f)
    with open("ml/sla_risk_model.pkl", "rb") as f:
        pipeline.sla_risk_model = pickle.load(f)
    with open("ml/le_tier.pkl", "rb") as f:
        pipeline.le_tier = pickle.load(f)
        
    rule_engine = RuleEngine()
    audit_logger = AuditLogger()
    return pipeline, rule_engine, audit_logger

pipeline, rule_engine, audit_logger = init_backend()

# Sidebar
st.sidebar.title("🎛️ Control Panel")
user_role = st.sidebar.selectbox("User Role", ["FedEx Admin", "DCA Agent", "Auditor"])
st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: **{user_role}**")

# Main Header
st.title("🛡️ DCA-ControlOS")
st.subheader("Regulation-First AI Governance Platform")
st.caption("Designed to enforce SLA contracts, predict compliance risk, and provide audit-ready oversight over external DCAs.")

# Load Data
df = pd.read_csv("data/cases.csv")
df['customer_tier_encoded'] = pipeline.le_tier.transform(df['customer_tier'])

# Run Inference
rec_probs, sla_risks = pipeline.predict(df)
df['Recovery Prob %'] = (rec_probs * 100).round(2)
df['SLA Risk %'] = (sla_risks * 100).round(2)

# Run Rule Validation
breached = []
escalated = []
messages = []

for _, row in df.iterrows():
    res = rule_engine.validate_case(row)
    breached.append(res['is_breached'])
    escalated.append(res['escalate'])
    messages.append(res['message'])

df['Breached'] = breached
df['Escalated'] = escalated
df['Status Message'] = messages

# Derived Governance Status
def get_sla_status(row):
    if row['Breached']: return "🔴 Breached"
    if row['SLA Risk %'] > 50: return "🟡 At Risk"
    return "🟢 OK"

df['SLA Status'] = df.apply(get_sla_status, axis=1)

# Dashboard KPIs
cols = st.columns(4)
cols[0].metric("Total Cases", len(df))
cols[1].metric(
    "At Risk (SLA)", 
    len(df[df['SLA Risk %'] > 50]),
    help="Cases predicted to breach SLA within the regulatory window"
)
cols[2].metric(
    "Critical Breaches", 
    len(df[df['Escalated'] == True]), 
    delta_color="inverse",
    help="Confirmed SLA violations triggering escalation"
)
cols[3].metric(
    "Avg Recovery Prob", 
    f"{df['Recovery Prob %'].mean():.1f}%",
    help="Model-estimated recovery likelihood across active cases"
)

# Main Interface
tab1, tab2, tab3 = st.tabs(["📋 Case Assignments", "🔎 Audit Trail", "🧠 ML Models & Risk"])

with tab1:
    st.markdown("### Active Inventory")
    
    # Filtering for DCA Agent role
    if user_role == "DCA Agent":
        dca_list = df['dca_id'].unique()
        selected_dca = st.selectbox("Select Your Agency", dca_list)
        display_df = df[df['dca_id'] == selected_dca]
    else:
        display_df = df

    # Search
    search = st.text_input("Search Case ID or DCA", "")
    if search:
        display_df = display_df[display_df['case_id'].astype(str).str.contains(search) | display_df['dca_id'].str.contains(search)]

    # Highlight rows based on SLA Status
    def style_rows(row):
        if "Breached" in row['SLA Status']:
            return ['background-color: rgba(255, 75, 75, 0.2)'] * len(row)
        elif "At Risk" in row['SLA Status']:
            return ['background-color: rgba(255, 165, 0, 0.2)'] * len(row)
        return [''] * len(row)

    st.dataframe(display_df.style.apply(style_rows, axis=1), use_container_width=True)

    if user_role != "Auditor":
        st.markdown("---")
        st.markdown("### Update Case Status")
        c1, c2, c3 = st.columns(3)
        with c1:
            case_to_upd = st.selectbox("Case ID", display_df['case_id'])
        with c2:
            new_status = st.selectbox("New Status", ["In Progress", "Recovered", "Disputed", "Closed"])
        with c3:
            if st.button("Update Status"):
                # Logging the action
                audit_logger.log(user_role, "STATUS_UPDATE", int(case_to_upd), {"new_status": new_status})
                st.success(f"Case {case_to_upd} updated to {new_status}. Action logged to immutable ledger.")

with tab2:
    st.markdown("### ⛓️ Immutable Audit Ledger")
    st.info("Each record is hash-linked to the previous entry. Any modification breaks the chain.")
    try:
        with open("data/audit_log.json", "r") as f:
            logs = json.load(f)
        if logs:
            log_df = pd.DataFrame(logs)
            st.table(log_df[['timestamp', 'actor', 'action', 'case_id', 'hash']])
        else:
            st.info("No logs yet.")
    except Exception as e:
        st.error(f"Error loading logs: {e}")

with tab3:
    st.markdown("### 🧠 Predictive Insights")
    st.markdown("Prioritization matrix: High recovery potential vs. compliance risk.")
    
    # Create the base scatter plot using Altair for custom quadrant overlay
    base = alt.Chart(df).mark_circle(size=120, opacity=0.8).encode(
        x=alt.X('SLA Risk %', scale=alt.Scale(domain=[0, 100]), title="Compliance Risk (%)"),
        y=alt.Y('Recovery Prob %', scale=alt.Scale(domain=[0, 100]), title="Recovery Probability (%)"),
        color=alt.Color('Escalated', scale=alt.Scale(domain=[True, False], range=['#ff4b4b', '#1f77b4']), legend=alt.Legend(title="Escalated")),
        tooltip=['case_id', 'amount_due', 'dca_id', 'SLA Risk %', 'Recovery Prob %']
    ).properties(height=500)

    # Vertical quadrant line (at 50% Compliance Risk)
    v_line = alt.Chart(pd.DataFrame({'x': [50]})).mark_rule(color='gray', strokeDash=[4, 4], opacity=0.7).encode(x='x')
    
    # Horizontal quadrant line (at 50% Recovery Probability)
    h_line = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(color='gray', strokeDash=[4, 4], opacity=0.7).encode(y='y')
    
    # Label for Top-Right Quadrant
    quadrant_label = alt.Chart(pd.DataFrame({
        'x': [75], 
        'y': [95], 
        'text': ['Immediate Governance Attention']
    })).mark_text(
        align='center', 
        fontSize=14, 
        fontWeight='bold', 
        color='#ff4b4b'
    ).encode(x='x', y='y', text='text')

    st.altair_chart((base + v_line + h_line + quadrant_label).interactive(), use_container_width=True)
    
    st.markdown("""
    - **Recovery Prob**: Predicts how likely we are to recover the funds based on amount and age.
    - **SLA Risk**: Predicts the likelihood of an agency missing the regulatory window.
    """)

st.markdown("---")
st.caption("DCA-ControlOS v1.0 — Hackathon Prototype | Built to demonstrate enforceable governance, not UI polish")
