#!/usr/bin/env python3
"""Test direct Perplexity API for brand intelligence"""

import os
import sys
import json
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_perplexity_api(brand_name="Gucci"):
    """Test Perplexity API directly"""
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ Error: PERPLEXITY_API_KEY environment variable not set!")
        print("💡 Please set: export PERPLEXITY_API_KEY='your-api-key'")
        return False
    
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    system_prompt = f"""You are a JSON data extraction specialist. You MUST respond ONLY with valid JSON - no explanations, no markdown, no additional text. Research {brand_name} and provide accurate business intelligence data."""
    
    user_prompt = f"""Research {brand_name} and return ONLY this JSON with real data:
{{
  "brand_name": "{brand_name}",
  "annual_revenue_millions": 0,
  "years_in_business": 0,
  "headquarter_italy": 0,
  "segment": ""
}}"""
    
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }
    
    print(f"🔍 Testing Perplexity API for {brand_name}...")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        print(f"✅ API Response received")
        print(f"\nRaw response:\n{content}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(content)
            print(f"\n✅ Successfully parsed JSON:")
            print(json.dumps(parsed, indent=2))
            
            # Save to output
            test_output_dir = os.path.join(os.path.dirname(__file__), 'output')
            os.makedirs(test_output_dir, exist_ok=True)
            
            with open(os.path.join(test_output_dir, 'test_direct_api_result.json'), 'w') as f:
                json.dump(parsed, f, indent=2)
            
            return True
        except json.JSONDecodeError as e:
            print(f"\n❌ Failed to parse JSON: {e}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False

def run_test():
    """Run the test"""
    return test_perplexity_api("Gucci")

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1) 