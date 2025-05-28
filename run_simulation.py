#!/usr/bin/env python3
"""
MODAMESH SINGLE MODEL SIMULATION WITH CAPACITY CONSTRAINTS
==========================================================
Runs Monte Carlo simulations where Macron must choose EITHER co-branded OR white-label
and can only allocate 50% of production capacity to the new business model.
"""

import sys
sys.path.append('.')

import json
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import logging
from tqdm import tqdm
import pandas as pd

from agents import (
    BrandAgent, 
    MacronAgent,
    MarketStateManager,
    load_all_brand_agents,
    load_macron_agent
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class ProductionCapacity:
    """Production capacity constraints for Macron"""
    # Total annual capacity (units)
    total_annual_capacity: int = 2_000_000  # 2M units/year estimated
    
    # Allocation to new business model (50% of total)
    new_model_allocation: float = 0.5
    
    # Product complexity capacity allocation - now represents max allocation per product type
    # NOT a division of total capacity
    complexity_max_share: Dict[str, float] = field(default_factory=lambda: {
        'Low': 0.5,      # Can use up to 50% of total for low complexity
        'Medium': 0.4,   # Can use up to 40% of total for medium complexity  
        'High': 0.3,     # Can use up to 30% of total for high complexity
        'Very High': 0.2 # Can use up to 20% of total for very high complexity
    })
    
    def get_available_capacity(self) -> int:
        """Get total capacity available for new business model"""
        return int(self.total_annual_capacity * self.new_model_allocation)
    
    def get_product_capacity(self, complexity: str) -> int:
        """Get maximum capacity for a specific product complexity level"""
        available = self.get_available_capacity()
        # Each product can use up to its max share of total capacity
        return int(available * self.complexity_max_share.get(complexity, 0.3))


@dataclass
class SimulationConfig:
    """Configuration for the single model simulation"""
    n_simulations: int = 10000
    simulation_years: int = 5
    months_per_year: int = 12
    
    # Partnership parameters - more realistic
    min_units_per_product: int = 2000  # Reduced from 5000
    max_units_per_product: int = 200000  # Increased to accommodate 5% of large brands' production
    
    # Production capacity
    production_capacity: ProductionCapacity = field(default_factory=ProductionCapacity)
    
    # Market shock parameters
    max_shocks_per_simulation: int = 4
    available_shocks: List[str] = field(default_factory=lambda: [
        'recession',
        'sustainability_push',
        'tech_boom',
        'luxury_crisis',
        'luxury_tech_convergence',
        'athleisure_surge',
        'supply_chain_crisis',
        'digital_transformation',
        'gen_z_takeover',
        'performance_fashion'
    ])
    
    # Financial parameters
    discount_rate: float = 0.08  # 8% annual discount rate
    
    # Random seed for reproducibility
    base_seed: int = 42


@dataclass
class PartnershipDeal:
    """Represents an active partnership deal"""
    brand_name: str
    model: str  # 'co-branded' or 'white-label'
    start_month: int
    end_month: int
    products: Dict[str, Dict[str, float]]  # product -> {'units': X, 'price': Y, 'cost': Z}
    monthly_revenue: float
    monthly_profit: float  # Profit after COGP
    segment: int  # Primary segment of the brand
    annual_units: int  # Total units per year for capacity tracking


@dataclass
class CapacityTracker:
    """Tracks production capacity usage"""
    annual_capacity: Dict[str, int] = field(default_factory=dict)  # product -> available units
    committed_capacity: Dict[str, int] = field(default_factory=dict)  # product -> used units
    
    def initialize_annual_capacity(self, products: List[str], product_complexity: Dict[str, str], 
                                  production_capacity: ProductionCapacity):
        """Initialize capacity for each product based on complexity"""
        for product in products:
            complexity = product_complexity.get(product, 'Medium')
            self.annual_capacity[product] = production_capacity.get_product_capacity(complexity)
            self.committed_capacity[product] = 0
    
    def check_capacity(self, product: str, units: int) -> bool:
        """Check if capacity is available for the requested units"""
        available = self.annual_capacity.get(product, 0) - self.committed_capacity.get(product, 0)
        return units <= available
    
    def commit_capacity(self, product: str, units: int):
        """Commit capacity for a product"""
        self.committed_capacity[product] = self.committed_capacity.get(product, 0) + units
    
    def release_capacity(self, product: str, units: int):
        """Release capacity when partnership ends"""
        self.committed_capacity[product] = max(0, self.committed_capacity.get(product, 0) - units)
    
    def get_utilization(self) -> float:
        """Get overall capacity utilization percentage"""
        total_capacity = sum(self.annual_capacity.values())
        total_used = sum(self.committed_capacity.values())
        return (total_used / total_capacity * 100) if total_capacity > 0 else 0


class SingleModelSimulation:
    """Simulation engine for single model choice with capacity constraints"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.total_months = config.simulation_years * config.months_per_year
        
        # Load agents
        print("📚 Loading agents...")
        self.brand_agents = load_all_brand_agents()
        self.macron_agent = load_macron_agent()
        
        # Load product costs from cost estimation
        self._load_product_costs()
        
        print(f"✅ Loaded {len(self.brand_agents)} brands and {len(self.product_list)} products")
        print(f"🏭 Production capacity: {config.production_capacity.get_available_capacity():,} units/year for new model")
    
    def _load_product_costs(self):
        """Load product costs from the cost estimation results"""
        # Find the most recent cost analysis file
        cost_files = list(Path("product_costs").glob("analysis_*.json"))
        if not cost_files:
            raise FileNotFoundError("No cost analysis files found in product_costs/")
        
        latest_file = sorted(cost_files)[-1]
        
        with open(latest_file, 'r') as f:
            cost_data = json.load(f)
        
        # Extract product list and hybrid scenario costs
        self.product_list = []
        self.product_costs = {}
        self.product_complexity = {}
        
        # Use Asian production costs for competitive pricing
        asian_products = cost_data['scenarios']['Asian_Production']['products']
        
        for product_name, product_data in asian_products.items():
            self.product_list.append(product_name)
            
            # Use variable cost only (fixed costs amortized separately)
            variable_cost = product_data['variable_costs']['mean']
            
            self.product_costs[product_name] = {
                'variable_cost': variable_cost,
                'fixed_cost_per_unit': product_data['fixed_costs']['mean'] / (100000 * 5)  # Amortized over 5 years
            }
            
            # Store complexity for capacity allocation
            self.product_complexity[product_name] = product_data.get('complexity', 'Medium')
    
    def _generate_market_shocks(self, seed: int) -> List[Dict[str, Any]]:
        """Generate random market shocks for a simulation"""
        random.seed(seed)
        
        n_shocks = random.randint(0, self.config.max_shocks_per_simulation)
        shocks = []
        
        for _ in range(n_shocks):
            shock_month = random.randint(6, self.total_months - 12)
            shock_type = random.choice(self.config.available_shocks)
            duration = random.randint(3, 8)  # 3-8 quarters
            intensity = random.uniform(0.4, 0.8)
            
            shocks.append({
                'month': shock_month,
                'type': shock_type,
                'duration': duration,
                'intensity': intensity
            })
        
        shocks.sort(key=lambda x: x['month'])
        return shocks
    
    def _calculate_pricing(self, product: str, units: int, model: str, brand: BrandAgent) -> float:
        """Calculate pricing based on model and brand characteristics"""
        base_cost = self.product_costs[product]['variable_cost']
        
        if model == 'co-branded':
            # More competitive co-branded pricing while maintaining premium
            base_margin = 0.28  # Reduced from 35% to 28% base margin
            
            # Brand value premium (based on market leader score) - reduced
            brand_premium = 0.06 * brand.market_leader_score  # Use market_leader_score instead
            
            # Segment premium - adjusted for pragmatism
            segment_premiums = {
                1: 0.0,   # Core Technical - no premium
                2: 0.02,  # Outdoor Technical - small premium
                3: 0.03,  # Athleisure
                4: 0.05,  # Luxury Activewear - reduced from higher
                5: 0.07,  # Athluxury
                6: 0.10,  # High-Performance Luxury
                7: 0.12   # Luxury Fashion - highest but reduced
            }
            primary_segment = brand.segment_id[0] if brand.segment_id else 3
            segment_premium = segment_premiums.get(primary_segment, 0.03)
            
            # Marketing investment factor - reduced
            marketing_factor = 0.03  # Reduced from 5% to 3%
            
            total_markup = 1 + base_margin + brand_premium + segment_premium + marketing_factor
            
            # Volume discount for larger orders (new - to encourage volume)
            if units > 30000:
                total_markup *= 0.95  # 5% discount for high volume
            elif units > 20000:
                total_markup *= 0.97  # 3% discount for medium-high volume
            
            return base_cost * total_markup
            
        else:  # white-label
            # White-label pricing
            base_margin = 0.14  # 14% base margin for white-label
            
            # Volume-based adjustments for white-label
            if units < 5000:
                volume_adjustment = 0.0
            elif units < 10000:
                volume_adjustment = -0.02
            elif units < 25000:
                volume_adjustment = -0.05
            else:
                volume_adjustment = -0.08
            
            final_margin = base_margin + volume_adjustment
            
            return base_cost * (1 + final_margin)
    
    def _calculate_brand_demand(self, brand: BrandAgent, model: str) -> Tuple[int, Dict[str, float]]:
        """Calculate demand from a brand based on their characteristics"""
        # Estimate brand's total production units
        # Using revenue and average price index to estimate units
        # avg_price_index represents average selling price of their products
        estimated_annual_units = (brand.annual_revenue_millions * 1_000_000) / brand.avg_price_index
        
        # For co-branded partnership: 1% of production for new line
        # For white-label: slightly higher as it's operational support
        if model == 'co-branded':
            base_demand_percentage = 0.01  # 1% of production
        else:
            base_demand_percentage = 0.015  # 1.5% for white-label (more volume)
        
        # Calculate base units from percentage of production
        base_units = int(estimated_annual_units * base_demand_percentage)
        
        # Apply segment adjustments - luxury brands might allocate less percentage
        segment_adjustments = {
            1: 1.0,   # Core Technical - full allocation
            2: 1.0,   # Outdoor Technical - full allocation
            3: 0.9,   # Athleisure - slightly less
            4: 0.7,   # Luxury Activewear - smaller capsule collections
            5: 0.6,   # Athluxury - smaller collections
            6: 0.5,   # High-Performance Luxury - exclusive lines
            7: 0.4    # Luxury Fashion - very exclusive
        }
        
        primary_segment = brand.segment_id[0] if brand.segment_id else 3
        segment_adjustment = segment_adjustments.get(primary_segment, 0.8)
        
        # Apply adjustments
        adjusted_units = int(base_units * segment_adjustment)
        
        # Add some randomness for realistic variation (±20%)
        final_units = int(adjusted_units * random.uniform(0.8, 1.2))
        
        # Apply min/max constraints
        final_units = max(1000, final_units)  # Minimum 1000 units
        final_units = min(final_units, self.config.max_units_per_product)
        
        # Log for debugging
        logger.debug(f"{brand.brand_name}: Revenue €{brand.annual_revenue_millions}M, "
                    f"Avg Price €{brand.avg_price_index}, Est. Units {estimated_annual_units:,.0f}, "
                    f"Base Demand ({base_demand_percentage*100}%): {base_units:,}, "
                    f"Final: {final_units:,}")
        
        # Return the DESIRED units - actual allocation will be decided by Macron based on capacity
        return final_units, None  # Return None for now, will allocate products later
    
    def _macron_capacity_allocation(self, brand_name: str, desired_units: int, model: str, 
                                  capacity_tracker: CapacityTracker, brand: BrandAgent) -> Tuple[int, Dict[str, float]]:
        """
        Macron decides how many units to actually offer based on available capacity
        and strategic priorities
        """
        # Strategic priority scoring for brands
        priority_score = 0.0
        
        # Revenue size factor (bigger brands get some priority)
        revenue_factor = min(brand.annual_revenue_millions / 1000, 2.0)  # Cap at 2x
        priority_score += revenue_factor * 0.3
        
        # Segment priority (luxury segments get higher priority for co-branded)
        primary_segment = brand.segment_id[0] if brand.segment_id else 3
        if model == 'co-branded':
            segment_priority = {
                7: 2.0,  # Luxury Fashion - highest priority
                6: 1.8,  # High-Performance Luxury
                5: 1.5,  # Athluxury
                4: 1.2,  # Luxury Activewear
                3: 1.0,  # Athleisure
                2: 0.9,  # Outdoor Technical
                1: 0.8   # Core Technical
            }
        else:  # white-label
            segment_priority = {
                1: 1.5,  # Core Technical - high volume priority
                2: 1.4,  # Outdoor Technical
                3: 1.3,  # Athleisure
                4: 1.0,  # Luxury Activewear
                5: 0.8,  # Athluxury
                6: 0.6,  # High-Performance Luxury
                7: 0.4   # Luxury Fashion - low priority for white-label
            }
        priority_score += segment_priority.get(primary_segment, 1.0) * 0.4
        
        # Brand strength factor
        priority_score += brand.market_leader_score * 0.3
        
        # Check available capacity across all products
        total_available = 0
        product_availability = {}
        
        for product in self.product_list:
            complexity = self.product_complexity.get(product, 'Medium')
            max_capacity = self.config.production_capacity.get_product_capacity(complexity)
            used_capacity = capacity_tracker.committed_capacity.get(product, 0)
            available = max_capacity - used_capacity
            product_availability[product] = available
            total_available += available
        
        # If no capacity available, reject
        if total_available == 0:
            return 0, {}
        
        # Macron's allocation strategy: 
        # - Never allocate more than 20% of remaining capacity to a single brand
        # - For co-branded: max 50,000 units per brand to maintain exclusivity
        # - For white-label: max 100,000 units per brand
        max_allocation_ratio = 0.2
        capacity_cap = int(total_available * max_allocation_ratio)
        
        if model == 'co-branded':
            model_cap = 50000
        else:
            model_cap = 100000
        
        # Final allocation decision
        allocated_units = min(desired_units, capacity_cap, model_cap)
        
        # Apply priority score to potentially increase allocation for high-priority brands
        if priority_score > 1.5:
            allocated_units = int(allocated_units * min(priority_score, 1.3))
        
        # Ensure minimum viable order
        if allocated_units < 1000:
            return 0, {}
        
        # Now allocate across products based on availability
        product_allocation = self._allocate_products_to_brand(brand, allocated_units)
        
        # Verify we can actually fulfill this allocation
        final_allocation = {}
        for product, units in product_allocation.items():
            if product_availability.get(product, 0) >= units:
                final_allocation[product] = units
            else:
                # Partial allocation if needed
                available = product_availability.get(product, 0)
                if available >= 1000:  # Minimum viable for a product
                    final_allocation[product] = available
        
        # If we couldn't allocate meaningfully, reject
        total_allocated = sum(final_allocation.values())
        if total_allocated < 1000:
            return 0, {}
        
        return total_allocated, final_allocation
    
    def _allocate_products_to_brand(self, brand: BrandAgent, total_units: int) -> Dict[str, float]:
        """Allocate total units across different products based on brand profile"""
        allocation = {}
        
        # Define product categories
        technical_products = [p for p in self.product_list if 'Hydrotex' in p or 'PCM' in p or 'HD' in p]
        structural_products = [p for p in self.product_list if 'Jacquard' in p or 'Bonding' in p or 'Magnetic' in p or 'Drawstring' in p]
        sustainable_products = [p for p in self.product_list if 'Recycled' in p or 'Bio' in p or 'Eco' in p]
        
        weights = {}
        
        for product in self.product_list:
            weight = 1.0
            
            if product in technical_products:
                weight *= (1 + (0.8 - brand.technical_capability))
            
            if product in sustainable_products:
                weight *= (1 + brand.sustainability_score)
            
            if brand.segment_id and 7 in brand.segment_id:
                if self.product_complexity.get(product, 'Medium') in ['High', 'Very High']:
                    weight *= 1.5
            
            weights[product] = weight
        
        # Select 1-4 products
        n_products = random.randint(1, min(4, len(self.product_list)))
        selected_products = random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=n_products
        )
        
        # Distribute units
        remaining_units = total_units
        for i, product in enumerate(selected_products):
            if i == len(selected_products) - 1:
                allocation[product] = remaining_units
            else:
                units = int(remaining_units * random.uniform(0.2, 0.5))
                allocation[product] = units
                remaining_units -= units
        
        return allocation
    
    def run_single_simulation(self, simulation_id: int, model: str) -> Dict[str, Any]:
        """Run a single 5-year simulation for a specific model"""
        # Set random seed
        seed = self.config.base_seed + simulation_id
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize capacity tracker
        capacity_tracker = CapacityTracker()
        capacity_tracker.initialize_annual_capacity(
            self.product_list, 
            self.product_complexity,
            self.config.production_capacity
        )
        
        # Initialize market state manager
        market_manager = MarketStateManager(initial_seed=seed)
        
        # Generate market shocks
        market_shocks = self._generate_market_shocks(seed)
        shock_index = 0
        
        # Track metrics
        active_partnerships = []
        monthly_revenues = np.zeros(self.total_months)
        monthly_profits = np.zeros(self.total_months)  # Track profits separately
        partnerships_formed = 0
        partnerships_rejected_capacity = 0
        partner_brands = set()
        revenue_by_product = {product: 0 for product in self.product_list}
        profit_by_product = {product: 0 for product in self.product_list}  # Track profit by product
        blocked_brands = set()
        
        # Track capacity utilization over time
        monthly_capacity_utilization = []
        
        # Co-branded specific tracking
        active_cobranded_count = 0
        
        # Main simulation loop
        for month in range(1, self.total_months + 1):
            quarter = ((month - 1) // 3) + 1
            
            # Update market state quarterly
            if (month - 1) % 3 == 0:
                market_manager.update_market_state()
                
                # Apply market shocks
                while shock_index < len(market_shocks) and market_shocks[shock_index]['month'] <= month:
                    shock = market_shocks[shock_index]
                    market_manager.apply_market_shock(
                        shock['type'],
                        duration=shock['duration'],
                        intensity=shock['intensity']
                    )
                    shock_index += 1
            
            # Check for partnership endings and release capacity
            partnerships_to_remove = []
            for i, partnership in enumerate(active_partnerships):
                if partnership.end_month == month:
                    # Release capacity
                    for product, details in partnership.products.items():
                        capacity_tracker.release_capacity(product, details['units'])
                    partnerships_to_remove.append(i)
                    
                    # 50% chance of renewal if not blocked
                    if partnership.brand_name not in blocked_brands and random.random() < 0.5:
                        # Get the brand object
                        renewing_brand = self.brand_agents.get(partnership.brand_name)
                        if renewing_brand:
                            # Calculate desired units for renewal (same as before)
                            renewal_units = partnership.annual_units
                            
                            # Get Macron's allocation decision for renewal
                            allocated_units, new_product_allocation = self._macron_capacity_allocation(
                                partnership.brand_name, renewal_units, partnership.model, 
                                capacity_tracker, renewing_brand
                            )
                            
                            if allocated_units > 0:
                                # Commit capacity for renewal
                                for product, units in new_product_allocation.items():
                                    capacity_tracker.commit_capacity(product, units)
                                
                                # Recalculate financials with new allocation
                                deal_products = {}
                                monthly_revenue = 0
                                monthly_profit = 0
                                
                                for product, units in new_product_allocation.items():
                                    price = self._calculate_pricing(product, units, partnership.model, renewing_brand)
                                    variable_cost = self.product_costs[product]['variable_cost']
                                    
                                    annual_revenue = price * units
                                    annual_cogp = variable_cost * units
                                    annual_profit = annual_revenue - annual_cogp
                                    
                                    deal_products[product] = {
                                        'units': units,
                                        'price': price,
                                        'variable_cost': variable_cost,
                                        'annual_revenue': annual_revenue,
                                        'annual_cogp': annual_cogp,
                                        'annual_profit': annual_profit
                                    }
                                    
                                    monthly_revenue += annual_revenue / 12
                                    monthly_profit += annual_profit / 12
                                
                                # Create renewed partnership
                                new_duration_months = random.randint(1, 3) * 12
                                renewed_partnership = PartnershipDeal(
                                    brand_name=partnership.brand_name,
                                    model=partnership.model,
                                    start_month=month + 1,
                                    end_month=min(month + new_duration_months, self.total_months),
                                    products=deal_products,
                                    monthly_revenue=monthly_revenue,
                                    monthly_profit=monthly_profit,
                                    segment=partnership.segment,
                                    annual_units=allocated_units
                                )
                                active_partnerships.append(renewed_partnership)
                            else:
                                # Couldn't renew due to capacity constraints
                                blocked_brands.add(partnership.brand_name)
                    else:
                        blocked_brands.add(partnership.brand_name)
            
            # Remove ended partnerships
            for i in reversed(partnerships_to_remove):
                active_partnerships.pop(i)
            
            # Update co-branded count
            if model == 'co-branded':
                active_cobranded_count = len([p for p in active_partnerships 
                                            if p.start_month <= month <= p.end_month])
            
            # Each brand considers partnership
            for brand_name, brand in self.brand_agents.items():
                if brand_name in blocked_brands:
                    continue
                
                # Check if already has active partnership
                has_active = any(p.brand_name == brand_name and p.end_month >= month 
                               for p in active_partnerships)
                
                if has_active:
                    continue
                
                # Decision frequency based on decision speed
                decision_frequency = int(3 / (brand.decision_speed + 0.1))
                
                if month % decision_frequency == 0:
                    # Get market intelligence
                    market_intel = market_manager.get_market_intelligence(brand.segment_id)
                    
                    # Evaluate partnership
                    sample_product = self.product_list[0]
                    sample_cost = self.product_costs[sample_product]['variable_cost']
                    
                    if model == 'co-branded':
                        price_multiplier = 1.45  # 45% markup
                    else:
                        price_multiplier = 1.15  # 15% markup
                    
                    sample_price = sample_cost * price_multiplier
                    
                    evaluation = brand.evaluate_partnership_opportunity(
                        product=sample_product,
                        model=model,
                        price_per_unit=sample_price,
                        technical_specs={'category': 'Technical'},
                        market_intelligence=market_intel
                    )
                    
                    # Apply exclusivity factor for co-branded
                    if model == 'co-branded':
                        # More pragmatic exclusivity factors - allow more partnerships
                        if brand.segment_id and any(seg in [6, 7] for seg in brand.segment_id):
                            # High-Performance Luxury and Luxury Fashion - still exclusive but more pragmatic
                            exclusivity_factor = max(0.5, 1.0 - (active_cobranded_count * 0.08))
                        elif brand.segment_id and any(seg in [4, 5] for seg in brand.segment_id):
                            # Luxury Activewear and Athluxury - moderate exclusivity
                            exclusivity_factor = max(0.6, 1.0 - (active_cobranded_count * 0.05))
                        else:
                            # Technical segments - minimal exclusivity constraint
                            exclusivity_factor = max(0.8, 1.0 - (active_cobranded_count * 0.02))
                        
                        adjusted_propensity = evaluation['propensity_score'] * exclusivity_factor
                    else:
                        adjusted_propensity = evaluation['propensity_score']
                    
                    # Decision thresholds - more pragmatic for co-branded
                    base_threshold = 0.20 if model == 'co-branded' else 0.20  # Lower threshold for co-branded
                    threshold = base_threshold * (1.5 - brand.risk_appetite)
                    
                    if adjusted_propensity > threshold:
                        acceptance_probability = adjusted_propensity * (0.5 + brand.decision_speed * 0.5)
                        
                        if random.random() < acceptance_probability:
                            # Calculate demand
                            desired_units, _ = self._calculate_brand_demand(brand, model)
                            
                            # Get Macron's allocation decision based on available capacity
                            allocated_units, product_allocation = self._macron_capacity_allocation(
                                brand_name, desired_units, model, capacity_tracker, brand
                            )
                            
                            # If Macron couldn't allocate meaningful capacity, reject
                            if allocated_units == 0:
                                partnerships_rejected_capacity += 1
                                continue
                            
                            # Macron strategic decision for co-branded - more pragmatic approach
                            macron_accepts = True
                            
                            if model == 'co-branded':
                                primary_segment = brand.segment_id[0] if brand.segment_id else 3
                                
                                # More pragmatic strategic acceptance criteria
                                # Focus on revenue potential while maintaining some brand standards
                                if primary_segment in [1, 2, 3]:  # Technical segments
                                    # Accept more technical brands (up to 20)
                                    if active_cobranded_count >= 20:
                                        # Still accept if brand has high revenue potential
                                        if brand.annual_revenue_millions < 100 or random.random() > 0.5:
                                            macron_accepts = False
                                elif primary_segment in [4, 5]:  # Mid-luxury segments
                                    # Accept more mid-luxury brands (up to 25)
                                    if active_cobranded_count >= 25:
                                        # Accept based on brand strength
                                        if brand.market_leader_score < 0.6 or random.random() > 0.7:
                                            macron_accepts = False
                                else:  # Luxury segments (6, 7)
                                    # Always prioritize luxury brands - no limit
                                    macron_accepts = True
                                
                                # Revenue-based override - accept high-value partnerships
                                if not macron_accepts and allocated_units > 20000:
                                    # High-volume partnerships are reconsidered
                                    if random.random() < 0.7:
                                        macron_accepts = True
                            
                            if macron_accepts:
                                # Commit capacity
                                for product, units in product_allocation.items():
                                    capacity_tracker.commit_capacity(product, units)
                                
                                partnerships_formed += 1
                                partner_brands.add(brand_name)
                                
                                # Create partnership
                                partnership_duration_months = random.randint(1, 3) * 12
                                
                                deal_products = {}
                                monthly_revenue = 0
                                monthly_profit = 0
                                total_annual_units = 0
                                
                                for product, units in product_allocation.items():
                                    price = self._calculate_pricing(product, units, model, brand)
                                    variable_cost = self.product_costs[product]['variable_cost']
                                    
                                    annual_revenue = price * units
                                    annual_cogp = variable_cost * units
                                    annual_profit = annual_revenue - annual_cogp
                                    
                                    deal_products[product] = {
                                        'units': units,
                                        'price': price,
                                        'variable_cost': variable_cost,
                                        'annual_revenue': annual_revenue,
                                        'annual_cogp': annual_cogp,
                                        'annual_profit': annual_profit
                                    }
                                    
                                    monthly_revenue += annual_revenue / 12
                                    monthly_profit += annual_profit / 12
                                    total_annual_units += units
                                    
                                    # Track cumulative revenue and profit
                                    revenue_by_product[product] += annual_revenue * (partnership_duration_months / 12)
                                    profit_by_product[product] += annual_profit * (partnership_duration_months / 12)
                                
                                partnership = PartnershipDeal(
                                    brand_name=brand_name,
                                    model=model,
                                    start_month=month,
                                    end_month=min(month + partnership_duration_months, self.total_months),
                                    products=deal_products,
                                    monthly_revenue=monthly_revenue,
                                    monthly_profit=monthly_profit,
                                    segment=brand.segment_id[0] if brand.segment_id else 3,
                                    annual_units=total_annual_units
                                )
                                
                                active_partnerships.append(partnership)
                        else:
                            # Macron strategically rejected despite capacity
                            logger.debug(f"Macron strategically rejected {brand_name} despite having capacity")
            
            # Calculate monthly revenue
            for partnership in active_partnerships:
                if partnership.start_month <= month <= partnership.end_month:
                    monthly_revenues[month - 1] += partnership.monthly_revenue
                    monthly_profits[month - 1] += partnership.monthly_profit
            
            # Track capacity utilization
            utilization = capacity_tracker.get_utilization()
            monthly_capacity_utilization.append(utilization)
        
        # Calculate financial metrics
        total_revenue = np.sum(monthly_revenues)
        total_profit = np.sum(monthly_profits)
        
        # Calculate NPV (on profits, not revenue)
        monthly_discount_rate = (1 + self.config.discount_rate) ** (1/12) - 1
        discount_factors = [(1 + monthly_discount_rate) ** -i for i in range(self.total_months)]
        npv_revenue = np.sum(monthly_revenues * discount_factors)
        npv_profit = np.sum(monthly_profits * discount_factors)
        
        # Revenue and profit by year
        revenue_by_year = []
        profit_by_year = []
        for year in range(self.config.simulation_years):
            year_start = year * 12
            year_end = (year + 1) * 12
            year_revenue = np.sum(monthly_revenues[year_start:year_end])
            year_profit = np.sum(monthly_profits[year_start:year_end])
            revenue_by_year.append(year_revenue)
            profit_by_year.append(year_profit)
        
        return {
            'simulation_id': simulation_id,
            'model': model,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'npv_revenue': npv_revenue,
            'npv_profit': npv_profit,
            'partnerships_formed': partnerships_formed,
            'partnerships_rejected_capacity': partnerships_rejected_capacity,
            'revenue_by_year': revenue_by_year,
            'profit_by_year': profit_by_year,
            'revenue_by_product': revenue_by_product,
            'profit_by_product': profit_by_product,
            'partner_brands': list(partner_brands),
            'market_shocks': market_shocks,
            'avg_capacity_utilization': np.mean(monthly_capacity_utilization),
            'max_capacity_utilization': np.max(monthly_capacity_utilization),
            'final_capacity_utilization': monthly_capacity_utilization[-1] if monthly_capacity_utilization else 0
        }
    
    def run_simulation(self) -> Dict[str, Any]:
        """Run simulations for both models and provide insights"""
        print("\n🚀 STARTING MODAMESH SIMULATION")
        print(f"   Simulations per model: {self.config.n_simulations:,}")
        print(f"   Total simulations: {self.config.n_simulations * 2:,}")
        print(f"   Simulation years: {self.config.simulation_years}")
        print(f"   Capacity constraint: {self.config.production_capacity.get_available_capacity():,} units/year\n")
        
        # Temporarily suppress market state manager logging
        market_logger = logging.getLogger('agents.market_state_manager')
        original_level = market_logger.level
        market_logger.setLevel(logging.ERROR)
        
        results = {
            'co-branded': [],
            'white-label': []
        }
        
        # Run simulations for each model with progress bar
        for model in ['co-branded', 'white-label']:
            print(f"\n📊 Running {model} simulations...")
            
            # Create progress bar
            with tqdm(total=self.config.n_simulations, 
                     desc=f"{model} simulations", 
                     unit="sim",
                     ncols=100,
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
                
                for i in range(self.config.n_simulations):
                    result = self.run_single_simulation(i, model)
                    results[model].append(result)
                    pbar.update(1)
        
        # Restore original logging level
        market_logger.setLevel(original_level)
        
        print("\n⏱️  Simulation completed!")
        
        # Analyze results
        analysis = self.analyze_results(results)
        
        # Save results
        self._save_results(results, analysis)
        
        # Print insights
        self._print_insights(analysis)
        
        return analysis
    
    def analyze_results(self, results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze simulation results"""
        analysis = {}
        
        for model, model_results in results.items():
            df = pd.DataFrame(model_results)
            
            analysis[model] = {
                'mean_total_revenue': df['total_revenue'].mean(),
                'std_total_revenue': df['total_revenue'].std(),
                'mean_total_profit': df['total_profit'].mean(),
                'std_total_profit': df['total_profit'].std(),
                'mean_npv_profit': df['npv_profit'].mean(),
                'std_npv_profit': df['npv_profit'].std(),
                'mean_partnerships': df['partnerships_formed'].mean(),
                'mean_rejected_capacity': df['partnerships_rejected_capacity'].mean(),
                'avg_capacity_utilization': df['avg_capacity_utilization'].mean(),
                'max_capacity_reached': (df['max_capacity_utilization'] >= 95).sum() / len(df) * 100,
                'revenue_percentiles': {
                    '5%': df['total_revenue'].quantile(0.05),
                    '25%': df['total_revenue'].quantile(0.25),
                    '50%': df['total_revenue'].quantile(0.50),
                    '75%': df['total_revenue'].quantile(0.75),
                    '95%': df['total_revenue'].quantile(0.95)
                },
                'profit_percentiles': {
                    '5%': df['total_profit'].quantile(0.05),
                    '25%': df['total_profit'].quantile(0.25),
                    '50%': df['total_profit'].quantile(0.50),
                    '75%': df['total_profit'].quantile(0.75),
                    '95%': df['total_profit'].quantile(0.95)
                }
            }
        
        # Compare models
        analysis['comparison'] = {
            'revenue_ratio': analysis['white-label']['mean_total_revenue'] / analysis['co-branded']['mean_total_revenue'],
            'profit_ratio': analysis['white-label']['mean_total_profit'] / analysis['co-branded']['mean_total_profit'],
            'npv_profit_ratio': analysis['white-label']['mean_npv_profit'] / analysis['co-branded']['mean_npv_profit'],
            'partnership_ratio': analysis['white-label']['mean_partnerships'] / analysis['co-branded']['mean_partnerships'],
            'capacity_util_diff': analysis['white-label']['avg_capacity_utilization'] - analysis['co-branded']['avg_capacity_utilization']
        }
        
        # Determine recommendation based on profit NPV
        co_branded_score = analysis['co-branded']['mean_npv_profit']
        white_label_score = analysis['white-label']['mean_npv_profit']
        
        analysis['recommendation'] = {
            'chosen_model': 'co-branded' if co_branded_score > white_label_score else 'white-label',
            'co_branded_score': co_branded_score,
            'white_label_score': white_label_score,
            'score_difference_pct': abs(co_branded_score - white_label_score) / max(co_branded_score, white_label_score) * 100
        }
        
        return analysis
    
    def _save_results(self, results: Dict[str, List[Dict]], analysis: Dict[str, Any]):
        """Save simulation results to file"""
        results_dir = Path("simulation_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        with open(results_dir / f"single_model_results_{timestamp}.json", 'w') as f:
            json.dump({
                'config': {
                    'n_simulations': self.config.n_simulations,
                    'simulation_years': self.config.simulation_years,
                    'capacity_constraint': self.config.production_capacity.get_available_capacity()
                },
                'results': results,
                'timestamp': timestamp
            }, f, indent=2)
        
        # Save analysis
        with open(results_dir / f"single_model_analysis_{timestamp}.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Results saved to simulation_results/single_model_analysis_{timestamp}.json")
    
    def _print_insights(self, analysis: Dict[str, Any]):
        """Print key insights and recommendations"""
        print("\n" + "="*80)
        print("📊 SIMULATION RESULTS & INSIGHTS")
        print("="*80)
        
        # Results for each model
        for model in ['co-branded', 'white-label']:
            profit_margin = (analysis[model]['mean_total_profit'] / analysis[model]['mean_total_revenue'] * 100) if analysis[model]['mean_total_revenue'] > 0 else 0
            
            print(f"\n{model.upper()} MODEL:")
            print(f"   Mean Total Revenue (5Y): €{analysis[model]['mean_total_revenue']:,.0f}")
            print(f"   Mean Total Profit (5Y): €{analysis[model]['mean_total_profit']:,.0f}")
            print(f"   Profit Margin: {profit_margin:.1f}%")
            print(f"   Mean NPV (Profit): €{analysis[model]['mean_npv_profit']:,.0f}")
            print(f"   Mean Partnerships: {analysis[model]['mean_partnerships']:.1f}")
            print(f"   Avg Capacity Utilization: {analysis[model]['avg_capacity_utilization']:.1f}%")
            print(f"   Revenue Range (5%-95%): €{analysis[model]['revenue_percentiles']['5%']:,.0f} - €{analysis[model]['revenue_percentiles']['95%']:,.0f}")
        
        # Comparison
        print(f"\n🔄 MODEL COMPARISON:")
        print(f"   Revenue Ratio (WL/CB): {analysis['comparison']['revenue_ratio']:.2f}x")
        print(f"   Profit Ratio (WL/CB): {analysis['comparison']['profit_ratio']:.2f}x")
        print(f"   NPV Profit Ratio (WL/CB): {analysis['comparison']['npv_profit_ratio']:.2f}x")
        print(f"   Partnership Ratio (WL/CB): {analysis['comparison']['partnership_ratio']:.2f}x")
        
        # Key insights
        print(f"\n💡 KEY INSIGHTS:")
        cb_margin = (analysis['co-branded']['mean_total_profit'] / analysis['co-branded']['mean_total_revenue'] * 100)
        wl_margin = (analysis['white-label']['mean_total_profit'] / analysis['white-label']['mean_total_revenue'] * 100)
        
        print(f"   • Co-Branded achieves {cb_margin:.1f}% profit margin vs White-Label's {wl_margin:.1f}%")
        print(f"   • White-Label generates {analysis['comparison']['revenue_ratio']:.1f}x more revenue but only {analysis['comparison']['profit_ratio']:.1f}x the profit")
        
        # R&D recovery
        rd_investment = 5_770_000  # €5.77M
        cb_recovery = analysis['co-branded']['mean_total_profit'] / rd_investment * 100
        wl_recovery = analysis['white-label']['mean_total_profit'] / rd_investment * 100
        
        print(f"\n📈 R&D INVESTMENT RECOVERY (€5.77M):")
        print(f"   • Co-Branded profit covers {cb_recovery:.0f}% of R&D investment")
        print(f"   • White-Label profit covers {wl_recovery:.0f}% of R&D investment")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION:")
        if analysis['comparison']['profit_ratio'] < 1:
            print(f"   ✅ Choose CO-BRANDED MODEL")
            print(f"   • Delivers {1/analysis['comparison']['profit_ratio']:.1f}x more profit despite lower revenue")
            print(f"   • Higher margins ({cb_margin:.1f}%) compensate for lower volume")
            print(f"   • Better unit economics: €{analysis['co-branded']['mean_total_profit']/analysis['co-branded']['mean_partnerships']/self.config.simulation_years/10000:.0f}/unit profit")
        else:
            print(f"   ✅ Choose WHITE-LABEL MODEL")
            print(f"   • Delivers {analysis['comparison']['profit_ratio']:.1f}x more profit")
            print(f"   • Volume advantage outweighs margin disadvantage")
        
        print(f"\n⚡ Strategic Considerations:")
        print(f"   • Co-Branded has {100-analysis['co-branded']['avg_capacity_utilization']:.0f}% capacity headroom for growth")
        print(f"   • White-Label uses {analysis['white-label']['avg_capacity_utilization']:.0f}% of capacity - more efficient")
        
        if analysis['co-branded']['avg_capacity_utilization'] < 20:
            print(f"   • Co-Branded's low utilization ({analysis['co-branded']['avg_capacity_utilization']:.1f}%) allows selective, high-margin partnerships")
        
        print("\n" + "="*80)


def main():
    """Run the single model simulation with capacity constraints"""
    print("🎯 MODAMESH SIMULATION - CO-BRANDED vs WHITE-LABEL ANALYSIS")
    print("=" * 80)
    
    # Check for test mode
    test_mode = '--test' in sys.argv
    
    # Create configuration
    if test_mode:
        n_sims = 100
        print("\n⚡ RUNNING IN TEST MODE (100 simulations)")
    else:
        n_sims = 10000
    
    config = SimulationConfig(
        n_simulations=n_sims,
        simulation_years=5,
        base_seed=42
    )
    
    print(f"\n📋 Configuration:")
    print(f"   • Simulations: {config.n_simulations:,} per model")
    print(f"   • Time horizon: {config.simulation_years} years")
    print(f"   • Production capacity: {config.production_capacity.get_available_capacity():,} units/year")
    print(f"   • Capacity allocation: 50% of total Macron capacity")
    print(f"   • Model choice: EITHER co-branded OR white-label (not both)")
    
    # Initialize and run simulation
    simulation = SingleModelSimulation(config)
    
    # Run simulation - it will automatically run both models and print insights
    start_time = datetime.now()
    analysis = simulation.run_simulation()
    end_time = datetime.now()
    
    print(f"\n⏱️  Total execution time: {(end_time - start_time).total_seconds():.1f} seconds")


if __name__ == "__main__":
    main() 