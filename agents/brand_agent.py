#!/usr/bin/env python3
"""
Brand Agent Module for ModaMesh™
LangChain-based agents representing Italian fashion brands in the ModaMesh™ simulation.
Each agent has decision-making capabilities based on brand intelligence data.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import sys
sys.path.append('..')  # Add parent directory to path

from langchain.agents import Agent
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models.base import BaseChatModel
from langchain_core.runnables import RunnablePassthrough

from italian_fashion_market import ItalianFashionMarket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BrandAgent:
    """
    LangChain agent representing an Italian fashion brand.
    Combines brand intelligence data with decision-making capabilities.
    """
    # Basic identification
    brand_name: str
    
    # Company basics
    is_public: int
    years_in_business: int
    headquarter_italy: int
    
    # Financial data
    annual_revenue_millions: float
    revenue_growth_rate: float
    profit_margin: float
    ebitda_margin: float
    financial_strength_score: float
    
    # Market position
    segment_id: List[int]
    avg_price_index: float
    price_tier: int
    geographic_reach: float
    market_share_estimate: float
    
    # Innovation profile
    technical_capability: float
    r_and_d_intensity: float
    innovation_count: int
    sustainability_score: float
    patent_count: int
    
    # Partnership history
    total_partnerships_3yr: int
    sportswear_partnerships: int
    partnership_success_rate: float
    collaboration_frequency: float
    outsourcing_ratio: float
    
    # Brand metrics
    heritage_score: float
    innovation_perception: float
    target_age_median: int
    target_income_index: int
    brand_heat: float
    
    # Operations
    production_flexibility: float
    technical_manufacturing: float
    supply_chain_complexity: float
    digital_maturity: float
    lead_time_index: int
    
    # Competitive position
    competitor_count: int
    competitive_intensity: float
    differentiation_score: float
    disruption_risk: float
    strategic_agility: float
    
    # Demand elasticity
    price_elasticity: float
    trend_responsiveness: float
    functionality_premium: float
    sustainability_premium: float
    brand_loyalty: float
    segment_fluidity: float
    
    # Resilience metrics
    covid_performance: float
    recession_beta: float
    crisis_recovery_speed: float
    supply_chain_redundancy: float
    inventory_flexibility: float
    
    # Influence metrics
    market_leader_score: float
    media_amplification: float
    influencer_affinity: float
    viral_potential: float
    competitor_monitoring: float
    
    # Strategic flexibility
    pivot_history: int
    channel_flexibility: float
    price_ladder_range: float
    brand_stretch_limit: float
    ip_dependency: float
    
    # Rivalry matrix
    primary_rivals: List[str]
    rivalry_intensity: Dict[str, float]
    differentiation_axes: Dict[str, float]
    
    # Market dynamics
    home_market_advantage: float
    new_entrant_resistance: float
    brand_dilution_sensitivity: float
    segment_permeability: float
    
    # Dynamic attributes (randomly generated)
    risk_appetite: float = field(default_factory=lambda: random.random())
    decision_speed: float = field(default_factory=lambda: random.random())
    appetite_for_high_performance_luxury_move: float = field(default=0.5)
    
    # Segment information from Italian Fashion Market
    segment_names: List[str] = field(default_factory=list)
    segment_characteristics: Dict[str, Any] = field(default_factory=dict)
    
    # LangChain components
    memory: ConversationBufferMemory = field(default_factory=lambda: ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    ))
    
    def __post_init__(self):
        """Initialize the agent's decision-making prompt"""
        self._set_appetite_for_luxury_move()
        self._load_segment_information()
        self.system_prompt = self._create_system_prompt()
        self.decision_chain = self._create_decision_chain()
    
    def _set_appetite_for_luxury_move(self):
        """Set appetite for high-performance luxury move based on segment positioning"""
        # Define segment fashion and function scores
        segment_scores = {
            1: {'fashion': 0.2, 'function': 1.0},  # Core Technical Sportswear
            2: {'fashion': 0.4, 'function': 0.8},  # Outdoor Technical Sportswear
            3: {'fashion': 0.6, 'function': 0.4},  # Athleisure
            4: {'fashion': 0.4, 'function': 0.8},  # Luxury Activewear
            5: {'fashion': 0.8, 'function': 0.4},  # Athluxury
            6: {'fashion': 0.8, 'function': 0.8},  # High-Performance Luxury
            7: {'fashion': 1.0, 'function': 0.2}   # Luxury Fashion
        }
        
        # Calculate weighted average scores for brands in multiple segments
        total_fashion = 0
        total_function = 0
        segment_count = len(self.segment_id)
        
        for seg_id in self.segment_id:
            if seg_id in segment_scores:
                total_fashion += segment_scores[seg_id]['fashion']
                total_function += segment_scores[seg_id]['function']
        
        avg_fashion = total_fashion / segment_count if segment_count > 0 else 0
        avg_function = total_function / segment_count if segment_count > 0 else 0
        
        # Calculate appetite based on fashion-function gap
        # High fashion + Low function = High appetite to move to HP Luxury
        # Low fashion + High function = Low appetite (already technical)
        # Segment 6 brands = Zero appetite (already there)
        
        if 6 in self.segment_id:
            # Already in High-Performance Luxury
            self.appetite_for_high_performance_luxury_move = 0.0
        else:
            # Fashion advantage over function = desire for technical credibility
            fashion_function_gap = avg_fashion - avg_function
            
            # Brands strong in fashion but weak in function have highest appetite
            # Gap ranges from -0.8 (pure technical) to +0.8 (pure fashion)
            # Normalize to 0-1 scale where high fashion/low function = 1
            base_appetite = (fashion_function_gap + 0.8) / 1.6
            
            # Additional factors:
            # - Innovation perception gap (low innovation perception increases appetite)
            innovation_gap_factor = max(0, 0.7 - self.innovation_perception) / 0.7
            
            # - Technical capability gap (low technical capability increases appetite if fashion-forward)
            if avg_fashion > 0.6:  # Fashion-forward brands
                tech_gap_factor = max(0, 0.6 - self.technical_capability) / 0.6
            else:
                tech_gap_factor = 0  # Technical brands don't need to move
            
            # - Segment 5 & 7 bonus (explicitly mentioned in requirements)
            segment_bonus = 0.2 if any(seg in [5, 7] for seg in self.segment_id) else 0
            
            # Combine factors with weights
            self.appetite_for_high_performance_luxury_move = min(1.0, 
                base_appetite * 0.5 +
                innovation_gap_factor * 0.2 +
                tech_gap_factor * 0.2 +
                segment_bonus
            )
            
            # Add small random variation for realism
            self.appetite_for_high_performance_luxury_move = max(0, min(1.0,
                self.appetite_for_high_performance_luxury_move + random.uniform(-0.1, 0.1)
            ))
    
    def _load_segment_information(self):
        """Load segment information from Italian Fashion Market"""
        try:
            market = ItalianFashionMarket("data/italian_fashion_market.json")
            brand_info = market.get_brand_segments(self.brand_name)
            
            if brand_info:
                self.segment_names = [seg.segment_name for seg in brand_info.segments]
                self.segment_characteristics = {
                    seg.segment_name: {
                        'functionality_score': seg.functionality_score,
                        'fashion_score': seg.fashion_score,
                        'definition': seg.definition
                    }
                    for seg in brand_info.segments
                }
                logger.debug(f"Loaded segment info for {self.brand_name}: {self.segment_names}")
        except Exception as e:
            logger.warning(f"Could not load segment information for {self.brand_name}: {e}")
    
    def _create_system_prompt(self) -> str:
        """Create a system prompt that captures the brand's personality and decision criteria"""
        return f"""You are the strategic decision-maker for {self.brand_name}, an Italian fashion brand.

Your brand profile:
- Revenue: €{self.annual_revenue_millions}M (Growth: {self.revenue_growth_rate*100:.1f}%)
- Market segments: {self.segment_id} ({', '.join(self.segment_names) if self.segment_names else 'N/A'})
- Technical capability: {self.technical_capability:.2f}
- Innovation perception: {self.innovation_perception:.2f}
- Risk appetite: {self.risk_appetite:.2f}
- Decision speed: {self.decision_speed:.2f}
- Appetite for high-performance luxury move: {self.appetite_for_high_performance_luxury_move:.2f}

Key characteristics:
- You have {self.years_in_business} years of heritage
- Your partnership success rate is {self.partnership_success_rate*100:.0f}%
- You've had {self.sportswear_partnerships} sportswear partnerships in the last 3 years
- Your brand heat score is {self.brand_heat:.2f}

Decision criteria for technical partnerships:
1. Brand alignment: Does this enhance or dilute our brand?
2. Technical gap: Do we need this capability? (Current: {self.technical_capability:.2f})
3. Financial viability: Can we afford it and will it generate ROI?
4. Competitive advantage: Will this differentiate us from {', '.join(self.primary_rivals[:3])}?
5. Risk assessment: Does this align with our risk appetite ({self.risk_appetite:.2f})?

You make decisions based on data and your brand's strategic position."""

    def _create_decision_chain(self):
        """Create the LangChain decision-making chain"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Create a simple chain for decision-making
        chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: self.memory.chat_memory.messages
            )
            | prompt
        )
        
        return chain
    
    def evaluate_partnership_opportunity(self, 
                                       product: str,
                                       model: str,  # "co-branded" or "white-label"
                                       price_per_unit: float,
                                       technical_specs: Dict[str, Any],
                                       market_intelligence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate a partnership opportunity with Macron
        
        Args:
            product: Name of the Macron product
            model: Partnership model (co-branded or white-label)
            price_per_unit: Proposed price per unit
            technical_specs: Technical specifications of the product
            market_intelligence: Market data from MarketStateManager (optional)
            
        Returns:
            Dictionary with decision and reasoning
        """
        # Calculate affordability based on revenue and margins
        affordable_investment = self.annual_revenue_millions * self.ebitda_margin * 0.1  # 10% of EBITDA
        
        # Evaluate technical fit
        technical_gap = max(0, 0.8 - self.technical_capability)  # Target 0.8 capability
        
        # Evaluate brand fit for co-branded, operational fit for white-label
        if model == "co-branded":
            # CO-BRANDED: Focus on brand dilution concerns
            brand_dilution_concern = self.brand_dilution_sensitivity * (1 - self.technical_capability)
            # Reduce concern if brand wants to move to high-performance luxury
            if self.appetite_for_high_performance_luxury_move > 0.5:
                brand_dilution_concern *= (1 - self.appetite_for_high_performance_luxury_move * 0.5)
            operational_benefit = 0.0  # Not a primary factor for co-branded
        else:
            # WHITE-LABEL: Focus on operational benefits
            brand_dilution_concern = 0.05  # Minimal concern for white-label
            
            # Calculate operational benefit score based on production constraints
            operational_constraints = []
            
            # Low production flexibility = higher need for outsourcing
            if self.production_flexibility < 0.4:
                operational_constraints.append(0.3)
            elif self.production_flexibility < 0.6:
                operational_constraints.append(0.15)
            
            # Low technical manufacturing capability = benefit from Macron's expertise
            if self.technical_manufacturing < 0.5:
                operational_constraints.append(0.25)
            elif self.technical_manufacturing < 0.7:
                operational_constraints.append(0.1)
            
            # High supply chain complexity = benefit from simplification
            if self.supply_chain_complexity > 0.7:
                operational_constraints.append(0.2)
            elif self.supply_chain_complexity > 0.5:
                operational_constraints.append(0.1)
            
            # Long lead times = benefit from Macron's efficiency
            if self.lead_time_index > 3:  # Assuming 1-5 scale
                operational_constraints.append(0.15)
            
            # High existing outsourcing ratio = comfortable with model
            if self.outsourcing_ratio > 0.5:
                operational_constraints.append(0.15)
            
            # Calculate total operational benefit
            operational_benefit = min(sum(operational_constraints), 0.5)  # Cap at 0.5
        
        # Initialize market adjustment factors
        market_adjustment = 1.0
        sustainability_boost = 0.0
        economic_penalty = 0.0
        
        # Apply market intelligence if available
        if market_intelligence:
            consumer_prefs = market_intelligence.get('consumer_preferences', {})
            market_indicators = market_intelligence.get('market_indicators', {})
            opportunities = market_intelligence.get('opportunities', [])
            threats = market_intelligence.get('threats', [])
            
            # Adjust for functionality importance
            if consumer_prefs.get('functionality_importance', 0.5) > 0.6:
                if 'Technical' in technical_specs.get('category', '') or technical_specs.get('complexity', '') in ['High', 'Very High']:
                    market_adjustment *= 1.2  # 20% boost for technical products when market values functionality
            
            # Adjust for sustainability importance
            if consumer_prefs.get('sustainability_importance', 0.3) > 0.5:
                if 'Sustainable' in product or 'Recycled' in product or 'Bio' in product:
                    sustainability_boost = 0.15  # 15% boost for sustainable products
            
            # Adjust for economic conditions
            economic_confidence = market_indicators.get('economic_confidence', 0.7)
            if economic_confidence < 0.5:
                # During economic downturn, be more conservative
                economic_penalty = (0.5 - economic_confidence) * 0.3
                # But white-label becomes more attractive (lower cost, no brand risk)
                if model == "white-label":
                    economic_penalty *= 0.5
                    # Additional benefit if we have operational constraints
                    if operational_benefit > 0.2:
                        economic_penalty *= 0.7  # Further reduce penalty
            
            # Consider opportunities
            for opp in opportunities:
                if opp['type'] == 'segment_expansion' and opp['target'] == 'High-Performance Luxury':
                    if self.appetite_for_high_performance_luxury_move > 0.3:
                        market_adjustment *= 1.1  # 10% boost if opportunity aligns with internal appetite
            
            # Consider threats
            for threat in threats:
                if threat['type'] == 'economic_downturn':
                    # Already handled above
                    pass
                elif threat['type'] == 'sustainability_compliance':
                    # Increase importance of sustainable products
                    if 'Sustainable' in product:
                        market_adjustment *= 1.15
        
        # Calculate partnership propensity score with market adjustments
        if model == "co-branded":
            # Co-branded focuses on brand and market alignment
            base_propensity = (
                self.risk_appetite * 0.20 +
                technical_gap * 0.20 +
                self.partnership_success_rate * 0.15 +
                (1 - brand_dilution_concern) * 0.20 +  # Higher weight on brand concerns
                self.appetite_for_high_performance_luxury_move * 0.10 +
                sustainability_boost  # Market-driven sustainability boost
            )
        else:
            # White-label focuses on operational efficiency and cost
            base_propensity = (
                self.risk_appetite * 0.15 +
                technical_gap * 0.15 +
                self.partnership_success_rate * 0.10 +
                operational_benefit * 0.35 +  # Major factor for white-label
                (1 - brand_dilution_concern) * 0.05 +  # Minor factor
                self.outsourcing_ratio * 0.10 +  # Comfort with outsourcing
                sustainability_boost  # Market-driven sustainability boost
            )
        
        # Apply market adjustment and economic penalty
        propensity_score = base_propensity * market_adjustment * (1 - economic_penalty)
        
        # Price sensitivity adjustment based on market conditions
        if market_intelligence:
            price_sensitivity_market = consumer_prefs.get('price_sensitivity', 0.4)
            # If market is price sensitive and we are too, be more cautious
            if price_sensitivity_market > 0.6 and abs(self.price_elasticity) > 1:
                propensity_score *= 0.9
                # But white-label is more price-efficient
                if model == "white-label":
                    propensity_score *= 1.1
        
        # Adjust for financial capability
        if price_per_unit * 1000 > affordable_investment:  # Assume 1000 units minimum
            propensity_score *= 0.5
            # Less penalty for white-label as it requires less upfront investment
            if model == "white-label":
                propensity_score *= 1.2
        
        # Make decision
        decision = propensity_score > 0.5
        
        return {
            "brand": self.brand_name,
            "product": product,
            "model": model,
            "decision": decision,
            "propensity_score": propensity_score,
            "reasoning": {
                "technical_gap": technical_gap,
                "brand_dilution_concern": brand_dilution_concern,
                "operational_benefit": operational_benefit,
                "affordable_investment": affordable_investment,
                "risk_alignment": abs(self.risk_appetite - 0.5) < 0.3,
                "market_adjustment": market_adjustment,
                "sustainability_boost": sustainability_boost,
                "economic_penalty": economic_penalty
            },
            "operational_factors": {
                "production_flexibility": self.production_flexibility,
                "technical_manufacturing": self.technical_manufacturing,
                "supply_chain_complexity": self.supply_chain_complexity,
                "lead_time_index": self.lead_time_index,
                "outsourcing_ratio": self.outsourcing_ratio
            } if model == "white-label" else None,
            "counter_offer": {
                "suggested_price": price_per_unit * (1 - self.price_elasticity * 0.1) if not decision else None,
                "preferred_model": "white-label" if (brand_dilution_concern > 0.5 or operational_benefit > 0.3) else model
            },
            "market_influenced": market_intelligence is not None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent data to dictionary (excluding LangChain components)"""
        data = {}
        for key, value in self.__dict__.items():
            if key not in ['memory', 'decision_chain', 'system_prompt']:
                data[key] = value
        return data
    
    @classmethod
    def from_json_file(cls, filepath: Path) -> 'BrandAgent':
        """Create a BrandAgent from a JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract nested data
        brand_data = {
            'brand_name': data['brand_name'],
            
            # Company basics
            'is_public': data['company_basics']['is_public'],
            'years_in_business': data['company_basics']['years_in_business'],
            'headquarter_italy': data['company_basics']['headquarter_italy'],
            
            # Financial data
            'annual_revenue_millions': data['financial_data']['annual_revenue_millions'],
            'revenue_growth_rate': data['financial_data']['revenue_growth_rate'],
            'profit_margin': data['financial_data']['profit_margin'],
            'ebitda_margin': data['financial_data']['ebitda_margin'],
            'financial_strength_score': data['financial_data']['financial_strength_score'],
            
            # Market position
            'segment_id': data['market_position']['segment_id'],
            'avg_price_index': data['market_position']['avg_price_index'],
            'price_tier': data['market_position']['price_tier'],
            'geographic_reach': data['market_position']['geographic_reach'],
            'market_share_estimate': data['market_position']['market_share_estimate'],
            
            # Innovation profile
            'technical_capability': data['innovation_profile']['technical_capability'],
            'r_and_d_intensity': data['innovation_profile']['r_and_d_intensity'],
            'innovation_count': data['innovation_profile']['innovation_count'],
            'sustainability_score': data['innovation_profile']['sustainability_score'],
            'patent_count': data['innovation_profile']['patent_count'],
            
            # Partnership history
            'total_partnerships_3yr': data['partnership_history']['total_partnerships_3yr'],
            'sportswear_partnerships': data['partnership_history']['sportswear_partnerships'],
            'partnership_success_rate': data['partnership_history']['partnership_success_rate'],
            'collaboration_frequency': data['partnership_history']['collaboration_frequency'],
            'outsourcing_ratio': data['partnership_history']['outsourcing_ratio'],
            
            # Brand metrics
            'heritage_score': data['brand_metrics']['heritage_score'],
            'innovation_perception': data['brand_metrics']['innovation_perception'],
            'target_age_median': data['brand_metrics']['target_age_median'],
            'target_income_index': data['brand_metrics']['target_income_index'],
            'brand_heat': data['brand_metrics']['brand_heat'],
            
            # Operations
            'production_flexibility': data['operations']['production_flexibility'],
            'technical_manufacturing': data['operations']['technical_manufacturing'],
            'supply_chain_complexity': data['operations']['supply_chain_complexity'],
            'digital_maturity': data['operations']['digital_maturity'],
            'lead_time_index': data['operations']['lead_time_index'],
            
            # Competitive position
            'competitor_count': data['competitive_position']['competitor_count'],
            'competitive_intensity': data['competitive_position']['competitive_intensity'],
            'differentiation_score': data['competitive_position']['differentiation_score'],
            'disruption_risk': data['competitive_position']['disruption_risk'],
            'strategic_agility': data['competitive_position']['strategic_agility'],
            
            # Demand elasticity
            'price_elasticity': data['demand_elasticity']['price_elasticity'],
            'trend_responsiveness': data['demand_elasticity']['trend_responsiveness'],
            'functionality_premium': data['demand_elasticity']['functionality_premium'],
            'sustainability_premium': data['demand_elasticity']['sustainability_premium'],
            'brand_loyalty': data['demand_elasticity']['brand_loyalty'],
            'segment_fluidity': data['demand_elasticity']['segment_fluidity'],
            
            # Resilience metrics
            'covid_performance': data['resilience_metrics']['covid_performance'],
            'recession_beta': data['resilience_metrics']['recession_beta'],
            'crisis_recovery_speed': data['resilience_metrics']['crisis_recovery_speed'],
            'supply_chain_redundancy': data['resilience_metrics']['supply_chain_redundancy'],
            'inventory_flexibility': data['resilience_metrics']['inventory_flexibility'],
            
            # Influence metrics
            'market_leader_score': data['influence_metrics']['market_leader_score'],
            'media_amplification': data['influence_metrics']['media_amplification'],
            'influencer_affinity': data['influence_metrics']['influencer_affinity'],
            'viral_potential': data['influence_metrics']['viral_potential'],
            'competitor_monitoring': data['influence_metrics']['competitor_monitoring'],
            
            # Strategic flexibility
            'pivot_history': data['strategic_flexibility']['pivot_history'],
            'channel_flexibility': data['strategic_flexibility']['channel_flexibility'],
            'price_ladder_range': data['strategic_flexibility']['price_ladder_range'],
            'brand_stretch_limit': data['strategic_flexibility']['brand_stretch_limit'],
            'ip_dependency': data['strategic_flexibility']['ip_dependency'],
            
            # Rivalry matrix
            'primary_rivals': data['rivalry_matrix']['primary_rivals'],
            'rivalry_intensity': data['rivalry_matrix']['rivalry_intensity'],
            'differentiation_axes': data['rivalry_matrix']['differentiation_axes'],
            
            # Market dynamics
            'home_market_advantage': data['market_dynamics']['home_market_advantage'],
            'new_entrant_resistance': data['market_dynamics']['new_entrant_resistance'],
            'brand_dilution_sensitivity': data['market_dynamics']['brand_dilution_sensitivity'],
            'segment_permeability': data['market_dynamics']['segment_permeability']
        }
        
        return cls(**brand_data)


def load_all_brand_agents(company_data_dir: str = "company_data") -> Dict[str, BrandAgent]:
    """
    Load all brand agents from the company data directory
    
    Args:
        company_data_dir: Path to directory containing company JSON files
        
    Returns:
        Dictionary mapping brand names to BrandAgent instances
    """
    agents = {}
    data_path = Path(company_data_dir)
    
    if not data_path.exists():
        logger.error(f"Company data directory not found: {company_data_dir}")
        return agents
    
    # Load all JSON files except Macron and summary files
    for json_file in data_path.glob("*.json"):
        # Skip Macron (special agent) and summary files
        if json_file.stem in ["Macron", "_collection_summary", "_failed_brands"]:
            continue
        
        try:
            agent = BrandAgent.from_json_file(json_file)
            agents[agent.brand_name] = agent
            logger.info(f"✅ Loaded agent for {agent.brand_name} (risk: {agent.risk_appetite:.2f}, speed: {agent.decision_speed:.2f}, luxury move: {agent.appetite_for_high_performance_luxury_move:.2f})")
        except Exception as e:
            logger.error(f"❌ Failed to load {json_file.stem}: {e}")
    
    logger.info(f"🎯 Loaded {len(agents)} brand agents successfully")
    return agents


def main():
    """Test the brand agent loading"""
    print("🤖 BRAND AGENT MODULE TEST")
    print("=" * 50)
    
    # Load all agents
    agents = load_all_brand_agents()
    
    # Test with a sample agent
    if "Gucci" in agents:
        gucci = agents["Gucci"]
        print(f"\n📊 Sample Agent: {gucci.brand_name}")
        print(f"   Revenue: €{gucci.annual_revenue_millions}M")
        print(f"   Segments: {gucci.segment_id}")
        print(f"   Segment Names: {gucci.segment_names}")
        print(f"   Risk Appetite: {gucci.risk_appetite:.2f}")
        print(f"   Decision Speed: {gucci.decision_speed:.2f}")
        print(f"   Appetite for HP Luxury Move: {gucci.appetite_for_high_performance_luxury_move:.2f}")
        
        # Test partnership evaluation
        result = gucci.evaluate_partnership_opportunity(
            product="Performance Jacquard Reinforcement",
            model="co-branded",
            price_per_unit=120.0,
            technical_specs={"stretch": "4-way", "weight_reduction": "23%"},
            market_intelligence=None
        )
        
        print(f"\n🤝 Partnership Evaluation:")
        print(f"   Decision: {'Accept' if result['decision'] else 'Reject'}")
        print(f"   Propensity Score: {result['propensity_score']:.2f}")
        print(f"   Technical Gap: {result['reasoning']['technical_gap']:.2f}")


if __name__ == "__main__":
    main() 