import questdb.ingress as qi
import logging
import sys
import os
import time
import psycopg2

def wait_for_questdb(host='questdb', port=8812, max_attempts=30):
    """Wait for QuestDB to be ready"""
    attempt = 0
    while attempt < max_attempts:
        try:
            # Try to connect using psycopg2
            conn = psycopg2.connect(
                dbname='qdb',
                user='admin',
                password='quest',
                host=host,
                port=port
            )
            conn.close()
            logging.info("Successfully connected to QuestDB")
            return True
        except Exception as e:
            attempt += 1
            logging.warning(f"Attempt {attempt}/{max_attempts} to connect to QuestDB failed: {e}")
            if attempt < max_attempts:
                time.sleep(2)
    
    raise Exception("Failed to connect to QuestDB after maximum attempts")

def init_database(host='questdb', port=8812):
    """Initialize QuestDB with required tables"""
    try:
        # Wait for QuestDB to be ready
        wait_for_questdb(host, port)
        
        # Connect using psycopg2 for DDL operations
        conn = psycopg2.connect(
            dbname='qdb',
            user='admin',
            password='quest',
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Define schema queries
        schema_queries = [
            """
            CREATE TABLE IF NOT EXISTS stock_historical_data (
                timestamp TIMESTAMP,
                symbol SYMBOL,
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
                symbol SYMBOL,
                title STRING,
                description STRING,
                source STRING,
                sentiment DOUBLE
            ) timestamp(timestamp) PARTITION BY DAY;
            """,
            """
            CREATE TABLE IF NOT EXISTS algorithm_performance (
                timestamp TIMESTAMP,
                symbol SYMBOL,
                predicted_direction INT,
                actual_direction INT,
                predicted_return DOUBLE,
                actual_return DOUBLE,
                confidence_score DOUBLE
            ) timestamp(timestamp) PARTITION BY DAY;
            """
        ]

        # Execute schema creation queries
        for query in schema_queries:
            try:
                cursor.execute(query)
                logging.info(f"Executed query successfully: {query[:50]}...")
            except Exception as e:
                logging.error(f"Error executing query: {query[:50]}... Error: {e}")
                raise

        cursor.close()
        conn.close()
        logging.info("Database initialization completed successfully")
        return True

    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get database connection details from environment
    db_host = os.getenv('QUESTDB_HOST', 'questdb')
    db_port = int(os.getenv('QUESTDB_PORT', '8812'))

    # Initialize database
    success = init_database(db_host, db_port)
    if success:
        print("Database initialized successfully")
        sys.exit(0)
    else:
        print("Failed to initialize database")
        sys.exit(1)