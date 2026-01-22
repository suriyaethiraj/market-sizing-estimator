from __future__ import annotations
import requests
from typing import Dict, List, Optional

WB_BASE = "https://api.worldbank.org/v2"

# Useful World Bank indicators for market sizing
INDICATORS = {
    "gdp_usd":           "NY.GDP.MKTP.CD",      # GDP (current USD)
    "gdp_per_capita":    "NY.GDP.PCAP.CD",      # GDP per capita
    "population":        "SP.POP.TOTL",          # Total population
    "internet_users":    "IT.NET.USER.ZS",       # Internet users (% of population)
    "mobile_subs":       "IT.CEL.SETS.P2",       # Mobile subscriptions per 100
    "urban_population":  "SP.URB.TOTL.IN.ZS",   # Urban population %
    "working_age_pop":   "SP.POP.1564.TO.ZS",   # Working age population %
    "gni_per_capita":    "NY.GNP.PCAP.CD",      # GNI per capita
    "fdi_inflows":       "BX.KLT.DINV.CD.WD",   # FDI net inflows
    "businesses":        "IC.BUS.EASE.XQ",       # Ease of doing business
}

# ISO3 country codes for common markets
COUNTRY_CODES: Dict[str, str] = {
    "United States":  "US",
    "United Kingdom": "GB",
    "India":          "IN",
    "Germany":        "DE",
    "France":         "FR",
    "Japan":          "JP",
    "China":          "CN",
    "Brazil":         "BR",
    "Canada":         "CA",
    "Australia":      "AU",
    "Singapore":      "SG",
    "UAE":            "AE",
    "South Korea":    "KR",
    "Indonesia":      "ID",
    "Mexico":         "MX",
    "Global":         "WLD",
    "Europe":         "EUU",
    "Southeast Asia": "EAS",
    "Latin America":  "LCN",
    "Africa":         "SSF",
}


def _fetch_indicator(country_code: str, indicator: str, year: int = 2023) -> Optional[float]:
    """Fetch a single World Bank indicator value."""
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator}"
    params = {"format": "json", "mrv": 3, "per_page": 5}
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2 or not data[1]:
            return None
        for entry in data[1]:
            if entry.get("value") is not None:
                return float(entry["value"])
        return None
    except Exception:
        return None


def fetch_market_data(geographies: List[str]) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Fetch key World Bank indicators for given geographies.
    Returns: { country_name: { indicator_key: value } }
    """
    results: Dict[str, Dict[str, Optional[float]]] = {}

    for geo in geographies:
        code = COUNTRY_CODES.get(geo, "WLD")
        geo_data: Dict[str, Optional[float]] = {}

        for key, indicator_id in INDICATORS.items():
            value = _fetch_indicator(code, indicator_id)
            geo_data[key] = value

        results[geo] = geo_data

    return results


def format_wb_summary(wb_data: Dict[str, Dict[str, Optional[float]]]) -> str:
    """Format World Bank data into a readable string for the LLM prompt."""
    lines = ["=== WORLD BANK DATA ==="]
    for country, metrics in wb_data.items():
        lines.append(f"\n{country.upper()}:")
        if metrics.get("gdp_usd"):
            lines.append(f"  GDP: ${metrics['gdp_usd']/1e12:.2f}T USD")
        if metrics.get("population"):
            lines.append(f"  Population: {metrics['population']/1e6:.1f}M")
        if metrics.get("internet_users"):
            lines.append(f"  Internet penetration: {metrics['internet_users']:.1f}%")
        if metrics.get("gdp_per_capita"):
            lines.append(f"  GDP per capita: ${metrics['gdp_per_capita']:,.0f}")
        if metrics.get("urban_population"):
            lines.append(f"  Urban population: {metrics['urban_population']:.1f}%")
        if metrics.get("working_age_pop"):
            lines.append(f"  Working age (15-64): {metrics['working_age_pop']:.1f}%")
        if metrics.get("mobile_subs"):
            lines.append(f"  Mobile subscriptions per 100: {metrics['mobile_subs']:.1f}")

    return "\n".join(lines)


def get_used_indicators(wb_data: Dict[str, Dict[str, Optional[float]]]) -> List[str]:
    """Return list of data points actually fetched (for citations)."""
    used = []
    for country, metrics in wb_data.items():
        for key, val in metrics.items():
            if val is not None:
                label = key.replace("_", " ").title()
                used.append(f"World Bank — {country}: {label}")
    return used
