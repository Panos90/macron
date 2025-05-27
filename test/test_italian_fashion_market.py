#!/usr/bin/env python3
"""Test Italian Fashion Market module"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from italian_fashion_market import ItalianFashionMarket

def test_market_data():
    """Test loading and accessing market data"""
    print("Testing Italian Fashion Market module...")
    
    try:
        # Initialize market
        market = ItalianFashionMarket()
        
        # Test getting all brands
        all_brands = market.get_all_brands()
        print(f"✅ Loaded {len(all_brands)} brands")
        
        # Test getting segments
        all_segments = market.get_all_segments()
        print(f"✅ Loaded {len(all_segments)} segments")
        
        # Test getting a specific brand
        test_brand = "Gucci"
        brand_info = market.get_brand_segments(test_brand)
        if brand_info:
            print(f"✅ Found {test_brand} in segments: {[s.segment_name for s in brand_info.segments]}")
        else:
            print(f"❌ Failed to find {test_brand}")
            return False
            
        # Test segment brands
        test_segment = "7. Luxury Fashion"
        segment_brands = market.get_segment_brands(test_segment)
        if segment_brands:
            print(f"✅ Found {len(segment_brands)} brands in {test_segment}")
        else:
            print(f"❌ Failed to get brands for {test_segment}")
            return False
            
        print("\n✅ All Italian Fashion Market tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_test():
    """Run the test"""
    return test_market_data()

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 