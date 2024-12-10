import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import questdb.ingress as qi
import psycopg2
from bs4 import BeautifulSoup
import logging

class StockDataCollector:
    def __init__(self, db_host: str = 'questdb', db_port: int = 8812):
        self.logger = logging.getLogger(__name__)
        self.db_host = db_host
        self.db_port = db_port
        self.conn = psycopg2.connect(
            dbname='qdb',
            user='admin',
            password='quest',
            host=db_host,
            port=db_port
        )
        self.conn.autocommit = True
        
    def get_nse_symbols(self) -> List[str]:
        """Fetch all NSE listed symbols"""
        try:
            # NSE provides this data through their website
            nse_url = "https://www1.nseindia.com/content/equities/EQUITY_L.csv"
            df = pd.read_csv(nse_url)
            return df['SYMBOL'].tolist()
        except Exception as e:
            self.logger.error(f"Error fetching NSE symbols: {e}")
            return []

    def fetch_historical_data(self, symbol: str, period: str = "5y") -> pd.DataFrame:
        """Fetch historical data for a given symbol"""
        try:
            stock = yf.Ticker(f"{symbol}.NS")
            hist = stock.history(period=period)
            hist['Symbol'] = symbol
            return hist
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def fetch_news(self, symbol: str, days: int = 30) -> List[Dict]:
        """Fetch recent news articles related to the stock"""
        try:
            news_sources = [
                f"https://newsapi.org/v2/everything?q={symbol}",
                f"https://economictimes.indiatimes.com/markets/stocks/news"
            ]
            news_items = []
            
            for source in news_sources:
                response = requests.get(source)
                if response.status_code == 200:
                    articles = response.json().get('articles', [])
                    news_items.extend(articles)
            
            return news_items
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def store_data(self, data: pd.DataFrame, table_name: str):
        """Store data in QuestDB using line protocol"""
        try:
            with qi.Sender(self.db_host, 9009) as sender:
                for index, row in data.iterrows():
                    # Convert timestamp to microseconds
                    timestamp = int(index.timestamp() * 1_000_000)
                    
                    # Send data using line protocol
                    sender.row(
                        table_name,
                        symbols={'symbol': row['Symbol']},
                        columns={
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': int(row['Volume'])
                        },
                        at=timestamp
                    )
        except Exception as e:
            self.logger.error(f"Error storing data in QuestDB: {e}")

    def collect_all_data(self):
        """Main method to collect all required data"""
        symbols = self.get_nse_symbols()
        
        for symbol in symbols:
            # Fetch and store historical data
            hist_data = self.fetch_historical_data(symbol)
            if not hist_data.empty:
                self.store_data(hist_data, 'stock_historical_data')
            
            # Fetch and store news
            news_data = self.fetch_news(symbol)
            if news_data:
                news_df = pd.DataFrame(news_data)
                self.store_data(news_df, 'stock_news')

if __name__ == "__main__":
    collector = StockDataCollector()
    collector.collect_all_data()