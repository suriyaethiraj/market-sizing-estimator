# Changelog

## [Unreleased]

## [1.0.0] — 2025-09-17

### Added
- Three-methodology market sizing: Top-Down, Bottom-Up, Value-Theory
- Reconciled TAM/SAM/SOM with Low/Mid/High scenario ranges
- 5-year growth projection with sourced CAGR per industry
- Sensitivity analysis across 3 key variables per analysis
- World Bank API integration (10 indicators, 20 geographies, no API key needed)
- User-provided research context ingestion
- Investor narrative (3-sentence pitch framing)
- PDF export (ReportLab) with funnel chart and assumption tables
- Excel export (openpyxl) with 4 sheets: Summary, Methodologies, Projection, Sensitivity
- PowerPoint export (python-pptx) with 5 investor-ready slides
- JSON export for downstream pipeline use
- Plotly interactive charts: funnel, scenario bars, line projection, sensitivity bars
- Automated eval harness with 6 quality checks across 3 industries
- GitHub Actions CI
- Docker support
