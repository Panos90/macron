#!/usr/bin/env python3
"""
Simulation Orchestrator for ModaMesh™
Central orchestration for the ModaMesh™ multi-agent simulation.
Manages agent initialization, market dynamics, and simulation execution.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from .brand_agent import BrandAgent, load_all_brand_agents
from .macron_agent import MacronAgent, load_macron_agent
from .market_state_manager import MarketStateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for simulation parameters"""
    simulation_years: int = 5
    time_steps_per_year: int = 4  # Quarterly
    random_seed: Optional[int] = None
    
    # Market dynamics parameters
    market_growth_rate: float = 0.03  # 3% annual growth
    innovation_diffusion_rate: float = 0.15  # Rogers' innovation adoption
    competitive_response_delay: int = 2  # Time steps for competitors to respond
    
    # Partnership parameters
    max_partnerships_per_brand: int = 3
    partnership_evaluation_frequency: int = 2  # Every 2 time steps
    minimum_partnership_duration: int = 4  # 1 year minimum
    
    # Economic parameters
    interest_rate: float = 0.02  # 2% discount rate
    inflation_rate: float = 0.02  # 2% annual inflation


@dataclass
class MarketState:
    """Current state of the market"""
    time_step: int = 0
    year: int = 1
    quarter: int = 1
    
    # Market metrics
    total_market_size: float = 0
    segment_growth_rates: Dict[int, float] = field(default_factory=dict)
    innovation_adoption_level: float = 0.1  # Starting adoption level
    
    # Partnership tracking
    active_partnerships: List[Dict[str, Any]] = field(default_factory=list)
    partnership_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    macron_revenue: float = 0
    macron_market_share: float = 0
    brand_satisfaction_scores: Dict[str, float] = field(default_factory=dict)


