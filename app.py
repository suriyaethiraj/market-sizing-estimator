import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
from schema import MarketInput

st.set_page_config(
    page_title="Market Sizing Estimator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main,.stApp{background:#F8FAFC}
.metric-card{background:white;border-radius:12px;padding:1.25rem 1.5rem;
  border:1px solid #E2E8F0;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.05)}
.tam-val{font-size:2rem;font-weight:700;color:#1F3C6B}
.sam-val{font-size:2rem;font-weight:700;color:#4F46E5}
.som-val{font-size:2rem;font-weight:700;color:#16A34A}
.label{font-size:.8rem;color:#64748B;font-weight:600;margin-bottom:4px}
.range{font-size:.78rem;color:#94A3B8;margin-top:4px}
.narrative-box{background:#1F3C6B;color:white;border-radius:10px;
  padding:1rem 1.5rem;margin-bottom:1.25rem;font-size:.95rem;line-height:1.7}
.assumption-row{background:#F8FAFC;border-radius:6px;padding:.4rem .75rem;
  margin:.2rem 0;font-size:.85rem;border:1px solid #E2E8F0}
.method-tab{background:white;border-radius:10px;padding:1rem;border:1px solid #E2E8F0}
.stButton>button{background:linear-gradient(90deg,#1F3C6B,#4F46E5);
  color:white;border:none;border-radius:8px;font-weight:600}
h1,h2{color:#1F3C6B !important}
h2.app-title{color:white !important; margin: 0; font-weight: 700; line-height: 1.2;}
div.app-subtitle{color:white !important; font-size: 0.95rem; margin-top: 0.4rem;}
h3{color:#4F46E5 !important}
.conf-high{color:#16A34A;font-weight:700}
.conf-med{color:#D97706;font-weight:700}
.conf-low{color:#DC2626;font-weight:700}
</style>
""", unsafe_allow_html=True)

INDUSTRIES = [
    "SaaS / B2B Software", "E-Commerce / Retail", "FinTech / Payments",
    "HealthTech / Digital Health", "EdTech", "AdTech / MarTech",
    "IT Infrastructure / Cloud", "Cybersecurity", "HR Tech",
    "LegalTech", "PropTech / Real Estate", "Supply Chain / Logistics",
    "Consumer App / Social", "Gaming", "Clean Energy / ClimaTech",
    "Manufacturing / Industrial", "Agriculture Tech", "Travel & Hospitality",
    "Media & Entertainment", "Other",
]

GEOGRAPHIES = [
    "United States", "United Kingdom", "India", "Germany", "France",
    "Japan", "China", "Brazil", "Canada", "Australia", "Singapore",
    "UAE", "South Korea", "Indonesia", "Mexico", "Global",
    "Europe", "Southeast Asia", "Latin America", "Africa",
]

PRICING_MODELS = [
    "SaaS / Subscription (per user/month)",
    "SaaS / Subscription (per seat/year)",
    "Transactional / Usage-based",
    "Marketplace (% of GMV)",
    "Freemium (conversion to paid)",
    "Hardware + Software",
    "Professional Services",
    "Advertising / CPM",
]

st.markdown("""
<div style="background: linear-gradient(90deg, #1F3C6B, #4F46E5); padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
    <h2 class="app-title">Market Sizing Estimator</h2>
    <div class="app-subtitle">AI-powered TAM/SAM/SOM analysis using top-down, bottom-up, and value-theory methodologies — grounded in World Bank data.</div>
</div>
""", unsafe_allow_html=True)


st.markdown("---")

# ── API Settings (Horizontal Top Panel) ───────────────────────────────────────
api_c1, api_c2 = st.columns(2)
with api_c1:
    provider = st.selectbox("AI Provider *", ["Mock Data", "Anthropic", "OpenAI", "Gemini", "Groq"])
with api_c2:
    api_key = st.text_input(f"{provider} API Key *" if provider != "Mock Data" else "API Key not required for Mock Data", type="password",
                            help=f"Enter your {provider} API key here.",
                            disabled=(provider == "Mock Data"))

st.markdown("---")

# ── Input Form ────────────────────────────────────────────────────────────────
with st.form("sizing_form"):
    # --- 1. Product / Industry Definition ---
    st.subheader("Define Your Market", anchor=False)

    product = st.text_area(
        "Product / Solution Description *",
        placeholder="e.g. AI-powered project management platform for remote engineering teams. Automates sprint planning, standup summaries, and dependency tracking.",
        height=90
    )

    c1, c2 = st.columns(2)
    with c1:
        industry  = c1.selectbox("Industry Vertical *", INDUSTRIES)
        stage     = c1.selectbox("Company Stage *", ["Startup (Pre-PMF)", "Startup (Post-PMF)", "SMB", "Mid-Market", "Enterprise"])
        geo_sel   = c1.multiselect("Geographies *", GEOGRAPHIES,
                                    default=["United States"],
                                    help="Select all markets you want to size")
    with c2:
        persona       = c2.text_input("Target Persona *",
                                       placeholder="e.g. Engineering Managers at Series A-C startups with 10-50 engineers")
        pricing_model = c2.selectbox("Pricing Model *", PRICING_MODELS)
        pc1, pc2      = c2.columns(2)
        avg_price     = pc1.number_input("Avg Price ($) *", min_value=1.0, value=500.0, step=50.0)
        price_unit    = pc2.text_input("Per", value="user/month",
                                       placeholder="user/month, seat/year, transaction…")

    custom_research = st.text_area(
        "Paste your own research / data (optional)",
        placeholder="Paste any industry reports, analyst estimates, competitor revenue figures, survey data, or your own assumptions here. The AI will incorporate them into the analysis.",
        height=100
    )

    submitted = st.form_submit_button("Run Analysis", use_container_width=True)

# ── Generation ────────────────────────────────────────────────────────────────
if submitted:
    errors = []
    if not api_key and provider != "Mock Data": errors.append(f"{provider} API Key is required.")
    if not product.strip(): errors.append("Product description is required.")
    if not geo_sel:         errors.append("Select at least one geography.")
    if not persona.strip(): errors.append("Target persona is required.")

    if errors:
        for e in errors: st.error(e)
    else:
        inp = MarketInput(
            product_description=product,
            industry_vertical=industry,
            geographies=geo_sel,
            company_stage=stage,
            target_persona=persona,
            pricing_model=pricing_model,
            avg_price=avg_price,
            price_unit=price_unit,
            custom_research=custom_research or None,
        )

        with st.spinner("🌐 Fetching World Bank data..."):
            try:
                from worldbank import fetch_market_data
                fetch_market_data(geo_sel)  # warm up
            except Exception:
                pass

        try:
            with st.spinner(f"🧠 {provider} is sizing your market across 3 methodologies..."):
                from analyzer import generate_market_sizing
                report = generate_market_sizing(inp, api_key, provider)
                st.session_state["report"] = report
                st.session_state["provider"] = provider
                st.session_state["inp"] = inp
            st.success("✅ Market sizing complete!")
            st.switch_page("pages/1_reports.py")
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()
