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
├── agents/                      # Simulation agents
│   ├── brand_agent.py          # Individual brand decision-making
│   └── macron_agent.py         # Macron's capacity management
├── data/                        # Input data
│   ├── macron_products.json    # 10 technical products
│   └── italian_fashion_market.json  # 67 brands, 7 segments
├── company_data/                # 📌 PRE-COMPUTED brand intelligence
│   └── *.json                  # Individual brand profiles
├── simulation_results/          # Output from simulations
└── test/                        # Test suite
    └── test.py                 # Run all tests
```

---

## 📊 Module Execution Order

### Option A: Use Pre-Computed Data (Recommended)
```bash
# 1. Just run the simulation!
python run_simulation.py

# 2. View results
cat EXECUTIVE_SUMMARY.md
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
```

---

## 🔧 Key Modules Explained

### 1. **Main Simulation** (`run_simulation.py`)
- Runs 20,000 Monte Carlo simulations
- Compares co-branded vs white-label models
- Outputs financial projections and recommendations
- **Runtime:** ~2 minutes

### 2. **Cost Estimation** (`cost_estimation.py`)
- Analyzes 10 Macron products across 3 geographical scenarios
- Uses 100,000 Monte Carlo simulations per scenario
- **Already integrated** into main simulation

### 3. **Brand Intelligence** (`brand_intelligence_agent.py`)
- Collects real-time data via Perplexity API
- **Not needed** - we provide pre-computed snapshot
- Only use if you want fresh market data

### 4. **Market Data** (`italian_fashion_market.py`)
- Maps 67 brands across 7 market segments
- Provides brand-segment relationships
- Automatically loaded by simulation

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
3. **ARCHITECTURE.md** - Technical implementation details
4. **simulation_results/` folder** - Detailed JSON data

Key metrics to look for:
- **Profit margins**: Co-branded (26.5%) vs White-label (6.8%)
- **NPV comparison**: Which model creates more long-term value
- **Capacity utilization**: How efficiently each model uses production
- **Brand adoption**: Number and quality of partnerships

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