class SimulationOrchestrator:
    """
    Main orchestrator for the ModaMesh™ simulation
    """
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        self.market_state = MarketState()
        
        # Set random seed if provided
        if self.config.random_seed:
            random.seed(self.config.random_seed)
            logger.info(f"🎲 Random seed set to: {self.config.random_seed}")
        
        # Agent collections
        self.brand_agents: Dict[str, BrandAgent] = {}
        self.macron_agent: Optional[MacronAgent] = None
        
        # Initialize Market State Manager
        self.market_manager = MarketStateManager(initial_seed=self.config.random_seed)
        
        # Market segments from Italian Fashion Market
        self.market_segments = {
            1: "Core Technical Sportswear",
            2: "Outdoor Technical Sportswear",
            3: "Athleisure",
            4: "Luxury Activewear",
            5: "Athluxury",
            6: "High-Performance Luxury",
            7: "Luxury Fashion"
        }
    
    def initialize_simulation(self) -> None:
        """Initialize all agents and market state"""
        logger.info("🎬 Initializing ModaMesh™ Simulation...")
        
        # Load all brand agents
        self.brand_agents = load_all_brand_agents()
        logger.info(f"✅ Loaded {len(self.brand_agents)} brand agents")
        
        # Load Macron agent
        self.macron_agent = load_macron_agent()
        logger.info("✅ Loaded Macron agent")
        
        # Initialize market state
        self._initialize_market_state()
        
        # Log agent statistics
        self._log_agent_statistics()
    
    def _initialize_market_state(self) -> None:
        """Initialize the market state with realistic values"""
        # Calculate total market size from brand revenues
        total_revenue = sum(agent.annual_revenue_millions for agent in self.brand_agents.values())
        self.market_state.total_market_size = total_revenue
        
        # Initialize segment growth rates
        segment_growth = {
            1: 0.02,  # Core Technical - Mature, slow growth
            2: 0.05,  # Outdoor Technical - Growing
            3: 0.04,  # Athleisure - Steady growth
            4: 0.08,  # Luxury Activewear - High growth
            5: 0.06,  # Athluxury - Strong growth
            6: 0.10,  # High-Performance Luxury - Highest growth
            7: 0.01   # Luxury Fashion - Slow growth
        }
        self.market_state.segment_growth_rates = segment_growth
        
        logger.info(f"📊 Total market size: €{total_revenue:,.0f}M")
    
    def _log_agent_statistics(self) -> None:
        """Log statistics about loaded agents"""
        # Risk appetite distribution
        risk_appetites = [agent.risk_appetite for agent in self.brand_agents.values()]
        avg_risk = sum(risk_appetites) / len(risk_appetites)
        
        # Decision speed distribution
        decision_speeds = [agent.decision_speed for agent in self.brand_agents.values()]
        avg_speed = sum(decision_speeds) / len(decision_speeds)
        
        # Appetite for high-performance luxury move distribution
        hp_luxury_appetites = [agent.appetite_for_high_performance_luxury_move for agent in self.brand_agents.values()]
        avg_hp_luxury_appetite = sum(hp_luxury_appetites) / len(hp_luxury_appetites)
        
        # Count brands by appetite levels
        brands_want_move = sum(1 for a in hp_luxury_appetites if a > 0.5)
        brands_in_seg_6 = sum(1 for agent in self.brand_agents.values() if 6 in agent.segment_id)
        brands_in_seg_5_or_7 = sum(1 for agent in self.brand_agents.values() 
                                   if any(seg in [5, 7] for seg in agent.segment_id))
        
        # Segment distribution
        segment_counts = {}
        for agent in self.brand_agents.values():
            for segment in agent.segment_id:
                segment_counts[segment] = segment_counts.get(segment, 0) + 1
        
        logger.info(f"\n📈 Agent Statistics:")
        logger.info(f"   Average Risk Appetite: {avg_risk:.2f}")
        logger.info(f"   Average Decision Speed: {avg_speed:.2f}")
        logger.info(f"   Average HP Luxury Move Appetite: {avg_hp_luxury_appetite:.2f}")
        logger.info(f"   Brands wanting HP Luxury move (>0.5): {brands_want_move} ({brands_want_move/len(self.brand_agents)*100:.1f}%)")
        logger.info(f"   Brands in segment 6 (HP Luxury): {brands_in_seg_6}")
        logger.info(f"   Brands in segments 5 or 7: {brands_in_seg_5_or_7}")
        logger.info(f"   Segment Distribution:")
        for segment, count in sorted(segment_counts.items()):
            logger.info(f"      {self.market_segments[segment]}: {count} brands")
    
    def evaluate_partnership_opportunities(self) -> List[Dict[str, Any]]:
        """
        Evaluate all potential partnerships between Macron and brands
        
        Returns:
            List of partnership opportunities ranked by potential
        """
        opportunities = []
        
        for brand_name, brand_agent in self.brand_agents.items():
            # Skip if brand already has max partnerships
            current_partnerships = sum(1 for p in self.market_state.active_partnerships 
                                     if p['brand'] == brand_name)
            if current_partnerships >= self.config.max_partnerships_per_brand:
                continue
            
            # Get market intelligence for the brand
            market_intel = self.market_manager.get_market_intelligence(brand_agent.segment_id)
            
            # Get Macron's assessment
            assessment = self.macron_agent.evaluate_brand_partnership_potential(brand_agent)
            
            # Get brand's interest with market context
            sample_product = list(self.macron_agent.product_portfolio.keys())[0]
            product_info = self.macron_agent.product_portfolio[sample_product]
            
            brand_interest = brand_agent.evaluate_partnership_opportunity(
                product=sample_product,
                model=assessment['recommended_model'],
                price_per_unit=100,  # Placeholder price
                technical_specs=product_info,
                market_intelligence=market_intel  # Pass market intelligence
            )
            
            # Create opportunity record
            opportunity = {
                'brand': brand_name,
                'macron_assessment': assessment,
                'brand_interest': brand_interest,
                'mutual_fit_score': (assessment['strategic_fit_score'] + 
                                   brand_interest['propensity_score']) / 2,
                'timing_alignment': self._calculate_timing_alignment(brand_agent),
                'market_context': {
                    'segment_growth': market_intel['segment_analysis']['weighted_growth_potential'],
                    'opportunities': len(market_intel['opportunities']),
                    'threats': len(market_intel['threats'])
                }
            }
            
            opportunities.append(opportunity)
        
        # Sort by mutual fit score
        opportunities.sort(key=lambda x: x['mutual_fit_score'], reverse=True)
        
        return opportunities
    
    def _calculate_timing_alignment(self, brand_agent: BrandAgent) -> float:
        """Calculate how well timing aligns for a partnership"""
        # Fast decision makers are ready sooner
        timing_score = brand_agent.decision_speed
        
        # Adjust for current market conditions
        if self.market_state.innovation_adoption_level < 0.3:
            # Early market - favor innovative brands
            timing_score *= (1 + brand_agent.innovation_perception)
        else:
            # Mature market - favor established brands
            timing_score *= (1 + brand_agent.market_leader_score)
        
        return min(timing_score, 1.0)
    
    def negotiate_partnership(self, 
                            brand_name: str,
                            products: List[str],
                            model: str) -> Optional[Dict[str, Any]]:
        """
        Negotiate a specific partnership deal
        
        Args:
            brand_name: Name of the brand to partner with
            products: List of products to include
            model: Partnership model (co-branded or white-label)
            
        Returns:
            Partnership agreement or None if negotiation fails
        """
        brand_agent = self.brand_agents[brand_name]
        
        # Get market intelligence for negotiation context
        market_intel = self.market_manager.get_market_intelligence(brand_agent.segment_id)
        
        # Get Macron's proposal
        proposal = self.macron_agent.propose_partnership_package(brand_agent)
        
        # Simulate negotiation rounds
        negotiation_rounds = int(3 * (1 - brand_agent.decision_speed))  # Slower brands negotiate more
        
        final_terms = {
            'brand': brand_name,
            'model': model,
            'products': [],
            'start_time': self.market_state.time_step,
            'duration': self.config.minimum_partnership_duration,
            'total_value': 0,
            'market_conditions': {
                'year': self.market_manager.current_year,
                'quarter': self.market_manager.current_quarter,
                'economic_confidence': market_intel['market_indicators']['economic_confidence'],
                'luxury_tech_convergence': market_intel['market_indicators']['luxury_technical_convergence']
            }
        }
        
        # Negotiate each product
        for product_proposal in proposal['product_proposals']:
            if product_proposal['product'] not in products:
                continue
            
            product_name = product_proposal['product']
            product_info = self.macron_agent.product_portfolio[product_name]
            
            # Handle "flexible" model by defaulting to white-label
            actual_model = model if model in ['co-branded', 'white-label'] else 'white-label'
            
            # Map model names to offer keys
            offer_key = 'co_branded_offer' if actual_model == 'co-branded' else 'white_label_offer'
            offer = product_proposal[offer_key]
            
            # Apply negotiation adjustments
            price_adjustment = 1.0
            for round in range(negotiation_rounds):
                if brand_agent.price_elasticity < -1:
                    # Price sensitive - push for discount
                    price_adjustment *= 0.95
                else:
                    # Less sensitive - accept closer to asking
                    price_adjustment *= 0.98
            
            # Market conditions affect final price
            if market_intel['market_indicators']['economic_confidence'] < 0.5:
                price_adjustment *= 0.95  # Additional discount in tough times
            
            final_price = offer['optimized_price'] * price_adjustment
            
            # Check if brand accepts final terms with market context
            acceptance = brand_agent.evaluate_partnership_opportunity(
                product=product_name,
                model=actual_model,
                price_per_unit=final_price,
                technical_specs=product_info,
                market_intelligence=market_intel
            )
            
            if acceptance['decision']:
                final_terms['products'].append({
                    'product': product_name,
                    'price': final_price,
                    'volume': offer['estimated_annual_volume'],
                    'annual_value': final_price * offer['estimated_annual_volume']
                })
                final_terms['total_value'] += final_price * offer['estimated_annual_volume']
        
        # Return agreement if any products accepted
        if final_terms['products']:
            return final_terms
        else:
            return None
    
    def update_market_state(self) -> None:
        """Update market state for the next time step"""
        self.market_state.time_step += 1
        
        # Update date
        self.market_state.quarter = ((self.market_state.time_step - 1) % 4) + 1
        self.market_state.year = ((self.market_state.time_step - 1) // 4) + 1
        
        # Update the market manager
        self.market_manager.update_market_state()
        
        # Get current market conditions
        market_summary = self.market_manager.get_current_state_summary()
        
        # Update innovation adoption based on market indicators
        self.market_state.innovation_adoption_level = market_summary['market_indicators']['luxury_technical_convergence']
        
        # Update market size with segment-specific growth
        segment_growth = market_summary['segment_dynamics']['growth_rates']
        avg_growth = sum(segment_growth.values()) / len(segment_growth)
        quarterly_growth = (1 + avg_growth) ** 0.25
        self.market_state.total_market_size *= quarterly_growth
        
        # Update active partnerships
        self._update_partnerships()
        
        logger.info(f"📊 Market conditions: {market_summary['consumer_preferences']}")
    
    def _update_partnerships(self) -> None:
        """Update partnership status and move expired ones to history"""
        active_partnerships = []
        
        for partnership in self.market_state.active_partnerships:
            # Check if partnership has expired
            if (self.market_state.time_step - partnership['start_time']) >= partnership['duration']:
                # Move to history
                partnership['end_time'] = self.market_state.time_step
                partnership['status'] = 'completed'
                self.market_state.partnership_history.append(partnership)
            else:
                active_partnerships.append(partnership)
        
        self.market_state.active_partnerships = active_partnerships
    
    def calculate_macron_performance(self) -> Dict[str, Any]:
        """Calculate Macron's current performance metrics"""
        # Revenue from active partnerships
        quarterly_revenue = sum(
            product['annual_value'] / 4  # Quarterly
            for partnership in self.market_state.active_partnerships
            for product in partnership['products']
        )
        
        # Market share in technical components market
        technical_market_size = self.market_state.total_market_size * 0.1  # Assume 10% is technical
        market_share = quarterly_revenue / (technical_market_size / 4) if technical_market_size > 0 else 0
        
        # Growth metrics
        previous_revenue = self.market_state.macron_revenue
        growth_rate = ((quarterly_revenue - previous_revenue) / previous_revenue 
                      if previous_revenue > 0 else 0)
        
        # Update state
        self.market_state.macron_revenue = quarterly_revenue
        self.market_state.macron_market_share = market_share
        
        return {
            'quarterly_revenue': quarterly_revenue,
            'annual_run_rate': quarterly_revenue * 4,
            'market_share': market_share,
            'growth_rate': growth_rate,
            'active_partnerships': len(self.market_state.active_partnerships),
            'partner_brands': list(set(p['brand'] for p in self.market_state.active_partnerships))
        }
    
    def apply_market_shock(self, shock_type: str, duration: int = 4, intensity: float = 0.5) -> None:
        """
        Apply a market shock through the Market State Manager
        
        Args:
            shock_type: Type of shock to apply
            duration: Duration in quarters
            intensity: Intensity of the shock (0-1)
        """
        self.market_manager.apply_market_shock(shock_type, duration, intensity)
        logger.warning(f"⚡ Market shock '{shock_type}' applied to simulation")
    
    def generate_simulation_report(self) -> Dict[str, Any]:
        """Generate comprehensive simulation report"""
        market_summary = self.market_manager.get_current_state_summary()
        
        return {
            'simulation_config': {
                'years': self.config.simulation_years,
                'current_time': {
                    'year': self.market_state.year,
                    'quarter': self.market_state.quarter,
                    'time_step': self.market_state.time_step
                }
            },
            'market_state': {
                'total_size': self.market_state.total_market_size,
                'innovation_adoption': self.market_state.innovation_adoption_level,
                'consumer_preferences': market_summary['consumer_preferences'],
                'market_indicators': market_summary['market_indicators'],
                'top_growth_segments': market_summary['top_growth_segments'],
                'active_shocks': market_summary['active_shocks']
            },
            'macron_performance': self.calculate_macron_performance(),
            'partnerships': {
                'active': len(self.market_state.active_partnerships),
                'completed': len(self.market_state.partnership_history),
                'total_value': sum(p['total_value'] for p in self.market_state.active_partnerships)
            },
            'agent_summary': {
                'total_brands': len(self.brand_agents),
                'macron_products': len(self.macron_agent.product_portfolio)
            }
        }


def main():
    """Test the simulation orchestrator"""
    print("🎮 SIMULATION ORCHESTRATOR TEST")
    print("=" * 60)
    
    # Create orchestrator with test config
    config = SimulationConfig(
        simulation_years=5,
        random_seed=42  # For reproducible results
    )
    
    orchestrator = SimulationOrchestrator(config)
    
    # Initialize simulation
    orchestrator.initialize_simulation()
    
    # Evaluate initial opportunities
    print("\n🔍 Top Partnership Opportunities:")
    opportunities = orchestrator.evaluate_partnership_opportunities()
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n{i}. {opp['brand']}")
        print(f"   Mutual Fit Score: {opp['mutual_fit_score']:.2f}")
        print(f"   Macron Priority: {opp['macron_assessment']['partnership_priority']}")
        print(f"   Brand Interest: {'Yes' if opp['brand_interest']['decision'] else 'No'}")
    
    # Simulate first partnership
    if opportunities:
        top_opportunity = opportunities[0]
        brand_name = top_opportunity['brand']
        products = [p[0] for p in top_opportunity['macron_assessment']['priority_products'][:2]]
        model = top_opportunity['macron_assessment']['recommended_model']
        
        print(f"\n🤝 Negotiating with {brand_name}...")
        agreement = orchestrator.negotiate_partnership(brand_name, products, model)
        
        if agreement:
            print(f"✅ Partnership agreed!")
            print(f"   Products: {len(agreement['products'])}")
            print(f"   Total Annual Value: €{agreement['total_value']:,.0f}")
            orchestrator.market_state.active_partnerships.append(agreement)
    
    # Generate initial report
    print("\n📊 Initial Simulation State:")
    report = orchestrator.generate_simulation_report()
    print(f"   Market Size: €{report['market_state']['total_size']:,.0f}M")
    print(f"   Innovation Adoption: {report['market_state']['innovation_adoption']:.1%}")
    print(f"   Active Partnerships: {report['partnerships']['active']}")


if __name__ == "__main__":
    main() 