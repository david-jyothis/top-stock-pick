"""
QuestDB Schema definition for the stock analysis system
"""

SCHEMA_QUERIES = [
    """
    CREATE TABLE IF NOT EXISTS stock_historical_data (
        timestamp TIMESTAMP,
        symbol SYMBOL INDEX,
        open DOUBLE,
        high DOUBLE,
        low DOUBLE,
        close DOUBLE,
        volume LONG
    ) timestamp(timestamp) PARTITION BY DAY;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS stock_news (
        timestamp TIMESTAMP,
        symbol SYMBOL INDEX,
        title STRING,
        description STRING,
        source STRING,
        sentiment DOUBLE
    ) timestamp(timestamp) PARTITION BY DAY;
    """,
    
    """
    CREATE TABLE IF NOT EXISTS algorithm_performance (
        timestamp TIMESTAMP,
        symbol SYMBOL INDEX,
        predicted_direction INT,
        actual_direction INT,
        predicted_return DOUBLE,
        actual_return DOUBLE,
        confidence_score DOUBLE
    ) timestamp(timestamp) PARTITION BY DAY;
    """
]