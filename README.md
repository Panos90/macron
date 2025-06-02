# ModaMesh™ - Multi-Agent Fashion Market Simulation

ModaMesh™ simulates how Italian fashion brands would respond to Macron's B2B technical component business models (co-branded vs white-label).

## 🚀 Quick Start

### 1. Clone & Install

```bash
# Clone the repository
git clone <repository-url>
cd macron

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Simulation (No API Key Needed!)

```bash
# Run the main simulation using pre-computed data
python run_simulation.py
```

This uses our pre-computed brand intelligence snapshot from `company_data/` - no API keys required!

---

## 📦 Dependencies

Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:
```bash
pip install -r requirements.txt
```

Key dependencies:
- `numpy>=1.24.0` - Numerical computations
- `pandas>=2.0.0` - Data analysis
- `matplotlib>=3.7.0` - Visualizations
- `seaborn>=0.12.0` - Statistical plots
- `requests>=2.31.0` - API calls
- `aiohttp>=3.9.0` - Async HTTP
- `langchain>=0.1.0` - Agent framework
- `pytest>=8.0.0` - Testing framework

---

## 🏗️ Project Structure

```
macron/
├── run_simulation.py            # 🎯 MAIN ENTRY POINT - Run this!
├── cost_estimation.py           # Monte Carlo cost analysis
├── italian_fashion_market.py    # Market segmentation data
├── brand_intelligence_agent.py  # Perplexity API integration
├── visualize_results.py         # Results visualization tools
│
├── agents/                      # Simulation agents
│   ├── __init__.py             # Package initialization
│   ├── brand_agent.py          # Individual brand decision-making
│   ├── macron_agent.py         # Macron's capacity management
│   ├── market_state_manager.py # Market dynamics & evolution
│   └── simulation_orchestrator.py # Simulation coordination
│
├── data/                        # Input data
│   ├── macron_products.json    # 10 technical products
│   └── italian_fashion_market.json  # 67 brands, 7 segments
│
├── company_data/                # 📌 PRE-COMPUTED brand intelligence
│   └── *.json                  # Individual brand profiles
│
├── simulation_results/          # Output from simulations
│   └── simulation_*.json       # Detailed results per run
│
├── product_costs/               # Cost analysis outputs
│   └── analysis_*.json         # Monte Carlo cost estimates
│
├── test/                        # Test suite
│   ├── test.py                 # Main test file
│   └── README.md               # Test documentation
│
├── slides/                      # Presentation materials
│
└── 📚 Documentation Files:
    ├── README.md               # This file - Getting started guide
    ├── EXECUTIVE_SUMMARY.md    # Strategic recommendations & results
    ├── ARCHITECTURE.md         # Technical implementation details
    ├── ASSUMPTIONS.md          # All simulation assumptions documented
    ├── BUSINESS_MODELS.md      # Co-branded vs White-label definitions
    ├── MARKETING_MIX.md        # 4Ps analysis for both models
    ├── PORTER.md               # Porter's 5 Forces analysis
    ├── VALUE_CHAIN.md          # Value chain analysis
    └── SWOT.md                 # SWOT analysis for Macron
```

---

## 📚 Documentation Guide

### Core Documentation

1. **EXECUTIVE_SUMMARY.md** - Start here for strategic insights
   - Simulation results summary
   - Key findings and recommendations
   - Financial projections comparison

2. **ARCHITECTURE.md** - Technical deep dive
   - System design and algorithms
   - Agent behavior models
   - Monte Carlo methodology

3. **ASSUMPTIONS.md** - All simulation assumptions
   - Financial & economic assumptions
   - Market behavior assumptions
   - Production & capacity constraints
   - Cost modeling distributions

### Strategic Analysis Documents

4. **BUSINESS_MODELS.md** - Partnership model definitions
   - Co-branded "Powered by Macron" model
   - White-label private manufacturing model
   - Value propositions for each

5. **MARKETING_MIX.md** - 4Ps analysis
   - Product, Price, Place, Promotion strategies
   - Comparison between both models
   - Market positioning approach

6. **PORTER.md** - Industry analysis
   - Five Forces framework applied
   - Competitive dynamics assessment
   - Strategic positioning insights

7. **VALUE_CHAIN.md** - Value creation analysis
   - Primary and support activities
   - Value capture mechanisms
   - Partnership synergies

8. **SWOT.md** - Strategic position assessment
   - Strengths & Weaknesses (internal)
   - Opportunities & Threats (external)
   - Strategic implications

---

## 📊 Module Execution Order

### Option A: Use Pre-Computed Data (Recommended)
```bash
# 1. Just run the simulation!
python run_simulation.py

