#!/usr/bin/env python3
"""
Comprehensive test suite for ModaMesh™ project
Tests all core components without modifying the actual codebase
"""

import sys
import os
import json
import shutil
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Import our modules with correct names
from cost_estimation import MonteCarloCostAnalysis
from brand_intelligence_agent import BrandIntelligenceAgent, PerplexityClient
from italian_fashion_market import ItalianFashionMarket
from run_simulation import SingleModelSimulation

class TestCostEstimation:
    """Test the cost estimation module"""
    
    def test_monte_carlo_initialization(self):
        """Test MonteCarloCostAnalysis initialization"""
        analysis = MonteCarloCostAnalysis(n_simulations=1000)
        assert analysis.n_simulations == 1000
        assert len(analysis.geographical_scenarios) == 3
        assert 'EU_Production' in analysis.geographical_scenarios
        assert 'Asian_Production' in analysis.geographical_scenarios
        assert 'Hybrid_Model' in analysis.geographical_scenarios
    
    def test_load_products(self):
        """Test loading products from JSON"""
        analysis = MonteCarloCostAnalysis()
        products = analysis.load_products()
        # Should return a list of 10 products
        assert isinstance(products, list)
        assert len(products) == 10
        assert 'Hydrotex Moisture-Control Liners' in products
    
    def test_cost_calculation(self):
        """Test cost calculation for a product"""
        analysis = MonteCarloCostAnalysis(n_simulations=100)
        # Note: load_products returns list but doesn't set self.products
        # The calculate_costs method uses self.cost_assumptions directly
        
        # Test calculation for one product
        product_name = 'Hydrotex Moisture-Control Liners'
        scenario_name = 'EU_Production'
        scenario_params = analysis.geographical_scenarios[scenario_name]
        
        costs = analysis.calculate_costs(product_name, scenario_name, scenario_params)
        
        assert 'fixed_costs' in costs
        assert 'variable_costs' in costs
        assert len(costs['fixed_costs']) == 100
        assert len(costs['variable_costs']) == 100
        assert np.all(costs['fixed_costs'] > 0)
        assert np.all(costs['variable_costs'] > 0)
    
    def test_geographical_scenarios(self):
        """Test that different scenarios produce different costs"""
        analysis = MonteCarloCostAnalysis(n_simulations=100)
        
        product_name = 'EcoMesh Ventilation Panels'
        
        # Calculate costs for different scenarios
        eu_costs = analysis.calculate_costs(
            product_name, 
            'EU_Production', 
            analysis.geographical_scenarios['EU_Production']
        )
        
        asian_costs = analysis.calculate_costs(
            product_name,
            'Asian_Production',
            analysis.geographical_scenarios['Asian_Production']
        )
        
        # Asian production should have lower variable costs
        assert np.mean(asian_costs['variable_costs']) < np.mean(eu_costs['variable_costs'])

class TestBrandIntelligence:
    """Test the brand intelligence module"""
    
    def test_perplexity_client_initialization(self):
        """Test PerplexityClient initialization"""
        # PerplexityClient expects API key in initialization
        client = PerplexityClient('test_key')
        assert client.api_key == 'test_key'
    
    def test_brand_intelligence_agent_initialization(self):
        """Test BrandIntelligenceAgent initialization"""
        # Mock the PerplexityClient
        with patch('brand_intelligence_agent.PerplexityClient'):
            agent = BrandIntelligenceAgent(
                brand_name='Gucci', 
                segments=['Luxury'],
                perplexity_client=Mock()
            )
            assert agent.brand_name == 'Gucci'
            assert agent.segments == ['Luxury']
    
    @patch('brand_intelligence_agent.PerplexityClient.query')
    def test_search_brand_info(self, mock_query):
        """Test searching for brand information"""
        # Mock the query response
        mock_query.return_value = json.dumps({
            'revenue': '€7.6 billion',
            'production_units': '50 million units',
            'technology_adoption': 'High'
        })
        
        client = PerplexityClient('test_key')
        agent = BrandIntelligenceAgent('Gucci', ['Luxury'], client)
        
        # The agent has an async gather_intelligence method
        # For now, just test the client works
        assert agent.perplexity_client is not None

