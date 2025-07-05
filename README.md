# AI Email Scraping to Live Ledger POC

A comprehensive proof of concept (POC) that automatically extracts financial data from emails and pushes it into a live ledger system with AI-powered classification.

## 🏗️ **Project Structure**

```
email-ledger-poc/
├── src/                          # Main source code
│   ├── __init__.py
│   ├── app/                      # Application core
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── db/
│   │   │   ├──models.py            # Database models
│   │   ├── core/                # Core business logic
│   │   │   ├── __init__.py
│   │   │   └── processor.py     # Main processing logic
│   │   ├── services/            # Business services
│   │   │   ├── __init__.py
│   │   │   ├── email_processor.py
│   │   │   ├── ai_extractor.py
│   │   │   └── ledger_service.py
│   │   └── api/                 # REST API
│   │   │  ├── __init__.py
│   │   │  ├── __init__.py
│   │   │  ├── app.py          # FastAPI application
│   │   │  ├── routes.py       # API routes
│   │   └── schema/ 
│   │       └── schemas.py      # Pydantic schemas
│   └── cli/                    # Command-line interface
│       ├── __init__.py
│       └── main.py             # CLI entry point
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
├── setup.py                    # Package setup configuration
├── MANIFEST.in                 # Package file inclusion rules
├── Makefile                    # Development tasks (Unix/Linux/macOS)
├── Makefile.win                # Development tasks (Windows)
├── dev.ps1                     # PowerShell development script
├── dev.bat                     # Windows batch development script
├── requirements.txt             # Dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-service deployment
└── README.md                   # This file
```

## 📸 **Preview**

<div align="center">

### Transaction Endpoind
![Transaction Endpoind](preview/preview%20(1).png)

### GCP Gmail Endpoint Publish
![GCP Gmail Endpoint Publish](preview/preview%20(2).png)

### GCP Gmail Endpoint Credential
![GCP Gmail Endpoint Credential](preview/preview%20(4).png)

### Endpoint Process Email
![Enpoint Process Email](preview/preview%20(5).png)

### Endpoint Health
![Endpoint Health](preview/preview%20(6).png)

### Endpoint Summary
![Endpoint Summary](preview/preview%20(7).png)

</div>

## 🎯 **Core Features Implemented:**

#### 1. **Email Ingestion** ✅
- **Gmail API Integration**: Connects to Gmail inbox via `simplegmail`
- **Smart Filtering**: Automatically identifies financial emails from:
  - Stripe, PayPal, Wise, Bank notifications
  - Receipt, invoice, payment emails
- **Batch Processing**: Configurable email batch sizes
- **Duplicate Prevention**: Tracks processed emails

#### 2. **AI-Powered Data Extraction** ✅
- **OpenAI GPT-3.5-turbo Integration**: Intelligent financial data extraction
- **Structured Data Fields**:
  - Amount and currency
  - Vendor/merchant name
  - Transaction type (debit/credit)
  - Reference ID and description
- **Fallback Pattern Matching**: Regex-based extraction when AI fails
- **Confidence Scoring**: Each extraction includes confidence metrics

#### 3. **Expense Classification** ✅
- **AI Classification**: Automatically categorizes into:
  - Meals and entertainment
  - Transport
  - SaaS subscriptions
  - Travel
  - Office supplies
  - Utilities
  - Insurance
  - Professional services
  - Marketing
  - Other

#### 4. **Live Ledger System** ✅
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **REST API**: FastAPI-based API with full CRUD operations
- **Real-time Processing**: Continuous email monitoring
- **Transaction Management**: Complete transaction lifecycle

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- PostgreSQL database
- Gmail API credentials (credentials.json)
- OpenAI API key
#### **Set Up GCP Gmail API**
- How to Create Gmail API App in the Google Developer Console: https://youtu.be/1Ua0Eplg75M?si=O61V_VunBO8i1INY
- Save the the file as credentials.json in root folder
#### 🐍 **Conda Environment Setup**
If you use [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html), you can prepare your environment as follows:

```bash
# Create a new environment with Python 3.11
conda create -n email-ledger python=3.11

# Activate the environment
conda activate email-ledger

# (Optional) Install pip in the environment if not already present
conda install pip

# Install project dependencies
pip install -r requirements.txt

# (Recommended) Install in development mode
pip install -e .

# Or use the install script for a full setup
python install.py
```

**Note:**
Some dependencies (like `psycopg2-binary`, `PyPDF2`, `lxml`, etc.) will be installed via pip. If you encounter build issues, you can pre-install some libraries with conda:

```bash
conda install -c conda-forge psycopg2 lxml
```
```

### **1. Installation**

#### **Option A: Modern Installation (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd email-ledger-poc

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[dev,test]"
```

#### **Option B: Using Development Scripts**
```bash
# Using Make (Unix/Linux/macOS)
make install-dev

# Using PowerShell (Windows)
.\dev.ps1 install-dev

# Using Batch (Windows)
dev.bat install-dev

# Using Installation Script
python install.py
```

#### **Option C: Traditional Installation**
```bash
# Install dependencies
pip install -r requirements.txt
```

### **2. Setup Environment**
```bash
# Copy environment file
cp env.example .env

# Edit .env with your credentials
nano .env
```

### **3. Configure Gmail API**
```bash
# Run the setup script
python scripts/setup_gmail.py
```

### **4. Setup Database**
```bash
# Using Docker
docker-compose up -d db

# Or manually create PostgreSQL database
createdb ledger_db
```

### **5. Run the Application**

