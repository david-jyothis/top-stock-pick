import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import time
import questdb.ingress as qi
import psycopg2

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
        """Return a list of test symbols for now"""
        return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'WIPRO.NS']

    def fetch_historical_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Fetch historical data for a given symbol"""
        try:
            # Remove .NS extension for storing in database
            clean_symbol = symbol.replace('.NS', '')
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            hist['Symbol'] = clean_symbol
            self.logger.info(f"Fetched {len(hist)} records for {symbol}")
            return hist
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def store_data_postgres(self, df: pd.DataFrame, table_name: str):
        """Store data using PostgreSQL connection"""
        try:
            cursor = self.conn.cursor()
            
            for index, row in df.iterrows():
                # Convert timestamp to string
                timestamp = index.strftime('%Y-%m-%d %H:%M:%S')
                
                insert_query = f"""
                INSERT INTO {table_name} 
                (timestamp, symbol, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    timestamp,
                    row['Symbol'],
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ))
            
            self.conn.commit()
            cursor.close()
            self.logger.info(f"Stored {len(df)} records in {table_name}")
            
        except Exception as e:
            self.logger.error(f"Error storing data in database: {e}")

    def generate_sample_news(self, symbol: str) -> List[Dict]:
        """Generate sample news data"""
        news_templates = [
            {"title": f"{symbol} reports strong quarterly results", "sentiment": 0.8},
            {"title": f"{symbol} announces expansion plans", "sentiment": 0.6},
            {"title": f"{symbol} faces market challenges", "sentiment": -0.4},
            {"title": f"New opportunities for {symbol}", "sentiment": 0.5}
        ]
        return news_templates

    def store_news_data(self, symbol: str, news_items: List[Dict]):
        """Store news data in database"""
        try:
            cursor = self.conn.cursor()
            
            for item in news_items:
                insert_query = """
                INSERT INTO stock_news 
                (timestamp, symbol, title, description, sentiment)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    datetime.now(),
                    symbol,
                    item['title'],
                    item.get('description', ''),
                    item.get('sentiment', 0)
                ))
            
            self.conn.commit()
            cursor.close()
            self.logger.info(f"Stored {len(news_items)} news items for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error storing news data: {e}")

    def collect_all_data(self):
        """Main method to collect all required data"""
        try:
            # Create tables if they don't exist
            cursor = self.conn.cursor()
            
            # Create stock_historical_data table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_historical_data (
                timestamp TIMESTAMP,
                symbol STRING,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume LONG
            );
            """)
            
            # Create stock_news table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_news (
                timestamp TIMESTAMP,
                symbol STRING,
                title STRING,
                description STRING,
                sentiment DOUBLE
            );
            """)
            
            self.conn.commit()
            cursor.close()
            
            symbols = self.get_nse_symbols()
            self.logger.info(f"Starting data collection for {len(symbols)} symbols")
            
            for symbol in symbols:
                self.logger.info(f"Processing {symbol}")
                
                # Fetch and store historical data
                hist_data = self.fetch_historical_data(symbol)
                if not hist_data.empty:
                    self.store_data_postgres(hist_data, 'stock_historical_data')
                
                # Generate and store sample news
                news_data = self.generate_sample_news(symbol.replace('.NS', ''))
                if news_data:
                    self.store_news_data(symbol.replace('.NS', ''), news_data)
                
                time.sleep(1)  # Avoid rate limiting
                
            self.logger.info("Data collection completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in data collection: {e}")
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    collector = StockDataCollector()
    collector.collect_all_data()