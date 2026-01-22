import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Market Sizing Estimator - Reports",
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

/* Segmented Control / Pill Tabs Design */
.stTabs [data-baseweb="tab-list"] {
    background-color: #F1F5F9;
    border-radius: 12px;
    padding: 6px;
    display: flex;
    width: 100%;
    gap: 8px;
    border: 1px solid #E2E8F0;
    margin-bottom: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    flex: 1;
    display: flex;
    justify-content: center;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    background-color: transparent !important;
    border: none !important;
    color: #64748B !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    margin: 0 !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #334155 !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: white !important;
    color: #0F172A !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
    font-weight: 600 !important;
}
/* Hide the default bottom highlight border */
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Plotly Chart Card Styling */
.stPlotlyChart {
    background-color: white;
    border-radius: 16px !important;
    padding: 1.2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid #E2E8F0;
    margin-top: 0.5rem;
}
.stPlotlyChart iframe {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


if "report" not in st.session_state:
    from schema import MarketSizingReport
    dummy_data = {
        "title": "TAM/SAM/SOM Analysis: Executive Overview",
        "product_description": "AI-powered project management platform for remote engineering teams.",
        "industry": "SaaS / B2B Software",
        "geographies": ["United States", "United Kingdom", "Canada"],
        "methodology_results": [
            {
                "methodology": "Top-Down",
                "tam": {"low": 12000, "mid": 15000, "high": 18000, "unit": "USD Millions"},
                "sam": {"low": 2000, "mid": 2500, "high": 3000, "unit": "USD Millions"},
                "som": {"low": 150, "mid": 250, "high": 350, "unit": "USD Millions"},
                "key_assumptions": [
                    {"label": "Global PM Software Market Size", "value": "$15B", "source": "Gartner", "confidence": "High"},
                    {"label": "Target Geography Share", "value": "40%", "source": "World Bank", "confidence": "Medium"},
                    {"label": "Remote Team Penetration", "value": "25%", "source": "Industry Average", "confidence": "Medium"}
                ],
                "narrative": "Using a top-down approach, we start with the global project management software market ($15B). Filtering for US, UK, and Canada (40% of global GDP) yields a $6B regional market. Focusing specifically on software catering to remote engineering teams (25% penetration) gives a SAM of $2.5B. We estimate capturing 10% of this segment over 3 years, resulting in a SOM of $250M."
            },
            {
                "methodology": "Bottom-Up",
                "tam": {"low": 13000, "mid": 14500, "high": 16000, "unit": "USD Millions"},
                "sam": {"low": 2200, "mid": 2400, "high": 2800, "unit": "USD Millions"},
                "som": {"low": 180, "mid": 240, "high": 300, "unit": "USD Millions"},
                "key_assumptions": [
                    {"label": "Total Target Companies", "value": "150,000", "source": "Census Data", "confidence": "High"},
                    {"label": "Average ACV", "value": "$16,000", "source": "Competitor Pricing", "confidence": "High"},
                    {"label": "Adoption Rate", "value": "10%", "source": "Market Survey", "confidence": "Low"}
                ],
                "narrative": "Bottom-up analysis identifies 150,000 tech companies in the target geographies. At an Average Contract Value (ACV) of $16k/year, the TAM is $14.5B. Filtering for companies with fully remote engineering teams (approx. 16.5%) gives a SAM of 24,750 companies ($2.4B). Assuming a conservative 10% market share capture over 3 years yields a SOM of $240M."
            },
            {
                "methodology": "Value-Theory",
                "tam": {"low": 11000, "mid": 16000, "high": 20000, "unit": "USD Millions"},
                "sam": {"low": 1800, "mid": 2600, "high": 3200, "unit": "USD Millions"},
                "som": {"low": 140, "mid": 260, "high": 380, "unit": "USD Millions"},
                "key_assumptions": [
                    {"label": "Engineering Hours Saved/Week", "value": "4 hours", "source": "Beta Testing", "confidence": "Medium"},
                    {"label": "Average Hourly Rate", "value": "$75", "source": "Salary Data", "confidence": "High"},
                    {"label": "Willingness to Pay (WTP)", "value": "15% of value", "source": "Pricing Research", "confidence": "Low"}
                ],
                "narrative": "Based on beta tests, the platform saves an average of 4 hours per engineer per week. At $75/hr, this generates $15,000 of value per engineer annually. Assuming a 15% willingness to pay, the software is worth $2,250 per seat. Across 1.1M remote engineers in target geos, the total value SAM is $2.6B. At 10% capture, the SOM is $260M."
            }
        ],
        "reconciled_tam": {"low": 12000, "mid": 15000, "high": 18000, "unit": "USD Millions"},
        "reconciled_sam": {"low": 2000, "mid": 2500, "high": 3000, "unit": "USD Millions"},
        "reconciled_som": {"low": 160, "mid": 250, "high": 340, "unit": "USD Millions"},
        "five_year_projection": [
            {"year": 2024, "tam": 15000, "sam": 2500, "som": 0, "cagr_applied": 0.10},
            {"year": 2025, "tam": 16500, "sam": 2800, "som": 50, "cagr_applied": 0.10},
            {"year": 2026, "tam": 18150, "sam": 3130, "som": 120, "cagr_applied": 0.10},
            {"year": 2027, "tam": 19960, "sam": 3500, "som": 200, "cagr_applied": 0.10},
            {"year": 2028, "tam": 21950, "sam": 3920, "som": 310, "cagr_applied": 0.10}
        ],
        "sensitivity_axes": [
            {"variable": "ACV Pricing", "values": ["$12k", "$16k", "$20k"], "som_impacts": [190, 250, 310]},
            {"variable": "Remote Work Trends", "values": ["20%", "25%", "30%"], "som_impacts": [200, 250, 300]}
        ],
        "world_bank_data_used": ["GDP (current US$)", "Labor force, total"],
        "executive_summary": "The market for an AI-powered project management platform catering specifically to remote engineering teams in the US, UK, and Canada is robust. Across all three methodologies, the SAM centers reliably around $2.5B. The product demonstrates strong value-creation by saving engineering hours, supporting an ACV that aligns perfectly with the bottom-up estimates.",
        "investor_narrative": "This product targets a highly lucrative, fast-growing niche. While the overall PM software market is crowded, the specific focus on AI-driven workflows for remote engineers commands a premium. A conservative 10% capture of the $2.5B SAM yields a highly investable $250M SOM over 3-5 years. The biggest risk is ACV compression from incumbent bundles, but the unique AI efficiency gains provide a strong defensive moat.",
        "confidence_rating": "Medium",
        "key_risks": ["Incumbent bundling (Atlassian, Asana) driving down WTP", "Return-to-office trends shrinking the remote SAM", "AI commoditization reducing the product's unique value prop"],
        "generated_at": "2024-05-12T10:30:00Z"
    }
    st.session_state["report"] = MarketSizingReport(**dummy_data)
    st.session_state["provider"] = "Mock Data"

if "report" in st.session_state:
    from exporters import export_json, export_pdf, export_excel, export_pptx
    rpt = st.session_state["report"]
    provider = st.session_state.get("provider", "Mock Data")

    def _fmt(v):
        if v >= 1_000_000: return f"${v/1_000_000:.1f}T"
        if v >= 1_000:     return f"${v/1_000:.1f}B"
        return f"${v:.0f}M"

    st.subheader(rpt.title if provider != "Mock Data" else "TAM / SAM / SOM Analysis Overview")

    # Investor narrative
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); overflow: hidden; font-family: 'Inter', system-ui, sans-serif; border: 1px solid #F1F5F9; margin: 1.5rem 0;">
      <div style="background: #FFF1E5; padding: 1.5rem; border-radius: 12px; margin: 8px;">
        <h3 style="margin: 0 0 1rem 0; font-size: 1.3rem; color: #1E293B; font-weight: 600;">Investor Narrative</h3>
        <div style="font-size: 1.05rem; line-height: 1.6; color: #475569;">
          {rpt.investor_narrative}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Confidence Box
    conf_colors = {
        "High": {"border": "#22C55E", "text": "#16A34A"},
        "Medium": {"border": "#F59E0B", "text": "#D97706"},
        "Low": {"border": "#EF4444", "text": "#DC2626"}
    }
    c_style = conf_colors.get(rpt.confidence_rating, conf_colors["Medium"])
    
    st.markdown(f"""
    <div style='display:inline-block; padding:0.4rem 1rem; border-radius:8px; 
                background-color:#FFFFFF; border:1px solid {c_style["border"]}; 
                color:#000000; font-size:0.9rem; font-weight:700; margin-bottom: 1.5rem;'>
        Overall Confidence: <span style='color:{c_style["text"]}'>{rpt.confidence_rating}</span>
    </div>
    """, unsafe_allow_html=True)

    # KPI cards
    k1, k2, k3 = st.columns(3)
    
    card_styles = [
        {"col": k1, "title": "Total Addressable Market", "abbr": "TAM", "val": rpt.reconciled_tam, "top_bg": "#E5F4FA", "pill_bg": "#D0ECF9"},
        {"col": k2, "title": "Serviceable Addressable", "abbr": "SAM", "val": rpt.reconciled_sam, "top_bg": "#E7E2F7", "pill_bg": "#D8CFF5"},
        {"col": k3, "title": "Serviceable Obtainable", "abbr": "SOM", "val": rpt.reconciled_som, "top_bg": "#DEF7E8", "pill_bg": "#C4F1D6"}
    ]
    
    for c in card_styles:
        c["col"].markdown(f"""
        <div style="background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); overflow: hidden; font-family: 'Inter', system-ui, sans-serif; border: 1px solid #F1F5F9;">
          <div style="background: {c['top_bg']}; padding: 1.5rem; border-radius: 12px; margin: 8px;">
            <h3 style="margin: 0; font-size: 1.3rem; color: #1E293B; font-weight: 600;">{c['title']}</h3>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.9rem; color: #475569;">({c['abbr']})</p>
            <div style="margin-top: 1rem; font-size: 2.2rem; font-weight: 700; color: #0F172A; letter-spacing: -0.5px;">
              {_fmt(c['val'].mid)}
            </div>
            <div style="margin-top: 1.2rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <span style="background: {c['pill_bg']}; color: #334155; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">Low: {_fmt(c['val'].low)}</span>
              <span style="background: {c['pill_bg']}; color: #334155; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">High: {_fmt(c['val'].high)}</span>
            </div>
          </div>
          <div style="padding: 0.8rem 1.5rem 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; background: white;">
            <span style="font-weight: 600; font-size: 1rem; color: #0F172A;">Explore</span>
            <div style="background: #F1F5F9; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #334155;">
              →
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_overview, tab_methods, tab_proj, tab_sensitivity, tab_risks, tab_sources = st.tabs([
        "Overview", "Methodologies", "5-Year Projection",
        "Sensitivity", "Risks", "Sources"
    ])

    # ── Overview ──────────────────────────────────────────────────────────────
    with tab_overview:
        st.markdown(f"**{rpt.executive_summary}**" if len(rpt.executive_summary)<200 else rpt.executive_summary)

        # Layered Streamgraph Funnel (High -> Mid -> Low)
        fig = go.Figure()
        
        # Add empty start and end points for curved/tapered edges
        x_cats = [" ", "TAM", "SAM", "SOM", "  "]
        
        # Select dynamic color palette based on report
        palettes = [
            ["#FFEDD5", "#FB923C", "#EA580C"], # Orange
            ["#E0E7FF", "#818CF8", "#4F46E5"], # Indigo
            ["#F3E8FF", "#C084FC", "#9333EA"], # Purple
            ["#D1FAE5", "#34D399", "#059669"], # Emerald
            ["#FCE7F3", "#F472B6", "#DB2777"]  # Rose
        ]
        color_idx = hash(rpt.product_description) % len(palettes)
        palette = palettes[color_idx]
        
        # Scenarios from outer (High) to inner (Low) padded with zeros for the curved ends
        scenarios = [
            ("High Scenario", [0, rpt.reconciled_tam.high, rpt.reconciled_sam.high, rpt.reconciled_som.high, 0], palette[0]),
            ("Mid Scenario", [0, rpt.reconciled_tam.mid, rpt.reconciled_sam.mid, rpt.reconciled_som.mid, 0], palette[1]),
            ("Low Scenario", [0, rpt.reconciled_tam.low, rpt.reconciled_sam.low, rpt.reconciled_som.low, 0], palette[2])
        ]
        
        for name, vals, color in scenarios:
            v_half = [v / 2 for v in vals]
            v_neg_half = [-v / 2 for v in vals]
            
            # Bottom bound (transparent)
            fig.add_trace(go.Scatter(
                x=x_cats, y=v_neg_half, mode='lines',
                line=dict(width=0, shape='spline', smoothing=0.6),
                showlegend=False, hoverinfo='skip'
            ))
            
            # Top bound with fill to bottom
            fig.add_trace(go.Scatter(
                x=x_cats, y=v_half, name=name, mode='lines',
                line=dict(width=0, shape='spline', smoothing=0.6),
                fill='tonexty', fillcolor=color,
                hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{customdata}}<extra></extra>",
                customdata=[_fmt(v) for v in vals]
            ))
            
        # Add vertical slice lines and floating annotations
        v_high = scenarios[0][1]
        v_low = scenarios[2][1]
        
        # Indices 1, 2, 3 correspond to TAM, SAM, SOM
        for i in range(1, 4):
            # Vertical line spanning the height of the high scenario
            fig.add_shape(
                type="line", x0=x_cats[i], x1=x_cats[i],
                y0=-v_high[i]/2, y1=v_high[i]/2,
                line=dict(color="rgba(255,255,255,0.8)", width=2)
            )
            # Label ABOVE the funnel (High value)
            fig.add_annotation(
                x=x_cats[i], y=v_high[i]/2,
                text=f"<span style='font-family: monospace; font-size: 13px; color: #475569;'>{_fmt(v_high[i])}</span>",
                showarrow=False, yshift=20,
                bgcolor="rgba(255,255,255,0.7)", borderpad=4
            )
            # Label BELOW the funnel (Low value)
            fig.add_annotation(
                x=x_cats[i], y=-v_high[i]/2,
                text=f"<span style='font-family: monospace; font-size: 13px; color: #475569;'>{_fmt(v_low[i])}</span>",
                showarrow=False, yshift=-20,
                bgcolor="rgba(255,255,255,0.7)", borderpad=4
            )

        fig.update_layout(
            title="Market Funnel — Scenario Ranges",
            height=400, plot_bgcolor="white", paper_bgcolor="white",
            font={"family":"system-ui","color":"#1E293B"},
            margin=dict(l=20, r=20, t=90, b=40),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            showlegend=True, legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Low/Mid/High scenario bar (Dark Theme Neon)
        cats = ["TAM", "SAM", "SOM"]
        high_vals = [rpt.reconciled_tam.high, rpt.reconciled_sam.high, rpt.reconciled_som.high]
        mid_vals = [rpt.reconciled_tam.mid, rpt.reconciled_sam.mid, rpt.reconciled_som.mid]
        low_vals = [rpt.reconciled_tam.low, rpt.reconciled_sam.low, rpt.reconciled_som.low]

        fig2 = go.Figure()
        
        # High Scenario (Neon Lime)
        fig2.add_trace(go.Bar(
            name='High Scenario', x=cats, y=high_vals,
            marker_color="#D4F234",
            text=[_fmt(v) for v in high_vals], textposition="auto",
            textfont=dict(color="#18181B", weight="bold")
        ))
        
        # Mid Scenario (Emerald/Lime)
        fig2.add_trace(go.Bar(
            name='Mid Scenario', x=cats, y=mid_vals,
            marker_color="#84CC16",
            text=[_fmt(v) for v in mid_vals], textposition="auto",
            textfont=dict(color="#18181B", weight="bold")
        ))
        
        # Low Scenario (Dark Slate)
        fig2.add_trace(go.Bar(
            name='Low Scenario', x=cats, y=low_vals,
            marker_color="#334155",
            text=[_fmt(v) for v in low_vals], textposition="auto",
            textfont=dict(color="#F8FAFC")
        ))

        fig2.update_layout(
            barmode='group',
            title=dict(text="Scenario Analysis (Low / Mid / High)", font=dict(color="#1E293B", size=18)),
            height=400,
            plot_bgcolor="white", paper_bgcolor="white",
            font={"family":"system-ui","color":"#64748B"},
            yaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False, title=""),
            xaxis=dict(showgrid=False, zeroline=False),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(color="#1E293B")),
            margin=dict(l=20, r=20, t=60, b=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Methodologies ─────────────────────────────────────────────────────────
    with tab_methods:
        for mr in rpt.methodology_results:
            st.subheader(f"🔬 {mr.methodology} Approach")
            st.markdown(mr.narrative)
            m1,m2,m3 = st.columns(3)
            for col,lbl,sc in [(m1,"TAM",mr.tam),(m2,"SAM",mr.sam),(m3,"SOM",mr.som)]:
                col.metric(lbl, _fmt(sc.mid), delta=f"High: {_fmt(sc.high)}")

            if mr.key_assumptions:
                st.markdown("**Key Assumptions**")
                for a in mr.key_assumptions:
                    conf_color = {"High":"#16A34A","Medium":"#D97706","Low":"#DC2626"}.get(a.confidence,"#64748B")
                    st.markdown(f"""
                    <div class='assumption-row'>
                      <strong>{a.label}:</strong> {a.value}
                      &nbsp;·&nbsp; <span style='color:#64748B'>Source: {a.source}</span>
                      &nbsp;·&nbsp; <span style='color:{conf_color};font-weight:600'>{a.confidence} confidence</span>
                    </div>""", unsafe_allow_html=True)
            st.markdown("---")

        # Method comparison bar
        method_names = [mr.methodology for mr in rpt.methodology_results]
        fig3 = go.Figure()
        for metric,color,vals in [
            ("TAM","#1F3C6B",[mr.tam.mid for mr in rpt.methodology_results]),
            ("SAM","#4F46E5",[mr.sam.mid for mr in rpt.methodology_results]),
            ("SOM","#16A34A",[mr.som.mid for mr in rpt.methodology_results]),
        ]:
            fig3.add_trace(go.Bar(name=metric, x=method_names, y=vals,
                                  marker_color=color,
                                  text=[_fmt(v) for v in vals], textposition="outside"))
        fig3.update_layout(barmode="group", title="Methodology Comparison",
                           height=400, plot_bgcolor="white", paper_bgcolor="white",
                           font={"family":"system-ui"}, yaxis_title="USD Millions")
        st.plotly_chart(fig3, use_container_width=True)

    # ── 5-Year Projection ─────────────────────────────────────────────────────
    with tab_proj:
        years = [p.year for p in rpt.five_year_projection]
        fig4  = go.Figure()
        for metric,color,vals in [
            ("TAM","#1F3C6B",[p.tam for p in rpt.five_year_projection]),
            ("SAM","#4F46E5",[p.sam for p in rpt.five_year_projection]),
            ("SOM","#16A34A",[p.som for p in rpt.five_year_projection]),
        ]:
            fig4.add_trace(go.Scatter(x=years, y=vals, name=metric,
                                      mode="lines+markers+text",
                                      line={"color":color,"width":3},
                                      marker={"size":8},
                                      text=[_fmt(v) for v in vals],
                                      textposition="top center"))
        fig4.update_layout(title="5-Year Market Size Projection",
                           height=450, plot_bgcolor="white", paper_bgcolor="white",
                           font={"family":"system-ui"}, yaxis_title="USD Millions",
                           legend={"orientation":"h","y":-0.15})
        st.plotly_chart(fig4, use_container_width=True)

        # Table
        import pandas as pd
        df = pd.DataFrame([{
            "Year": p.year, "TAM": _fmt(p.tam), "SAM": _fmt(p.sam),
            "SOM": _fmt(p.som), "CAGR": f"{p.cagr_applied:.1f}%"
        } for p in rpt.five_year_projection])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Sensitivity ───────────────────────────────────────────────────────────
    with tab_sensitivity:
        st.markdown("Adjust key assumptions to see how SOM changes.")
        for axis in rpt.sensitivity_axes:
            st.subheader(axis.variable)
            fig5 = go.Figure(go.Bar(
                x=axis.values,
                y=axis.som_impacts,
                marker_color=["#DC2626" if v == min(axis.som_impacts)
                              else "#16A34A" if v == max(axis.som_impacts)
                              else "#4F46E5" for v in axis.som_impacts],
                text=[_fmt(v) for v in axis.som_impacts],
                textposition="outside"
            ))
            fig5.update_layout(height=300, plot_bgcolor="white", paper_bgcolor="white",
                               font={"family":"system-ui"}, yaxis_title="SOM (USD Millions)")
            st.plotly_chart(fig5, use_container_width=True)

    # ── Risks ─────────────────────────────────────────────────────────────────
    with tab_risks:
        st.subheader("⚠️ Key Risks & Sizing Limitations")
        for i, risk in enumerate(rpt.key_risks, 1):
            st.markdown(f"""
            <div style='background:white;border-left:4px solid #D97706;padding:.75rem 1rem;
              border-radius:0 8px 8px 0;margin:.5rem 0;font-size:.9rem;border:1px solid #E2E8F0'>
              <strong>Risk {i}:</strong> {risk}
            </div>""", unsafe_allow_html=True)

    # ── Sources ───────────────────────────────────────────────────────────────
    with tab_sources:
        st.subheader("📚 Data Sources & Citations")
        if rpt.world_bank_data_used:
            st.markdown("**World Bank Data Used:**")
            for src in rpt.world_bank_data_used:
                st.markdown(f"• {src}")
        st.markdown("\n**Additional Sources:**")
        
        # safely access provider and inp
        provider = st.session_state.get("provider", "AI Provider")
        st.markdown(f"• {provider} — industry knowledge and AI-estimated parameters")
        
        inp = st.session_state.get("inp", None)
        if inp and inp.custom_research:
            st.markdown("• User-provided research and data")

    # ── Exports ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Export", anchor=False)
    
    st.markdown("""
    <div id="export-marker"></div>
    <style>
    /* Turn the export buttons columns into a Pill Segmented Control */
    [data-testid="stVerticalBlock"] > div:has(#export-marker) ~ div [data-testid="stHorizontalBlock"] {
        background-color: #F1F5F9;
        border-radius: 12px;
        padding: 6px;
        border: 1px solid #E2E8F0;
        gap: 8px !important;
    }
    /* Inactive Format Tabs */
    [data-testid="stVerticalBlock"] > div:has(#export-marker) ~ div [data-testid="stHorizontalBlock"] button {
        background: transparent !important;
        border: none !important;
        color: #64748B !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    /* Hover state for Format Tabs */
    [data-testid="stVerticalBlock"] > div:has(#export-marker) ~ div [data-testid="stHorizontalBlock"] button:hover {
        background: white !important;
        color: #0F172A !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
    }
    /* Active Format Tab (styled via primary kind) */
    [data-testid="stVerticalBlock"] > div:has(#export-marker) ~ div [data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: white !important;
        color: #0F172A !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
        font-weight: 600 !important;
    }
    /* Download Button (5th tab) styled distinctively */
    [data-testid="stVerticalBlock"] > div:has(#export-marker) ~ div [data-testid="stHorizontalBlock"] a[download] button {
        background: linear-gradient(90deg,#1F3C6B,#4F46E5) !important;
        color: white !important;
        font-weight: 600 !important;
        margin-top: 0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    e1, e2, e3, e4 = st.columns(4)

    if e1.button("JSON", use_container_width=True, type="primary" if st.session_state.get("export_active") == "JSON" else "secondary"):
        st.session_state.export_active = "JSON"
        st.rerun()
    if e2.button("Excel", use_container_width=True, type="primary" if st.session_state.get("export_active") == "Excel" else "secondary"):
        st.session_state.export_active = "Excel"
        st.rerun()
    if e3.button("PDF", use_container_width=True, type="primary" if st.session_state.get("export_active") == "PDF" else "secondary"):
        st.session_state.export_active = "PDF"
        st.rerun()
    if e4.button("PowerPoint", use_container_width=True, type="primary" if st.session_state.get("export_active") == "PowerPoint" else "secondary"):
        st.session_state.export_active = "PowerPoint"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    fmt = st.session_state.get("export_active")
    if fmt:
        # Generate the file if needed
        if st.session_state.get("export_generated_fmt") != fmt:
            with st.spinner(f"Preparing {fmt}..."):
                try:
                    if fmt == "JSON":
                        st.session_state.export_data = export_json(rpt)
                        st.session_state.export_mime = "application/json"
                        st.session_state.export_ext = "json"
                    elif fmt == "Excel":
                        st.session_state.export_data = export_excel(rpt)
                        st.session_state.export_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        st.session_state.export_ext = "xlsx"
                    elif fmt == "PDF":
                        st.session_state.export_data = export_pdf(rpt)
                        st.session_state.export_mime = "application/pdf"
                        st.session_state.export_ext = "pdf"
                    elif fmt == "PowerPoint":
                        st.session_state.export_data = export_pptx(rpt)
                        st.session_state.export_mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        st.session_state.export_ext = "pptx"
                    
                    st.session_state.export_generated_fmt = fmt
                except Exception as ex:
                    st.error(f"Failed: {ex}")
        
        # Show the confirmation/preview card below the tabs
        if st.session_state.get("export_generated_fmt") == fmt and st.session_state.get("export_data"):
            with st.container(border=True):
                st.markdown(f"#### Are you want to download?")
                st.caption(f"Preview of {fmt} data (Showing max 5 rows/lines):")
                
                # Preview Data
                if fmt == "JSON":
                    # For JSON, decode bytes to string if necessary, then show first 5 lines
                    json_str = st.session_state.export_data
                    if isinstance(json_str, bytes):
                        json_str = json_str.decode('utf-8')
                    lines = json_str.split("\n")
                    st.code("\n".join(lines[:5]) + ("\n..." if len(lines) > 5 else ""), language="json")
                else:
                    # For Excel, PDF, PPTX, show a quick DataFrame preview
                    import pandas as pd
                    df_prev = pd.DataFrame([{
                        "Year": p.year, "TAM": _fmt(p.tam), "SAM": _fmt(p.sam), "SOM": _fmt(p.som), "CAGR": f"{p.cagr_applied:.1f}%"
                    } for p in rpt.five_year_projection]).head(5)
                    st.dataframe(df_prev, use_container_width=True, hide_index=True)
                
                # Actions
                c1, c2, _ = st.columns([1, 1, 3])
                with c1:
                    st.download_button(
                        label="Download",
                        data=st.session_state.export_data,
                        file_name=f"market_sizing.{st.session_state.export_ext}",
                        mime=st.session_state.export_mime,
                        use_container_width=True,
                        type="primary"
                    )
                with c2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.export_active = None
                        st.session_state.export_generated_fmt = None
                        st.rerun()


else:
    st.warning("No report data found. Please generate a report from the main app page.")
