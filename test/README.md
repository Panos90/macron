# ModaMesh™ Test Suite

This directory contains comprehensive tests for the ModaMesh™ project, testing all core components without modifying the actual codebase.

## Test Coverage

The test suite covers all major modules:

### 1. **Cost Estimation Tests** (`TestCostEstimation`)
- Monte Carlo initialization with proper parameters
- Product loading from JSON files
- Cost calculation for different products and scenarios
- Geographical scenario comparison (EU vs Asian production)

### 2. **Brand Intelligence Tests** (`TestBrandIntelligence`)
- PerplexityClient initialization
- BrandIntelligenceAgent creation
- API query mocking and response handling

### 3. **Italian Fashion Market Tests** (`TestItalianFashionMarket`)
- Market data initialization
- Brand listing and retrieval
- Market segment analysis
- Brand-segment relationship queries

### 4. **Simulation Tests** (`TestSimulation`)
- Simulation configuration
- SingleModelSimulation initialization
- Brand agent loading and management

### 5. **Integration Tests** (`TestIntegration`)
- Cost estimation to market analysis flow
- Market segmentation functionality
- Cross-module data consistency

## Running the Tests

### Prerequisites
- Python 3.12+
- pytest installed (`pip install pytest`)
- All project dependencies installed

### Run All Tests
```bash
python3 -m pytest test/test.py -v
```

### Run Specific Test Classes
```bash
# Test only cost estimation
python3 -m pytest test/test.py::TestCostEstimation -v

# Test only Italian fashion market
python3 -m pytest test/test.py::TestItalianFashionMarket -v
```

### Run Specific Test Methods
```bash
# Test Monte Carlo initialization
python3 -m pytest test/test.py::TestCostEstimation::test_monte_carlo_initialization -v
```

### Test Output Options
```bash
# Quiet mode (less output)
python3 -m pytest test/test.py -q

# Show print statements
python3 -m pytest test/test.py -s

# Short traceback format
python3 -m pytest test/test.py --tb=short
```

## Test Design Principles

1. **No Codebase Modification**: Tests work with the existing modules as-is
2. **Proper Mocking**: External dependencies (APIs, files) are mocked appropriately
3. **Fixture Management**: Test data files are copied/cleaned up automatically
4. **Comprehensive Coverage**: All major functionality is tested
5. **Integration Testing**: Cross-module interactions are verified

## Key Test Fixtures

- `setup_test_data`: Handles copying `macron_products.json` to the current directory for tests that need it, then cleans up afterward
- `setup_integration_data`: Similar fixture for integration tests

## Important Notes

- The test suite handles the fact that `cost_estimation.py` expects `macron_products.json` in the current directory (not in `data/`)
- Tests use appropriate mocking to avoid real API calls to Perplexity or other external services
- All 16 tests should pass successfully

## Test Results

Current status: ✅ **16 tests passing** (with 1 deprecation warning from LangChain that can be ignored) 