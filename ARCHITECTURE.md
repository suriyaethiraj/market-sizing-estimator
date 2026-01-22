# System Architecture: Market Sizing Estimator

This document outlines the high-level entity relationship and data flow architecture of the Market Sizing Estimator application. 

The application follows a modern decoupled architecture: a vanilla HTML/JS frontend interacting with a FastAPI Python backend, which in turn acts as an orchestrator between external data sources (World Bank) and generative AI APIs.

## High-Level Architecture Diagram

```mermaid
flowchart TD
    %% Define styles
    classDef frontend fill:#E2E8F0,stroke:#64748B,stroke-width:2px,color:#0F172A
    classDef backend fill:#E0E7FF,stroke:#4F46E5,stroke-width:2px,color:#0F172A
    classDef external fill:#DCFCE7,stroke:#16A34A,stroke-width:2px,color:#0F172A

    subgraph Client [Frontend - Browser]
        UI[index.html & styles.css]:::frontend
        App[app.js / Plotly.js]:::frontend
    end

    subgraph Server [Backend - FastAPI]
        ServerPY[server.py\nAPI Router]:::backend
        Schema[schema.py\nPydantic Models]:::backend
        Analyzer[analyzer.py\nCore Logic]:::backend
        WB[worldbank.py\nData Fetcher]:::backend
        Exporters[exporters.py\nFile Generation]:::backend
    end

    subgraph External [External APIs]
        WorldBankAPI[World Bank Data API\n(Macroeconomics)]:::external
        LLM[AI Providers\nOpenAI / Anthropic / Groq / Gemini]:::external
    end

    %% Data Flow
    UI --> |1. User inputs market parameters| App
    App -->|2. POST /api/analyze| ServerPY
    
    ServerPY -->|3. Validates Input| Schema
    ServerPY -->|4. Invokes| Analyzer
    
    Analyzer -->|5. Requests Geodata| WB
    WB <-->|6. HTTP GET Indicators| WorldBankAPI
    
    Analyzer -->|7. Compiles Prompt + WB Data| LLM
    LLM -->|8. Returns unstructured JSON| Analyzer
    
    Analyzer -->|9. Validates & Cleans JSON| Schema
    Analyzer -->|10. Returns structured object| ServerPY
    ServerPY -->|11. HTTP 200 OK| App
    App -->|12. Renders Plotly Charts| UI

    %% Export Flow
    App -.->|A. POST /api/export| Exporters
    Exporters -.->|B. Returns Blob (PDF/XLSX/PPTX)| App
```

## Component Breakdown

### 1. Frontend (Client)
- **`index.html` & `styles.css`**: The structural and visual presentation of the dashboard. Uses a custom vanilla CSS design system (no external CSS frameworks).
- **`app.js`**: Handles DOM manipulation, form state, and API communication. It manages the loading states and uses `Plotly.js` to render the interactive TAM/SAM/SOM charts, methodology comparisons, and sensitivity analyses.

### 2. Backend (FastAPI)
- **`server.py`**: The main entry point. Mounts the static frontend files and exposes two primary API routes: `/api/analyze` and `/api/export`.
- **`schema.py`**: Utilizes Pydantic to strictly define and validate both the inbound `MarketInput` requests and the outbound `MarketSizingReport` JSON structures.
- **`worldbank.py`**: A specialized module that makes outbound HTTP requests to the World Bank API to fetch real-time macroeconomic indicators (GDP, population, internet penetration) based on the user's selected geographies.
- **`analyzer.py`**: The core "brain" of the application. It aggregates the user's input and the fetched World Bank data, constructs a rigorous system prompt, and manages communication with the selected AI provider (Anthropic, OpenAI, Gemini, or Groq). It also handles fallback parsing and JSON repair.
- **`exporters.py`**: Converts the structured JSON report into downloadable formats (Excel, PDF, PowerPoint) using libraries like `pandas`, `fpdf`, and `python-pptx`.

### 3. External APIs
- **World Bank API**: Provides grounding data to ensure the AI's assumptions are rooted in factual, up-to-date macroeconomic reality.
- **AI Providers**: The generative models that perform the actual top-down, bottom-up, and value-theory mathematical modeling based on the provided constraints and data.