#### **CLI Usage (Recommended)**
```bash
# Process emails once
python -m src.cli.main process

# Run continuous processing
python -m src.cli.main process --continuous

# Setup database tables
python -m src.cli.main setup
```

#### **Using Development Scripts**
```bash
# Using Make (Unix/Linux/macOS)
make run-cli              # Process emails once
make run-cli-continuous   # Continuous processing
make run-api-dev          # Start API server

# Using PowerShell (Windows)
.\dev.ps1 run-cli
.\dev.ps1 run-cli-continuous
.\dev.ps1 run-api-dev

# Using Batch (Windows)
dev.bat run-cli
dev.bat run-cli-continuous
dev.bat run-api-dev
```

#### **API Server**
```bash
# Start the API server
python -m src.app.api.app

# Or using uvicorn directly
uvicorn src.app.api.app:app --reload --host 0.0.0.0 --port 8000
```

#### **Docker Deployment (Recommended)**
```bash
# Start all services
docker-compose up --build

```

## 📚 **Usage Examples**

### **CLI Commands**
```bash
# Process emails once
python -m src.cli.main process

# Run continuous processing
python -m src.cli.main process --continuous

# Setup database
python -m src.cli.main setup

# Generate demo data
python scripts/demo_data.py --count 100

# Clear demo data
python scripts/demo_data.py --clear
```

### **Development Scripts**
```bash
# Quick start
make quick-start              # Unix/Linux/macOS
.\dev.ps1 quick-start        # PowerShell (Windows)
dev.bat quick-start          # Batch (Windows)

# Testing
make test                     # Run tests
make test-cov                # Run tests with coverage
make lint                     # Run linting
make format                   # Format code

# Development
make dev-setup               # Complete development setup
make dev-test                # Full test suite
make dev-run                 # Start development server

# Status and utilities
make status                  # Show project status
make env-check               # Check environment variables
make clean                   # Clean build artifacts
```

### **API Endpoints**
```bash
# Get all transactions
curl http://localhost:8000/api/v1/transactions

# Get summary statistics
curl http://localhost:8000/api/v1/summary

# Process unprocessed emails via API
curl -X POST http://localhost:8000/api/v1/process-emails

# Process recent emails (specify count)
curl -X POST "http://localhost:8000/api/v1/process-recent-emails?email_count=10"

# Get transactions by category
curl http://localhost:8000/api/v1/transactions/category/saas_subscriptions
```

### **API Documentation**
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ledger_db

# Gmail API
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Processing
EMAIL_BATCH_SIZE=50
EMAIL_POLL_INTERVAL=300
```

### **Package Configuration**
The project uses modern Python packaging with `pyproject.toml`:

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with test dependencies
pip install -e ".[test]"
```

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v
```

## 🐳 **Docker Deployment**

### **Development**
```bash
# Start all services
docker-compose up --build -d

# Start only database
docker-compose up -d db

# View logs
docker-compose logs -f app
```

### **Production**
```bash
# Build production image
docker build -t email-ledger-poc .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e OPENAI_API_KEY=your_key \
  email-ledger-poc
```

## 📊 **Data Model**

### **FinancialTransaction**
```sql
CREATE TABLE financial_transactions (
    id SERIAL PRIMARY KEY,
    email_id VARCHAR UNIQUE,
    email_subject VARCHAR,
    email_sender VARCHAR,
    email_date TIMESTAMP,
    amount DECIMAL,
    currency VARCHAR(3),
    vendor VARCHAR,
    transaction_type VARCHAR,
    reference_id VARCHAR,
    description TEXT,
    category VARCHAR,
    confidence_score DECIMAL,
    processed_at TIMESTAMP,
    is_processed BOOLEAN
);
```

## 🔧 **Development**

### **Code Quality**
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/
```

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 **Monitoring and Logging**

The application includes comprehensive logging:
- Email processing status
- AI extraction results
- Database operations
- Error handling

Logs are output to stdout and can be configured via Python's logging module.

## 🔒 **Security Considerations**

- **API Keys**: Store securely in environment variables
- **Database**: Use strong passwords and SSL connections
- **Gmail API**: Follow OAuth 2.0 best practices
- **Data Privacy**: Ensure compliance with data protection regulations

## 🚀 **Performance Optimization**

- **Batch Processing**: Configurable batch sizes
- **Database Indexing**: Automatic indexing on key fields
- **Connection Pooling**: SQLAlchemy connection management
- **Caching**: Consider Redis for high-traffic scenarios

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Gmail API Authentication**
   ```bash
   # Ensure credentials.json is in project root
   # Run application to generate token.json
   python -m src.cli.main setup
   ```

2. **Database Connection**
   ```bash
   # Check database is running
   docker-compose ps
   
   # Test connection
   python -c "from src.app.db.models import engine; print(engine.execute('SELECT 1').fetchone())"
   ```

3. **OpenAI API Issues**
   ```bash
   # Verify API key
   export OPENAI_API_KEY=your_key_here
   python -c "from src.app.services.ai_extractor import AIExtractor; AIExtractor()"
   ```
## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 **Support**

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`

## 🎯 **Architecture Highlights**

```
Gmail API → Email Processor → AI Extractor → Classification → Ledger Service → PostgreSQL
                                    ↓
                              FastAPI REST API
```

The POC successfully addresses all requirements:
- ✅ **Email Ingestion**: Gmail API integration with smart filtering
- ✅ **Data Extraction**: AI-powered extraction with fallback patterns
- ✅ **Live Ledger**: PostgreSQL database with REST API
- ✅ **Expense Classification**: AI classification
- ✅ **Production Ready**: Docker deployment, tests, documentation
- ✅ **Modern Structure**: Clean package organization with best practices