# 2. View results
cat EXECUTIVE_SUMMARY.md

# 3. Visualize results (optional)
python visualize_results.py
```

### Option B: Fresh Data Collection (Requires API Key)
```bash
# 1. Set Perplexity API key
export PERPLEXITY_API_KEY='your-api-key-here'

# 2. Collect fresh brand intelligence (optional - we have snapshot)
python brand_intelligence_agent.py

# 3. Run cost analysis (optional - already integrated)
python cost_estimation.py

# 4. Run main simulation
python run_simulation.py

# 5. Generate visualizations
python visualize_results.py
```

---

## 🔧 Key Modules Explained

### 1. **Main Simulation** (`run_simulation.py`)
- Runs 20,000 Monte Carlo simulations (10,000 per model)
- Simulates 5-year partnership lifecycle
- Models 67 Italian fashion brands' decisions
- Includes market shocks and dynamics
- **Runtime:** ~2-3 minutes

### 2. **Cost Estimation** (`cost_estimation.py`)
- Analyzes 10 Macron products across 3 geographical scenarios
- Uses 100,000 Monte Carlo simulations per scenario
- Models cost distributions (log-normal, beta, triangular, etc.)
- **Already integrated** into main simulation

### 3. **Brand Intelligence** (`brand_intelligence_agent.py`)
- Collects real-time data via Perplexity API
- **Not needed** - we provide pre-computed snapshot
- Gathers 40+ metrics per brand
- Only use if you want fresh market data

### 4. **Market Data** (`italian_fashion_market.py`)
- Maps 67 brands across 7 market segments
- Provides brand-segment relationships
- Fashion vs. Function scoring (1-10 scale)
- Automatically loaded by simulation

### 5. **Visualization** (`visualize_results.py`)
- Creates charts and graphs from simulation results
- Profit comparisons, capacity utilization, brand adoption
- Exports publication-ready figures

### 6. **Agent System** (`agents/`)
- **brand_agent.py**: Individual brand decision logic
- **macron_agent.py**: Macron's pricing and capacity optimization
- **market_state_manager.py**: Market evolution and shocks
- **simulation_orchestrator.py**: Coordinates all agents

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest test/test.py -v

# Run specific test suites
python -m pytest test/test.py::TestCostEstimation -v
python -m pytest test/test.py::TestItalianFashionMarket -v
python -m pytest test/test.py::TestSimulation -v
```

---

## 📈 Understanding the Results

After running the simulation, check:

1. **Console Output** - Real-time simulation progress and summary
2. **EXECUTIVE_SUMMARY.md** - Strategic recommendations
3. **simulation_results/` folder** - Detailed JSON data
4. **Visualization outputs** - Charts and graphs (if generated)

Key metrics to look for:
- **Profit margins**: Co-branded (26.5%) vs White-label (6.8%)
- **NPV comparison**: Which model creates more long-term value
- **Capacity utilization**: How efficiently each model uses production
- **Brand adoption**: Number and quality of partnerships
- **Market evolution**: How preferences shift over 5 years

---

## 🔑 Perplexity API (Optional)

Only needed if you want to refresh brand intelligence data:

1. Get API key from [Perplexity.ai](https://www.perplexity.ai)
2. Set environment variable:
   ```bash
   export PERPLEXITY_API_KEY='pplx-xxxxxxxxxxxxx'
   ```
3. Run brand intelligence collection:
   ```bash
   python brand_intelligence_agent.py
   ```

**Note:** The simulation works perfectly with our pre-computed snapshot. Fresh data collection takes ~30 minutes and may have API costs.

---

## ⚡ Quick Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt
```

### "API key not found"
You don't need an API key! The simulation uses pre-computed data. Only set the key if collecting fresh data.

### Memory issues
Reduce simulation count in `run_simulation.py`:
```python
config = SimulationConfig(n_simulations=1000)  # Instead of 10000
```

### Results not updating
Delete old results and re-run:
```bash
rm -rf simulation_results/*
python run_simulation.py
```

---

## 📝 Key Insights

The simulation reveals that despite lower revenue, the **co-branded model delivers 1.5x more profit** due to:
- Premium positioning (26.5% margins vs 6.8%)
- Better alignment with luxury brands
- Higher value per unit (€12 vs €3 profit/unit)
- Strategic capacity flexibility

Read `EXECUTIVE_SUMMARY.md` for full strategic recommendations.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests: `python -m pytest test/test.py`
4. Submit a pull request

---

## 📄 License

© 2024 Macron S.p.A. - Simulation Framework