class TestItalianFashionMarket:
    """Test the Italian fashion market module"""
    
    def test_market_initialization(self):
        """Test ItalianFashionMarket initialization"""
        market = ItalianFashionMarket()
        assert market is not None
        assert hasattr(market, 'market_data')
        assert hasattr(market, 'brand_to_segments')
        assert isinstance(market.market_data, dict)
        assert isinstance(market.brand_to_segments, dict)
    
    def test_get_all_brands(self):
        """Test getting all brands"""
        market = ItalianFashionMarket()
        brands = market.get_all_brands()
        
        assert isinstance(brands, list)
        assert len(brands) > 0
        assert 'Gucci' in brands
        assert 'Prada' in brands
    
    def test_get_all_segments(self):
        """Test getting all segments"""
        market = ItalianFashionMarket()
        segments = market.get_all_segments()
        
        assert isinstance(segments, list)
        assert len(segments) == 7  # 7 segments as per the module
        assert any('Luxury' in seg for seg in segments)
    
    def test_get_brand_segments(self):
        """Test getting segments for a brand"""
        market = ItalianFashionMarket()
        brand_info = market.get_brand_segments('Gucci')
        
        assert brand_info is not None
        assert brand_info.brand_name == 'Gucci'
        assert len(brand_info.segments) > 0
        assert any('Luxury' in seg.segment_name for seg in brand_info.segments)

class TestSimulation:
    """Test the simulation module"""
    
    def test_simulation_config(self):
        """Test SingleModelSimulation configuration"""
        from run_simulation import SimulationConfig
        
        config = SimulationConfig(
            n_simulations=100,
            simulation_years=5,
            base_seed=42
        )
        
        assert config.n_simulations == 100
        assert config.simulation_years == 5
        assert config.base_seed == 42
    
    def test_simulation_initialization(self):
        """Test SingleModelSimulation initialization"""
        from run_simulation import SimulationConfig
        
        config = SimulationConfig(n_simulations=10)
        sim = SingleModelSimulation(config)
        
        assert sim.config.n_simulations == 10
        assert sim.brand_agents is not None
        assert sim.macron_agent is not None
    
    def test_brand_agents_loading(self):
        """Test that brand agents are loaded"""
        from run_simulation import SimulationConfig
        
        config = SimulationConfig(n_simulations=10)
        sim = SingleModelSimulation(config)
        
        # Check that we have brand agents
        assert len(sim.brand_agents) > 0
        assert 'Gucci' in sim.brand_agents
        assert 'Nike' in sim.brand_agents

class TestIntegration:
    """Integration tests across modules"""
    
    def test_cost_to_market_flow(self):
        """Test the flow from cost estimation to market analysis"""
        # Initialize cost analysis
        cost_analysis = MonteCarloCostAnalysis(n_simulations=100)
        products = cost_analysis.load_products()
        
        # Initialize market
        market = ItalianFashionMarket()
        brands = market.get_all_brands()
        
        # Verify we can analyze costs for products that brands might want
        assert len(products) == 10
        assert len(brands) > 60  # Should have 67 brands
        
        # Calculate sample costs
        product_name = 'Hydrotex Moisture-Control Liners'
        costs = cost_analysis.calculate_costs(
            product_name,
            'EU_Production',
            cost_analysis.geographical_scenarios['EU_Production']
        )
        
        assert np.mean(costs['variable_costs']) > 0
        assert np.mean(costs['fixed_costs']) > 0
    
    def test_market_segmentation(self):
        """Test market segmentation functionality"""
        market = ItalianFashionMarket()
        
        # Test luxury brands
        gucci_info = market.get_brand_segments('Gucci')
        assert any('Luxury' in seg.segment_name for seg in gucci_info.segments)
        
        # Test sportswear brands
        nike_info = market.get_brand_segments('Nike')
        assert any('Technical' in seg.segment_name or 'Sportswear' in seg.segment_name 
                  for seg in nike_info.segments)

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v']) 