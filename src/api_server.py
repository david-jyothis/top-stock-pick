from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import logging
import os

# Import analyzer
from src.stock_analyzer import StockAnalyzer
from src.stock_data_collector import StockDataCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Initialize components with environment variables
questdb_host = os.getenv('QUESTDB_HOST', 'questdb')
questdb_port = int(os.getenv('QUESTDB_PORT', '8812'))

analyzer = StockAnalyzer(db_host=questdb_host, db_port=questdb_port)
collector = StockDataCollector(db_host=questdb_host, db_port=questdb_port)

class StockAnalysis(BaseModel):
    symbol: str
    predicted_return: float
    technical_score: float
    sentiment_score: float
    overall_score: float

@app.get("/")
async def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/static/index.html")

@app.get("/api/top-stocks", response_model=List[StockAnalysis])
async def get_top_stocks():
    """Get top 10 stock picks"""
    try:
        stocks = analyzer.get_top_stocks(10)
        if not stocks:
            raise HTTPException(status_code=404, detail="No stocks found")
        return stocks
    except Exception as e:
        logger.error(f"Error getting top stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}")
async def get_stock_details(symbol: str):
    """Get detailed analysis for a specific stock"""
    try:
        analysis = analyzer.predict_stock_performance(symbol)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-data")
async def update_data():
    """Trigger data update"""
    try:
        collector.collect_all_data()
        return {"status": "success", "message": "Data update triggered successfully"}
    except Exception as e:
        logger.error(f"Error updating data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "questdb": f"{questdb_host}:{questdb_port}"}