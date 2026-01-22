from __future__ import annotations
import json
import re
from datetime import datetime
import anthropic
from schema import MarketInput, MarketSizingReport
from worldbank import fetch_market_data, format_wb_summary, get_used_indicators

SYSTEM_PROMPT = """You are a world-class Market Sizing Analyst who has built market models for 
Goldman Sachs, McKinsey, and top-tier VC firms. You are rigorous, data-driven, and always cite 
your sources and assumptions explicitly.

RULES:
- All monetary values in USD millions (e.g. 5000 = $5B)
- Every assumption must have a source (World Bank data provided, industry knowledge, or stated as "AI estimate")
- TAM > SAM > SOM always — never violate this hierarchy
- Low scenario = conservative (-30% to -40% of mid), High = optimistic (+40% to +60% of mid)
- 5-year projections must use realistic CAGR for the industry (cite the CAGR source)
- Sensitivity axes must show how changing ONE variable moves the SOM
- investor_narrative must be 3 crisp sentences suitable for a pitch deck
- Return ONLY valid JSON — no markdown fences, no explanation"""


def _build_prompt(inp: MarketInput, wb_summary: str) -> str:
    geo_str = ", ".join(inp.geographies)
    custom  = f"\nUSER-PROVIDED RESEARCH:\n{inp.custom_research}" if inp.custom_research else ""
    today   = datetime.now().strftime("%Y-%m-%d")

    return f"""Perform a comprehensive market sizing analysis for the following product.

PRODUCT: {inp.product_description}
INDUSTRY: {inp.industry_vertical}
GEOGRAPHIES: {geo_str}
COMPANY STAGE: {inp.company_stage}
TARGET PERSONA: {inp.target_persona}
PRICING MODEL: {inp.pricing_model}
AVERAGE PRICE: ${inp.avg_price:,.2f} {inp.price_unit}
{custom}

{wb_summary}

Return a JSON object matching this EXACT schema (all monetary values in USD millions):

{{
  "title": "Market Sizing: [Product] in [Geography]",
  "product_description": "{inp.product_description}",
  "industry": "{inp.industry_vertical}",
  "geographies": {json.dumps(inp.geographies)},
  "methodology_results": [
    {{
      "methodology": "Top-Down",
      "tam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "sam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "som": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "key_assumptions": [
        {{"label": "assumption name", "value": "specific value", "source": "World Bank / Industry report / AI estimate", "confidence": "High | Medium | Low"}}
      ],
      "narrative": "2-3 sentence explanation of this methodology's approach and findings"
    }},
    {{
      "methodology": "Bottom-Up",
      "tam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "sam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "som": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "key_assumptions": [],
      "narrative": "..."
    }},
    {{
      "methodology": "Value-Theory",
      "tam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "sam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "som": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
      "key_assumptions": [],
      "narrative": "..."
    }}
  ],
  "reconciled_tam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
  "reconciled_sam": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
  "reconciled_som": {{"low": 0, "mid": 0, "high": 0, "unit": "USD millions"}},
  "five_year_projection": [
    {{"year": 2025, "tam": 0, "sam": 0, "som": 0, "cagr_applied": 0}},
    {{"year": 2026, "tam": 0, "sam": 0, "som": 0, "cagr_applied": 0}},
    {{"year": 2027, "tam": 0, "sam": 0, "som": 0, "cagr_applied": 0}},
    {{"year": 2028, "tam": 0, "sam": 0, "som": 0, "cagr_applied": 0}},
    {{"year": 2029, "tam": 0, "sam": 0, "som": 0, "cagr_applied": 0}}
  ],
  "sensitivity_axes": [
    {{
      "variable": "Variable name (e.g. Market Penetration Rate)",
      "values": ["1%", "3%", "5%", "8%", "12%"],
      "som_impacts": [0, 0, 0, 0, 0]
    }},
    {{
      "variable": "Average Contract Value",
      "values": ["$500", "$1,000", "$2,000", "$5,000", "$10,000"],
      "som_impacts": [0, 0, 0, 0, 0]
    }},
    {{
      "variable": "Addressable Geography Expansion",
      "values": ["1 country", "3 countries", "5 countries", "10 countries", "Global"],
      "som_impacts": [0, 0, 0, 0, 0]
    }}
  ],
  "world_bank_data_used": ["list of World Bank data points actually used in the analysis"],
  "executive_summary": "4-5 sentence summary covering TAM/SAM/SOM, methodology reconciliation, and growth outlook",
  "investor_narrative": "Exactly 3 sentences: (1) Market size & growth, (2) Our addressable slice & why, (3) Realistic capture target & timeline",
  "confidence_rating": "High | Medium | Low",
  "key_risks": ["risk 1", "risk 2", "risk 3", "risk 4"],
  "generated_at": "{today}"
}}

IMPORTANT:
- Use the World Bank data provided to ground your population, GDP, and internet penetration assumptions
- Bottom-Up: start from addressable units × pricing model
- Top-Down: start from total industry size, filter down by geography/persona/stage
- Value-Theory: start from value delivered to customer × willingness to pay × addressable buyers
- Reconciled values = weighted average of the 3 methodologies
- Make sensitivity_axes realistic and relevant to THIS specific product
- All numbers must be internally consistent (TAM > SAM > SOM always)

Return ONLY the JSON object."""


