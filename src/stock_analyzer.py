import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import questdb
from typing import List, Dict
import logging
from textblob import TextBlob
import psycopg2

class StockAnalyzer:
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
        self.scaler = StandardScaler()
        
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for analysis"""
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Volatility
        df['Volatility'] = df['Close'].rolling(window=20).std()
        
        return df

    def analyze_news_sentiment(self, news_items: List[Dict]) -> float:
        sentiments = []
        for item in news_items:
            blob = TextBlob(item['title'] + ' ' + item['description'])
            sentiments.append(blob.sentiment.polarity)
        return np.mean(sentiments) if sentiments else 0

    def predict_stock_performance(self, symbol: str) -> Dict:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM stock_historical_data WHERE symbol = %s", (symbol,))
            columns = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            hist_data = pd.DataFrame(cursor.fetchall(), columns=columns)
            cursor.close()
            
            if hist_data.empty:
                return None
                
            hist_data = self.calculate_technical_indicators(hist_data)
            
            # Fetch and analyze news
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM stock_news WHERE symbol = %s", (symbol,))
            news_columns = ['timestamp', 'symbol', 'title', 'description', 'source', 'sentiment']
            news_data = pd.DataFrame(cursor.fetchall(), columns=news_columns)
            cursor.close()
            
            sentiment_score = self.analyze_news_sentiment(news_data.to_dict('records'))
            
            # Prepare features
            features = [
                'SMA_20', 'SMA_50', 'SMA_200', 'RSI', 'MACD', 'Signal_Line',
                'Volatility', 'volume'
            ]
            X = hist_data[features].fillna(0)
            X['Sentiment'] = sentiment_score
            X = self.scaler.fit_transform(X)
            
            # Train model
            y = hist_data['close'].pct_change().shift(-1).fillna(0)
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X[:-1], y[:-1])
            
            # Make prediction
            prediction = model.predict(X[-1:])
            
            return {
                'symbol': symbol,
                'predicted_return': float(prediction[0]),
                'technical_score': self.calculate_technical_score(hist_data),
                'sentiment_score': sentiment_score,
                'overall_score': self.calculate_overall_score(prediction[0], sentiment_score)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return None

    def calculate_technical_score(self, df: pd.DataFrame) -> float:
        scores = []
        
        # Trend following indicators
        if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
            scores.append(1)
        if df['SMA_50'].iloc[-1] > df['SMA_200'].iloc[-1]:
            scores.append(1)
            
        # RSI
        rsi = df['RSI'].iloc[-1]
        if 30 <= rsi <= 70:
            scores.append(1)
            
        # MACD
        if df['MACD'].iloc[-1] > df['Signal_Line'].iloc[-1]:
            scores.append(1)
            
        return sum(scores) / len(scores)

    def calculate_overall_score(self, predicted_return: float, sentiment_score: float) -> float:
        weights = {
            'predicted_return': 0.5,
            'sentiment': 0.3,
            'risk': 0.2
        }
        
        normalized_return = min(max(predicted_return, -1), 1)
        risk_score = 1 - abs(normalized_return)
        
        return (
            weights['predicted_return'] * normalized_return +
            weights['sentiment'] * sentiment_score +
            weights['risk'] * risk_score
        )

    def get_top_stocks(self, n: int = 10) -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT symbol FROM stock_historical_data")
            symbols = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            results = []
            for symbol in symbols:
                analysis = self.predict_stock_performance(symbol)
                if analysis:
                    results.append(analysis)
            
            # Sort by overall score
            results.sort(key=lambda x: x['overall_score'], reverse=True)
            return results[:n]
            
        except Exception as e:
            self.logger.error(f"Error getting top stocks: {e}")
            return []