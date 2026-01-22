import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel
from schema import MarketInput, MarketSizingReport
from analyzer import generate_market_sizing
from exporters import export_json, export_excel, export_pdf, export_pptx

app = FastAPI(title="Market Sizing Estimator")

class AnalyzeRequest(BaseModel):
    provider: str
    api_key: str
    market_input: MarketInput

class ExportRequest(BaseModel):
    format: str
    report: MarketSizingReport

@app.post("/api/analyze", response_model=MarketSizingReport)
async def api_analyze(req: AnalyzeRequest):
    try:
        # Pre-warm world bank data
        from worldbank import fetch_market_data
        try:
            fetch_market_data(req.market_input.geographies)
        except Exception:
            pass

        report = generate_market_sizing(
            inp=req.market_input,
            api_key=req.api_key,
            provider=req.provider
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export")
async def api_export(req: ExportRequest):
    fmt = req.format.lower()
    report = req.report

    try:
        if fmt == "json":
            data = export_json(report)
            return Response(
                content=data,
                media_type="application/json",
                headers={"Content-Disposition": 'attachment; filename="market_sizing.json"'}
            )
        elif fmt == "excel":
            data = export_excel(report)
            return Response(
                content=data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": 'attachment; filename="market_sizing.xlsx"'}
            )
        elif fmt == "pdf":
            data = export_pdf(report)
            return Response(
                content=data,
                media_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="market_sizing.pdf"'}
            )
        elif fmt == "powerpoint":
            data = export_pptx(report)
            return Response(
                content=data,
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                headers={"Content-Disposition": 'attachment; filename="market_sizing.pptx"'}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format requested")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Mount static files at root
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
