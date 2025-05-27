# ModaMesh - Italian Fashion Market Simulation Framework

ModaMesh is a multi-agent simulation system analyzing the Italian fashion market's response to Macron's B2B business models. The project consists of three main modules: Cost Estimation, Brand Intelligence, and Testing Suite.

## 🏗️ Project Structure

```
macron/
├── cost_estimation.py           # Monte Carlo cost analysis module
├── brand_intelligence_agent.py  # LangChain agents for brand intelligence
├── italian_fashion_market.py    # Italian fashion market data & utilities
├── test/                        # Testing suite
│   ├── test.py                 # Unified test runner
│   ├── test_cost_estimation.py
│   ├── test_italian_fashion_market.py
│   ├── test_single_brand.py
│   └── test_direct_api.py
├── data/                        # Data files
│   ├── macron_products.json    # Macron product definitions
│   └── italian_fashion_market.json
├── product_costs/               # Cost analysis outputs
└── company_data/                # Brand intelligence outputs
```

## 📋 Prerequisites

- Python 3.8+
- Perplexity API key for brand intelligence module

### Environment Setup

For the Brand Intelligence module and tests, you must set the Perplexity API key:

```bash
export PERPLEXITY_API_KEY='your-api-key-here'
```

## 🧩 Module Overview

### 1. Cost Estimation Module (`cost_estimation.py`)

Performs Monte Carlo simulations to analyze production costs for 10 Macron products across 3 geographical scenarios.

**Features:**
- 100,000 Monte Carlo simulations per scenario
- Statistical distributions for cost components
- Three production scenarios: EU, Asian, and Hybrid
- Comprehensive visualizations and reports

**Usage:**
```bash
python cost_estimation.py
```

**Output:** Results saved to `product_costs/` directory:
- `analysis_YYYYMMDD_HHMMSS.json` - Full simulation data
- `executive_summary_YYYYMMDD_HHMMSS.json` - Key insights
- Visualization plots (PNG files)

### 2. Brand Intelligence Module (`brand_intelligence_agent.py`)

Collects comprehensive business intelligence for 67 Italian fashion brands using Perplexity Sonar Pro API.

**Features:**
- LangChain-based intelligent agents
- 15 intelligence categories per brand
- 80+ metrics collected
- Robust JSON extraction handling markdown/text artifacts
- 60-second timeout with 4 retries
- Individual JSON files per brand

**Usage:**
```bash
# Set API key first
export PERPLEXITY_API_KEY='your-api-key'

# Run collection
python brand_intelligence_agent.py
```

**Output:** Results saved to `company_data/` directory:
- Individual brand files: `{BrandName}.json`
- `_collection_summary.json` - Collection statistics
- `_failed_brands.json` - Any failed collections

### 3. Testing Suite (`test/`)

Comprehensive test suite for all modules with unified test runner.

**Features:**
- Environment validation
- Module functionality tests
- API connectivity tests
- Colored output for clarity

**Usage:**
```bash
# Run all tests
python test/test.py

# Run individual tests
python test/test_cost_estimation.py
python test/test_italian_fashion_market.py
python test/test_single_brand.py
python test/test_direct_api.py
```

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone [repository-url]
   cd macron
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment (for Brand Intelligence):**
   ```bash
   export PERPLEXITY_API_KEY='your-api-key'
   ```

4. **Run tests to verify setup:**
   ```bash
   python test/test.py
   ```

5. **Run cost analysis:**
   ```bash
   python cost_estimation.py
   ```

6. **Collect brand intelligence:**
   ```bash
   python brand_intelligence_agent.py
   ```

## 📊 Data Sources

- **Macron Products:** 10 innovative products across 4 categories
- **Italian Fashion Brands:** 67 brands across 7 market segments
- **Cost Models:** Statistical distributions based on industry benchmarks

## 🔍 Key Insights

The system provides:
- Production cost optimization strategies
- Market positioning intelligence
- Competitive dynamics analysis
- Partnership opportunity identification

## 📝 License

[Your License Here]

## 👥 Contributors

[Your Contributors Here] 