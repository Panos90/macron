# ModaMesh - Italian Fashion Market Simulation Framework

ModaMesh is a multi-agent simulation system analyzing the Italian fashion market's response to Macron's B2B business models. The project consists of three main modules: Cost Estimation, Brand Intelligence, and Testing Suite.

## 🏗️ Project Structure

```
macron/
├── cost_estimation.py           # Monte Carlo cost analysis module
├── brand_intelligence_agent.py  # Direct API integration for brand intelligence
├── italian_fashion_market.py    # Italian fashion market data & utilities
├── test/                        # Testing suite
│   ├── test.py                 # Unified test runner
│   ├── test_cost_estimation.py
│   ├── test_italian_fashion_market.py
│   ├── test_single_brand.py
│   └── test_direct_api.py
├── data/                        # Data files
│   ├── macron_products.json    # Macron product definitions
│   └── italian_fashion_market.csv # Market mapping
├── product_costs/               # Cost analysis outputs (generated)
└── company_data/                # Brand intelligence outputs (generated)
```

## 📋 Requirements

```bash
pip install numpy pandas matplotlib seaborn requests
```

## 🔑 Environment Setup

For Brand Intelligence collection and testing, you MUST set the Perplexity API key:

```bash
export PERPLEXITY_API_KEY='your-perplexity-api-key'
```

## 🎯 Module 1: Cost Estimation

Monte Carlo simulation for analyzing Macron product costs across different production scenarios.

### Features
- 10 Macron product analysis (Hero, Icon, Evo, etc.)
- 3 production scenarios (Italy-only, Hybrid, Outsourced)
- Cost factor distributions with uncertainty modeling
- Visual analysis with distribution plots

### Usage
```bash
python cost_estimation.py
```

### Output
- Individual product cost distributions saved to `product_costs/`
- Comprehensive analysis report in JSON format
- Visualization screenshots for each product

## 🔍 Module 2: Brand Intelligence

Direct Perplexity API integration for gathering comprehensive market intelligence on Italian fashion brands.

### Features
- Automated data collection for 67 Italian fashion brands
- 15 intelligence categories with 80+ metrics per brand
- Robust JSON extraction handling
- Individual company data files
- Batch processing with rate limiting

### Usage
```bash
# Set API key first
export PERPLEXITY_API_KEY='your-api-key'

# Run collection
python brand_intelligence_agent.py
```

### Output
- Individual brand JSON files in `company_data/`
- Collection summary with success statistics
- Failed brands tracking

## 🧪 Module 3: Testing Suite

Unified testing framework for all modules.

### Features
- Single command to run all tests
- Environment variable validation
- Module integrity checks
- API connectivity tests

### Usage
```bash
# Set API key for brand intelligence tests
export PERPLEXITY_API_KEY='your-api-key'

# Run all tests
cd test
python test.py

# Or run individual tests
python test_cost_estimation.py
python test_italian_fashion_market.py
python test_single_brand.py
python test_direct_api.py
```

## 📊 Data Sources

### Italian Fashion Market Data
- 67 brands mapped across 7 market segments
- Functionality vs Fashion positioning (0-10 scale)
- Segment definitions from luxury to sportswear

### Macron Product Portfolio
- 10 key products with technical specifications
- Target segments and price points
- Production complexity ratings

## 🚀 Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set Perplexity API key: `export PERPLEXITY_API_KEY='your-key'`
4. Run tests: `cd test && python test.py`
5. Generate cost analysis: `python cost_estimation.py`
6. Collect brand intelligence: `python brand_intelligence_agent.py`

## 📈 Next Steps

The collected data feeds into the ModaMesh simulation engine for:
- Market entry strategy analysis
- Competitive response modeling
- Partnership opportunity identification
- Risk assessment across segments

## 📝 License

TBD

## 👥 Contributors

Panagiotis Stratis