#!/usr/bin/env python3
"""
ModaMesh Test Suite
==================
Runs all tests for the ModaMesh project modules.
"""

import os
import sys
import asyncio
import subprocess
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestSuite:
    """Unified test suite for ModaMesh"""
    
    def __init__(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.test_dir)
        self.results = []
        
    def print_header(self):
        """Print test suite header"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}ModaMesh Test Suite{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
    def print_footer(self):
        """Print test suite results"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}Test Results{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        passed = sum(1 for r in self.results if r['passed'])
        failed = len(self.results) - passed
        
        for result in self.results:
            status = f"{GREEN}✅ PASSED{RESET}" if result['passed'] else f"{RED}❌ FAILED{RESET}"
            print(f"{result['name']}: {status}")
            
        print(f"\n{BLUE}Summary:{RESET}")
        print(f"  Total: {len(self.results)}")
        print(f"  {GREEN}Passed: {passed}{RESET}")
        print(f"  {RED}Failed: {failed}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        return failed == 0
        
    def check_environment(self):
        """Check if required environment variables are set"""
        print(f"{YELLOW}🔍 Checking environment...{RESET}")
        
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            print(f"{RED}❌ PERPLEXITY_API_KEY not set!{RESET}")
            print(f"{YELLOW}💡 Please set: export PERPLEXITY_API_KEY='your-api-key'{RESET}")
            return False
        else:
            print(f"{GREEN}✅ PERPLEXITY_API_KEY is set{RESET}")
            return True
            
    def run_test(self, test_name, test_file):
        """Run a single test file"""
        print(f"\n{YELLOW}🧪 Running {test_name}...{RESET}")
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, os.path.join(self.test_dir, test_file)],
                capture_output=True,
                text=True,
                cwd=self.parent_dir
            )
            
            # Check if test passed
            passed = result.returncode == 0
            
            if passed:
                print(f"{GREEN}✅ {test_name} passed!{RESET}")
            else:
                print(f"{RED}❌ {test_name} failed!{RESET}")
                if result.stdout:
                    print(f"Output:\n{result.stdout}")
                if result.stderr:
                    print(f"Error:\n{result.stderr}")
                    
            self.results.append({
                'name': test_name,
                'passed': passed,
                'output': result.stdout,
                'error': result.stderr
            })
            
            return passed
            
        except Exception as e:
            print(f"{RED}❌ Error running {test_name}: {e}{RESET}")
            self.results.append({
                'name': test_name,
                'passed': False,
                'output': '',
                'error': str(e)
            })
            return False
            
    def run_all_tests(self):
        """Run all tests in the suite"""
        self.print_header()
        
        # Check environment first
        if not self.check_environment():
            print(f"\n{RED}❌ Environment check failed. Exiting.{RESET}")
            return False
            
        # Define all tests
        tests = [
            ("Italian Fashion Market", "test_italian_fashion_market.py"),
            ("Direct API Test", "test_direct_api.py"),
            ("Single Brand Intelligence", "test_single_brand.py"),
            ("Cost Estimation", "test_cost_estimation.py"),
        ]
        
        # Run each test
        for test_name, test_file in tests:
            if os.path.exists(os.path.join(self.test_dir, test_file)):
                self.run_test(test_name, test_file)
            else:
                print(f"{YELLOW}⚠️  Skipping {test_name} - file not found: {test_file}{RESET}")
                
        # Print results
        all_passed = self.print_footer()
        
        return all_passed

def main():
    """Main entry point"""
    suite = TestSuite()
    success = suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 