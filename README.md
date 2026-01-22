# 📊 AI Market Sizing Estimator

[![Evals](https://img.shields.io/badge/Evals-Passing-success)](evals.py)
[![Model](https://img.shields.io/badge/Model-Claude%20Sonnet-blue)](https://anthropic.com)
[![Data](https://img.shields.io/badge/Data-World%20Bank%20API-orange)](https://data.worldbank.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> AI-powered TAM/SAM/SOM analysis using three methodologies — top-down, bottom-up, and value-theory — grounded in live World Bank data. Exports to PDF, Excel, PowerPoint, and JSON. Built for investor decks, board presentations, and annual planning.

---

## 📌 Problem this solves

Market sizing for investor decks and strategy docs requires **3–5 hours of research and spreadsheet work**. Estimates are often undocumented, impossible to defend, and inconsistent across methodologies. When a VC asks "how did you get to this number?" most PMs can't answer rigorously.

This tool generates a three-methodology market sizing analysis in under 60 seconds, with every assumption cited, every scenario range calculated, and a 5-year growth projection built in.

---

## ✨ What you get

| Section | Details |
|---|---|
| **TAM / SAM / SOM** | All three methodologies + reconciled consensus |
| **Scenario ranges** | Low / Mid / High for every estimate |
| **5-year projection** | Year-by-year growth with sourced CAGR |
| **Sensitivity analysis** | How changing key assumptions moves SOM |
| **Investor narrative** | 3-sentence pitch-ready framing |
| **Key risks** | What could make the sizing wrong |
| **Data citations** | Every World Bank data point used |

---

## 🔬 Three methodologies

**Top-Down** — Start from total industry size → filter by geography → filter by target segment → apply penetration rate

**Bottom-Up** — Start from addressable units (people/companies) × conversion rate × average price

**Value-Theory** — Start from value delivered per customer × willingness-to-pay fraction × number of buyers

The reconciled estimate is a weighted average of all three.

---

## 🌐 Data sources

- **World Bank API** — GDP, population, internet penetration, GNI per capita, urbanization (live, no API key needed)
- **Claude Sonnet** — Industry knowledge, CAGR benchmarks, segment sizing heuristics
- **Your own research** — Paste analyst reports, competitor revenues, or survey data for Claude to incorporate

---

## 🚀 Quickstart

```bash
git clone https://github.com/your-username/market-sizing.git
cd market-sizing
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

### Docker

```bash
cp .env.example .env
docker-compose up
```

---

## 📐 Architecture

```
app.py          ← Streamlit UI with 6 tabs + 4 export formats
analyzer.py     ← Claude Sonnet 3-methodology engine
worldbank.py    ← World Bank API fetcher (10 indicators, 20 geographies)
exporters.py    ← PDF (ReportLab), Excel (openpyxl), PPTX (python-pptx), JSON
schema.py       ← Pydantic data models
evals.py        ← 6-check automated benchmark across 3 industries
```

---

## 🧪 Evaluation

```bash
python evals.py
```

Checks: TAM > SAM > SOM hierarchy · 3 methodologies generated · Assumptions sourced · 5-year projection · Sensitivity axes · Investor narrative quality

---

## 📂 Structure

```
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/eval.yml
├── app.py
├── analyzer.py
├── worldbank.py
├── exporters.py
├── schema.py
├── evals.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🔮 Roadmap (v2.0)

- [ ] Crunchbase / PitchBook integration for funding-based TAM signals
- [ ] Comparable company revenue benchmarks
- [ ] Multi-product portfolio sizing
- [ ] Google Sheets live export
- [ ] Shareable report link (hosted)

---

## 📄 License

MIT — see [LICENSE](LICENSE).
