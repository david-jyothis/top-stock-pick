<<<<<<< HEAD
# NSE Stock Analysis System

A comprehensive system for analyzing NSE stocks using machine learning and technical analysis.

## Features

- Real-time stock data collection from NSE
- Technical analysis using multiple indicators
- Machine learning-based predictions
- News sentiment analysis
- Interactive web dashboard
- Automated testing and CI/CD pipeline
- QuestDB for high-performance time-series data storage

## Prerequisites

- Docker and Docker Compose
- Python 3.9 or higher
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/top-stock-pick.git
cd top-stock-pick
```

2. Start the application:
```bash
docker-compose up -d
```

3. Initialize the database:
```bash
docker-compose exec app python scripts/init_db.py
```

4. Access the application:
   - Dashboard: http://localhost:8000/static/index.html
   - API Docs: http://localhost:8000/docs
   - QuestDB Console: http://localhost:9000

## Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
=======
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
>>>>>>> 25c7cbae76f73da59217fc164e1748bb72fbfa9b
```bash
pip install -r requirements.txt
```

<<<<<<< HEAD
3. Run tests:
=======
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
>>>>>>> 25c7cbae76f73da59217fc164e1748bb72fbfa9b
```bash
python -m pytest tests/
```

<<<<<<< HEAD
## Architecture

- FastAPI for REST API
- QuestDB for time-series data
- Pandas & Scikit-learn for analysis
- Docker for containerization

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License
=======
## License

MIT
>>>>>>> 25c7cbae76f73da59217fc164e1748bb72fbfa9b
