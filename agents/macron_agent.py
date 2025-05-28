#!/usr/bin/env python3
"""
MACRON AGENT MODULE
===================
Special LangChain-based agent representing Macron in the ModaMesh simulation.
This agent has unique capabilities for managing partnerships and pricing strategies.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

from .brand_agent import BrandAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MacronAgent(BrandAgent):
    """
    Special agent for Macron with additional capabilities for partnership management
    """
    # Fixed values for Macron
    risk_appetite: float = field(default=0.8)  # High risk appetite
    decision_speed: float = field(default=0.7)  # Fast decision-making
    
    # Macron-specific attributes
    product_portfolio: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    active_partnerships: Dict[str, List[str]] = field(default_factory=dict)  # product -> [brands]
    pricing_strategy: Dict[str, float] = field(default_factory=dict)  # product -> base_price
    
    def __post_init__(self):
        """Initialize Macron's special capabilities"""
        super().__post_init__()
        self.system_prompt = self._create_macron_system_prompt()
        self.load_product_portfolio()
    
    def _create_macron_system_prompt(self) -> str:
        """Create Macron's strategic system prompt"""
        return f"""You are the strategic decision-maker for Macron, an innovative Italian sportswear brand.

Your unique position:
- Technical innovation leader with {self.patent_count} patents
- Revenue: €{self.annual_revenue_millions}M (Growth: {self.revenue_growth_rate*100:.1f}%)
- Technical capability: {self.technical_capability:.2f} (highest in the market)
- Risk appetite: {self.risk_appetite:.2f} (aggressive growth strategy)
- Decision speed: {self.decision_speed:.2f} (rapid market response)

Your strategic objectives:
1. Expand into fashion segments through technical partnerships
2. Maximize value capture from innovation portfolio
3. Build "Powered by Macron" brand equity
4. Optimize pricing for market penetration vs. margin

Partnership models:
1. "Powered by Macron" (Co-branded): Visible partnership for brand building
2. White-Label: Hidden partnership for volume and margin

You evaluate partnerships based on:
- Brand's market influence and reach
- Technical gap they need to fill
- Price sensitivity and volume potential
- Strategic value for market expansion
- Competitive dynamics in their segment"""
    
    def load_product_portfolio(self):
        """Load Macron's product portfolio and set initial pricing"""
        # Load product costs from cost estimation results
        try:
            cost_data_path = Path("product_costs")
            latest_analysis = sorted(cost_data_path.glob("analysis_*.json"))[-1]
            
            with open(latest_analysis, 'r') as f:
                cost_analysis = json.load(f)
            
            # Extract Asian production costs (most competitive)
            asian_costs = cost_analysis['scenarios']['Asian_Production']['products']
            
            for product_name, product_data in asian_costs.items():
                variable_cost = product_data['variable_costs']['mean']
                
                # Set initial pricing: 3x cost for co-branded, 2x for white-label
                self.product_portfolio[product_name] = {
                    'variable_cost': variable_cost,
                    'category': product_data['category'],
                    'complexity': product_data['complexity']
                }
                
                self.pricing_strategy[product_name] = {
                    'co-branded': variable_cost * 3.0,
                    'white-label': variable_cost * 2.0,
                    'minimum_margin': 0.5  # 50% minimum margin
                }
                
            logger.info(f"📦 Loaded {len(self.product_portfolio)} products into Macron's portfolio")
            
        except Exception as e:
            logger.error(f"Failed to load product portfolio: {e}")
            # Set default products if loading fails
            self._set_default_portfolio()
    
    def _set_default_portfolio(self):
        """Set default product portfolio if cost data unavailable"""
        default_products = [
            "Hydrotex Moisture-Control Liners",
            "EcoMesh Ventilation Panels", 
            "HD Bonded Insulation Pads",
            "Phase Change Material (PCM) Inserts",
            "Performance Jacquard Reinforcement",
            "Abrasion-Resistant Bonding",
            "MacronLock Magnetic Closures",
            "Auto-Tension Drawstrings",
            "100% Recycled Performance Jacquard",
            "Bio-Based Water Repellents"
        ]
        
        for product in default_products:
            self.product_portfolio[product] = {
                'variable_cost': 50.0,  # Default cost
                'category': 'Technical Component',
                'complexity': 'High'
            }
            self.pricing_strategy[product] = {
                'co-branded': 150.0,
                'white-label': 100.0,
                'minimum_margin': 0.5
            }
    
    def evaluate_brand_partnership_potential(self, brand_agent: BrandAgent) -> Dict[str, Any]:
        """
        Evaluate a brand's potential as a partner
        
        Args:
            brand_agent: The brand agent to evaluate
            
        Returns:
            Partnership potential assessment
        """
        # Calculate strategic value
        market_influence = (
            brand_agent.market_leader_score * 0.3 +
            brand_agent.media_amplification * 0.2 +
            brand_agent.geographic_reach * 0.2 +
            brand_agent.brand_heat * 0.3
        )
        
        # Calculate technical need
        technical_gap = max(0, 0.8 - brand_agent.technical_capability)
        innovation_gap = max(0, 0.7 - brand_agent.innovation_perception)
        capability_need = (technical_gap + innovation_gap) / 2
        
        # Calculate financial capacity
        revenue_score = min(1.0, brand_agent.annual_revenue_millions / 1000)  # Normalize to 1B
        margin_score = brand_agent.ebitda_margin / 0.3  # Normalize to 30% EBITDA
        financial_capacity = (revenue_score + margin_score) / 2
        
        # UPDATED: Infer segment expansion interest from observable signals
        # Instead of directly accessing appetite, we infer from market behaviors
        segment_expansion_signals = self._infer_segment_expansion_interest(brand_agent)
        
        # Strategic fit score (updated weights)
        strategic_fit = (
            market_influence * 0.35 +
            capability_need * 0.25 +
            financial_capacity * 0.15 +
            brand_agent.partnership_success_rate * 0.1 +
            segment_expansion_signals * 0.15  # Based on inferred signals
        )
        
        # Recommended approach (updated logic based on observable factors)
        if brand_agent.brand_dilution_sensitivity > 0.7 and brand_agent.innovation_perception > 0.6:
            recommended_model = "white-label"
        elif brand_agent.innovation_perception < 0.5 or (6 not in brand_agent.segment_id and brand_agent.technical_capability < 0.5):
            recommended_model = "co-branded"  # They need innovation credibility
        else:
            recommended_model = "flexible"  # Could work with either
        
        # Priority products based on brand profile
        priority_products = self._identify_priority_products(brand_agent)
        
        return {
            "brand": brand_agent.brand_name,
            "strategic_fit_score": strategic_fit,
            "market_influence": market_influence,
            "capability_need": capability_need,
            "financial_capacity": financial_capacity,
            "segment_expansion_signals": segment_expansion_signals,  # Based on inferred signals
            "recommended_model": recommended_model,
            "priority_products": priority_products[:3],  # Top 3 products
            "estimated_volume_potential": self._estimate_volume_potential(brand_agent),
            "partnership_priority": "high" if strategic_fit > 0.7 else "medium" if strategic_fit > 0.4 else "low"
        }
    
    def _infer_segment_expansion_interest(self, brand_agent: BrandAgent) -> float:
        """
        Infer a brand's interest in segment expansion from observable market signals
        
        Args:
            brand_agent: The brand to analyze
            
        Returns:
            Inferred interest score (0.0 to 1.0)
        """
        signals = []
        
        # Signal 1: Recent sportswear partnerships indicate openness to technical integration
        if brand_agent.sportswear_partnerships > 2:
            signals.append(0.3)
        elif brand_agent.sportswear_partnerships > 0:
            signals.append(0.2)
        
        # Signal 2: High outsourcing ratio suggests willingness to adopt external innovations
        if brand_agent.outsourcing_ratio > 0.6:
            signals.append(0.3)
        elif brand_agent.outsourcing_ratio > 0.3:
            signals.append(0.2)
        
        # Signal 3: Strategic agility indicates willingness to explore new segments
        if brand_agent.strategic_agility > 0.7:
            signals.append(0.2)
        
        # Signal 4: High innovation count but low perception suggests need for technical credibility
        if brand_agent.innovation_count > 5 and brand_agent.innovation_perception < 0.5:
            signals.append(0.3)
        
        # Signal 5: Segment fluidity indicates openness to cross-segment moves
        if brand_agent.segment_fluidity > 0.6:
            signals.append(0.3)
        elif brand_agent.segment_fluidity > 0.4:
            signals.append(0.2)
        
        # Signal 6: Brands in adjacent segments (5 or 7) more likely to be interested
        if any(seg in [5, 7] for seg in brand_agent.segment_id):
            signals.append(0.2)
        
        # Signal 7: Already in HP Luxury (segment 6) - no expansion needed
        if 6 in brand_agent.segment_id:
            return 0.0
        
        # Aggregate signals with diminishing returns
        if signals:
            return min(sum(signals) / len(signals) * 1.5, 1.0)
        else:
            return 0.1  # Base level interest
    
    def _identify_priority_products(self, brand_agent: BrandAgent) -> List[Tuple[str, float]]:
        """Identify which products would be most valuable for a brand"""
        product_scores = []
        
        for product_name, product_info in self.product_portfolio.items():
            score = 0
            
            # Match product complexity with brand capability
            if product_info['complexity'] == 'Very High' and brand_agent.technical_capability < 0.3:
                score += 0.3
            elif product_info['complexity'] == 'High' and brand_agent.technical_capability < 0.5:
                score += 0.2
            
            # Sustainability products for brands with high sustainability score
            if 'Sustainable' in product_info['category'] and brand_agent.sustainability_score > 0.6:
                score += 0.3
            
            # Innovation products for brands needing innovation boost
            if brand_agent.innovation_perception < 0.5:
                score += 0.2
            
            # UPDATED: Boost score based on inferred expansion interest
            expansion_signals = self._infer_segment_expansion_interest(brand_agent)
            if expansion_signals > 0.5:
                # Technical components are crucial for segment 6
                if 'Technical' in product_info['category'] or product_info['complexity'] in ['High', 'Very High']:
                    score += expansion_signals * 0.3
            
            # Price tier alignment
            price_alignment = 1 - abs(brand_agent.price_tier - 3) / 3  # Assuming tier 3 is mid
            score += price_alignment * 0.2
            
            product_scores.append((product_name, score))
        
        return sorted(product_scores, key=lambda x: x[1], reverse=True)
    
    def _estimate_volume_potential(self, brand_agent: BrandAgent) -> int:
        """Estimate annual volume potential for a brand partnership"""
        # Base volume on revenue and market reach
        base_volume = brand_agent.annual_revenue_millions * 10  # Rough units per million revenue
        
        # Adjust for market reach
        base_volume *= brand_agent.geographic_reach
        
        # Adjust for production flexibility
        base_volume *= brand_agent.production_flexibility
        
        # Adjust for outsourcing tendency
        base_volume *= (0.5 + brand_agent.outsourcing_ratio * 0.5)
        
        return int(base_volume)
    
    def optimize_pricing_for_brand(self, 
                                  brand_agent: BrandAgent,
                                  product: str,
                                  model: str) -> Dict[str, Any]:
        """
        Optimize pricing for a specific brand and product
        
        Args:
            brand_agent: The brand to price for
            product: The product to price
            model: Partnership model (co-branded or white-label)
            
        Returns:
            Optimized pricing proposal
        """
        base_price = self.pricing_strategy[product][model]
        variable_cost = self.product_portfolio[product]['variable_cost']
        
        # Adjust for brand's price elasticity
        elasticity_adjustment = 1 + (brand_agent.price_elasticity * 0.1)
        
        # Adjust for brand's financial capacity
        if brand_agent.annual_revenue_millions < 100:
            capacity_adjustment = 0.8  # 20% discount for smaller brands
        elif brand_agent.annual_revenue_millions > 1000:
            capacity_adjustment = 1.1  # 10% premium for large brands
        else:
            capacity_adjustment = 1.0
        
        # Adjust for strategic value
        partnership_assessment = self.evaluate_brand_partnership_potential(brand_agent)
        if partnership_assessment['partnership_priority'] == 'high':
            strategic_adjustment = 0.9  # 10% discount for strategic partners
        else:
            strategic_adjustment = 1.0
        
        # UPDATED: Additional discount based on inferred expansion interest
        segment_move_discount = 1.0
        expansion_signals = self._infer_segment_expansion_interest(brand_agent)
        if expansion_signals > 0.7:
            segment_move_discount = 0.95  # 5% additional discount as incentive
        
        # Calculate final price
        optimized_price = base_price * elasticity_adjustment * capacity_adjustment * strategic_adjustment * segment_move_discount
        
        # Ensure minimum margin
        minimum_price = variable_cost * (1 + self.pricing_strategy[product]['minimum_margin'])
        final_price = max(optimized_price, minimum_price)
        
        # Volume-based discounts
        estimated_volume = partnership_assessment['estimated_volume_potential']
        volume_discount = 0
        if estimated_volume > 10000:
            volume_discount = 0.15
        elif estimated_volume > 5000:
            volume_discount = 0.10
        elif estimated_volume > 1000:
            volume_discount = 0.05
        
        final_price *= (1 - volume_discount)
        
        return {
            "product": product,
            "model": model,
            "base_price": base_price,
            "optimized_price": final_price,
            "variable_cost": variable_cost,
            "margin_percentage": ((final_price - variable_cost) / final_price) * 100,
            "volume_discount": volume_discount * 100,
            "estimated_annual_volume": estimated_volume,
            "estimated_annual_revenue": final_price * estimated_volume,
            "price_adjustments": {
                "elasticity": elasticity_adjustment,
                "capacity": capacity_adjustment,
                "strategic": strategic_adjustment,
                "volume": 1 - volume_discount,
                "segment_move": segment_move_discount  # Based on inferred signals
            }
        }
    
    def propose_partnership_package(self, brand_agent: BrandAgent) -> Dict[str, Any]:
        """
        Create a complete partnership proposal for a brand
        
        Args:
            brand_agent: The brand to create a proposal for
            
        Returns:
            Complete partnership package proposal
        """
        assessment = self.evaluate_brand_partnership_potential(brand_agent)
        
        # Select top 3 products
        product_proposals = []
        for product_name, score in assessment['priority_products']:
            # Price for both models
            co_branded_pricing = self.optimize_pricing_for_brand(brand_agent, product_name, "co-branded")
            white_label_pricing = self.optimize_pricing_for_brand(brand_agent, product_name, "white-label")
            
            product_proposals.append({
                "product": product_name,
                "recommendation_score": score,
                "co_branded_offer": co_branded_pricing,
                "white_label_offer": white_label_pricing,
                "recommended_model": assessment['recommended_model']
            })
        
        # Calculate total package value
        total_co_branded_value = sum(p['co_branded_offer']['estimated_annual_revenue'] for p in product_proposals)
        total_white_label_value = sum(p['white_label_offer']['estimated_annual_revenue'] for p in product_proposals)
        
        return {
            "brand": brand_agent.brand_name,
            "partnership_assessment": assessment,
            "product_proposals": product_proposals,
            "package_summary": {
                "recommended_model": assessment['recommended_model'],
                "total_products": len(product_proposals),
                "estimated_annual_value_co_branded": total_co_branded_value,
                "estimated_annual_value_white_label": total_white_label_value,
                "strategic_benefits": self._identify_strategic_benefits(brand_agent, assessment)
            },
            "next_steps": [
                "Technical feasibility assessment",
                "Pilot program design",
                "Contract negotiation",
                "Implementation timeline"
            ]
        }
    
    def _identify_strategic_benefits(self, brand_agent: BrandAgent, assessment: Dict[str, Any]) -> List[str]:
        """Identify strategic benefits of partnering with a brand"""
        benefits = []
        
        if assessment['market_influence'] > 0.7:
            benefits.append(f"Access to {brand_agent.brand_name}'s strong market influence")
        
        if brand_agent.geographic_reach > 0.8:
            benefits.append("Global market expansion opportunity")
        
        if brand_agent.segment_id != self.segment_id:
            benefits.append(f"Entry into new market segments: {brand_agent.segment_id}")
        
        if brand_agent.sustainability_score > 0.7:
            benefits.append("Sustainability credibility enhancement")
        
        if len(brand_agent.primary_rivals) > 5:
            benefits.append("Competitive differentiation in crowded market")
        
        # UPDATED: Add benefit based on inferred expansion signals
        if assessment.get('segment_expansion_signals', 0) > 0.5:
            benefits.append(f"Strong market signals suggest partner interest in technical enhancement")
        
        return benefits


