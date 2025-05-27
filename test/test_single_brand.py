#!/usr/bin/env python3
"""Test the improved brand intelligence agent with a single brand"""

import os
import sys
import asyncio
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brand_intelligence_agent import BrandIntelligenceAgent, PerplexityClient
from italian_fashion_market import ItalianFashionMarket

async def test_single_brand(brand_name: str = "Gucci"):
    """Test intelligence gathering for a single brand"""
    # Initialize
    market = ItalianFashionMarket()
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ Error: PERPLEXITY_API_KEY environment variable not set!")
        print("💡 Please set: export PERPLEXITY_API_KEY='your-api-key'")
        return False
    
    perplexity_client = PerplexityClient(api_key)
    
    # Get brand segments
    brand_info = market.get_brand_segments(brand_name)
    if not brand_info:
        print(f"Brand {brand_name} not found!")
        return False
    
    segments = [seg.segment_name for seg in brand_info.segments]
    print(f"Testing {brand_name} in segments: {segments}")
    
    # Create agent and gather intelligence
    agent = BrandIntelligenceAgent(brand_name, segments, perplexity_client)
    result = await agent.gather_intelligence()
    
    if result:
        print(f"\n✅ Successfully gathered intelligence for {brand_name}")
        print(f"Data source: {result.get('_data_source', 'unknown')}")
        print(f"Segment IDs: {result['market_position']['segment_id']}")
        print(f"Revenue: ${result['financial_data']['annual_revenue_millions']}M")
        print(f"Years in business: {result['company_basics']['years_in_business']}")
        
        # Save to file for inspection
        test_output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(test_output_dir, exist_ok=True)
        
        with open(os.path.join(test_output_dir, f'test_result_{brand_name.lower().replace(" ", "_")}.json'), 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull result saved to test/output/test_result_{brand_name.lower().replace(' ', '_')}.json")
        return True
    else:
        print(f"\n❌ Failed to gather intelligence for {brand_name}")
        return False

async def run_test():
    """Run the test and return success status"""
    # Test with a brand that previously failed due to markdown
    return await test_single_brand("Columbia")

if __name__ == "__main__":
    # Run test
    success = asyncio.run(run_test())
    sys.exit(0 if success else 1) 