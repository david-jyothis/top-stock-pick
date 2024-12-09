# NSE Stock Analysis and Profiling System

An advanced stock analysis system for NSE stocks using machine learning and technical analysis.

## Features

- Real-time stock data collection
- Technical analysis
- Machine learning-based predictions
- News sentiment analysis
- Web dashboard
- Automated testing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database:
```bash
python scripts/init_db.py
```

3. Run the application:
```bash
python src/api_server.py
```

4. Access dashboard at http://localhost:8000

## Testing

Run tests:
```bash
python -m pytest tests/
```

## License

MIT