def load_macron_agent() -> MacronAgent:
    """Load the Macron agent with its special configuration"""
    macron_data_path = Path("company_data/Macron.json")
    
    if not macron_data_path.exists():
        logger.error("Macron data file not found!")
        raise FileNotFoundError(f"Missing {macron_data_path}")
    
    # Load Macron data
    agent = MacronAgent.from_json_file(macron_data_path)
    
    # Verify fixed values are set correctly
    assert agent.risk_appetite == 0.8, f"Macron risk appetite should be 0.8, got {agent.risk_appetite}"
    assert agent.decision_speed == 0.7, f"Macron decision speed should be 0.7, got {agent.decision_speed}"
    
    logger.info(f"🚀 Loaded Macron agent with {len(agent.product_portfolio)} products")
    logger.info(f"   Risk Appetite: {agent.risk_appetite} (fixed)")
    logger.info(f"   Decision Speed: {agent.decision_speed} (fixed)")
    
    return agent


def main():
    """Test the Macron agent"""
    print("🚀 MACRON AGENT MODULE TEST")
    print("=" * 50)
    
    # Load Macron agent
    macron = load_macron_agent()
    
    print(f"\n📊 Macron Profile:")
    print(f"   Revenue: €{macron.annual_revenue_millions}M")
    print(f"   Technical Capability: {macron.technical_capability}")
    print(f"   Products: {len(macron.product_portfolio)}")
    
    # Test with loading a brand agent
    from .brand_agent import BrandAgent
    gucci_path = Path("company_data/Gucci.json")
    if gucci_path.exists():
        gucci = BrandAgent.from_json_file(gucci_path)
        
        # Test partnership evaluation
        print(f"\n🤝 Evaluating Partnership with {gucci.brand_name}:")
        assessment = macron.evaluate_brand_partnership_potential(gucci)
        print(f"   Strategic Fit: {assessment['strategic_fit_score']:.2f}")
        print(f"   Recommended Model: {assessment['recommended_model']}")
        print(f"   Priority: {assessment['partnership_priority']}")
        
        # Test pricing optimization
        if assessment['priority_products']:
            product = assessment['priority_products'][0][0]
            print(f"\n💰 Pricing for {product}:")
            pricing = macron.optimize_pricing_for_brand(gucci, product, "co-branded")
            print(f"   Optimized Price: €{pricing['optimized_price']:.2f}")
            print(f"   Margin: {pricing['margin_percentage']:.1f}%")
            print(f"   Est. Annual Revenue: €{pricing['estimated_annual_revenue']:,.0f}")


if __name__ == "__main__":
    main() 