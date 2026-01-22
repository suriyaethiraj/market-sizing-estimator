# Contributing

## Setup
```bash
git clone https://github.com/your-username/market-sizing.git
cd market-sizing
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY
streamlit run app.py
```

## Before submitting a PR
- `python evals.py` must pass
- Update `CHANGELOG.md` under `[Unreleased]`
- No secrets committed
- `pip-audit` clean

## Adding new geographies
Add the country name → ISO3 code mapping in `worldbank.py → COUNTRY_CODES`
and add it to the `GEOGRAPHIES` list in `app.py`.

## Adding new indicators
Add the indicator ID to `worldbank.py → INDICATORS` and update
`format_wb_summary()` to include it in the LLM prompt.