def generate_market_sizing(inp: MarketInput, api_key: str, provider: str = "Anthropic") -> MarketSizingReport:
    # Fetch World Bank data
    wb_data    = fetch_market_data(inp.geographies)
    wb_summary = format_wb_summary(wb_data)
    wb_used    = get_used_indicators(wb_data)
    prompt     = _build_prompt(inp, wb_summary)

    if provider == "Mock Data":
        dummy_data = {
            "title": "Market Sizing: AI-Powered Project Management Platform",
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
        return MarketSizingReport(**dummy_data)

    if provider == "Anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text

    elif provider == "OpenAI":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content

    elif provider == "Gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        
        # gemini-3.6-flash is the standard free tier model in the current API version
        model_id = "gemini-3.6-flash"
        
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json"
                )
            )
            raw = response.text
        except Exception as e:
            raise ValueError(f"Gemini API Error (using {model_id}). Error: {e}")

    elif provider == "Groq":
        from groq import Groq
        client = Groq(api_key=api_key)
        available_models = client.models.list()
        valid_models = [
            m.id for m in available_models.data 
            if 'guard' not in m.id.lower() 
            and 'tool' not in m.id.lower() 
            and 'whisper' not in m.id.lower()
        ]
        
        if not valid_models:
            raise ValueError(f"No valid conversational models found. Available models: {[m.id for m in available_models.data]}")
            
        # Try to prioritize conversational models
        llama_models = [m for m in valid_models if 'llama' in m.lower()]
        qwen_models = [m for m in valid_models if 'qwen' in m.lower()]
        mixtral_models = [m for m in valid_models if 'mixtral' in m.lower()]
        gemma_models = [m for m in valid_models if 'gemma' in m.lower()]
        
        if llama_models:
            model_id = llama_models[-1]
        elif mixtral_models:
            model_id = mixtral_models[-1]
        elif qwen_models:
            model_id = qwen_models[-1]
        elif gemma_models:
            model_id = gemma_models[-1]
        else:
            raise ValueError(f"No standard conversational models (LLaMA/Mixtral/Qwen/Gemma) available on this API key. You only have access to: {valid_models}")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=16000
        )
        raw = response.choices[0].message.content
        
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Robust JSON extraction to handle conversational filler
    match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if match:
        clean = match.group(1)
    else:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        
    try:
        import json_repair
        data = json_repair.loads(clean)
    except Exception as e:
        # Log model ID and raw output
        debug_info = f"Provider: {provider}\n"
        if provider == "Groq":
            debug_info += f"Model Used: {model_id}\n"
        debug_info += f"Raw Output: '{raw}'"
        
        with open("groq_error_log.txt", "w") as f:
            f.write(debug_info)
        raise ValueError(f"Failed to parse JSON. I've saved the raw output to 'groq_error_log.txt'.")

    # Merge World Bank citations
    if wb_used:
        existing = set(data.get("world_bank_data_used", []))
        data["world_bank_data_used"] = list(existing | set(wb_used))

    try:
        from pydantic import ValidationError
        return MarketSizingReport(**data)
    except Exception as e:
        if provider == "Groq":
            raise ValueError(
                "The Groq API truncated the response (likely hitting a token or rate limit). "
                "Because of this, the AI was unable to generate all the mandatory data required to render the dashboard. "
                "Please try again, or select 'OpenAI' or 'Anthropic' from the provider dropdown if the issue persists!"
            )
        else:
            raise ValueError(f"The AI missed some required fields in its response. Details: {str(e)[:200]}")
