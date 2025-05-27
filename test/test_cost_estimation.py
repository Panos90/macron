#!/usr/bin/env python3
"""Test Cost Estimation module"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_cost_estimation():
    """Test cost estimation module"""
    print("Testing Cost Estimation module...")
    
    try:
        # Check if the module exists
        import cost_estimation
        print("✅ Cost estimation module imported successfully")
        
        # Check if required data files exist
        data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'macron_products.json')
        if os.path.exists(data_file):
            print("✅ Macron products data file exists")
        else:
            # Try alternative location
            alt_data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'macron_products.json')
            if os.path.exists(alt_data_file):
                print("✅ Macron products data file exists (alternative location)")
            else:
                print("❌ Macron products data file not found")
                return False
            
        # Check if the module has required classes/functions
        required_attrs = ['MonteCarloCostAnalysis']
        for attr in required_attrs:
            if hasattr(cost_estimation, attr):
                print(f"✅ Found {attr} in module")
            else:
                print(f"❌ Missing {attr} in module")
                return False
        
        # Test instantiation
        try:
            analyzer = cost_estimation.MonteCarloCostAnalysis(n_simulations=100)
            print("✅ MonteCarloCostAnalysis instantiated successfully")
            
            # Check if it has required methods
            required_methods = ['load_products', 'calculate_costs', 'run_analysis']
            for method in required_methods:
                if hasattr(analyzer, method):
                    print(f"✅ Found method: {method}")
                else:
                    print(f"❌ Missing method: {method}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to instantiate MonteCarloCostAnalysis: {e}")
            return False
                
        print("\n✅ All Cost Estimation tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import cost_estimation: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_test():
    """Run the test"""
    return test_cost_estimation()

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 