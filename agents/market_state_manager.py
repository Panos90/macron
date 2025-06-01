#!/usr/bin/env python3
"""
Market State Manager for ModaMesh™ Simulation
Manages and evolves market conditions over time in the ModaMesh™ simulation.
Tracks consumer preferences, segment dynamics, and market indicators.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConsumerPreferences:
    """Tracks what consumers value in the market"""
    functionality_importance: float = 0.5  # 0-1, importance of technical features
    sustainability_importance: float = 0.3  # 0-1, importance of eco-friendly aspects
    brand_status_importance: float = 0.7   # 0-1, importance of brand prestige
    price_sensitivity: float = 0.4         # 0-1, how much price matters (1 = very sensitive)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'functionality_importance': self.functionality_importance,
            'sustainability_importance': self.sustainability_importance,
            'brand_status_importance': self.brand_status_importance,
            'price_sensitivity': self.price_sensitivity
        }


@dataclass
class MarketIndicators:
    """Tracks broader market trends and pressures"""
    technical_innovation_heat: float = 0.5        # 0-1, market excitement for tech innovation
    luxury_technical_convergence: float = 0.3     # 0-1, luxury brands adopting technical features
    sustainability_pressure: float = 0.4          # 0-1, regulatory and social pressure for sustainability
    economic_confidence: float = 0.7              # 0-1, overall economic health (affects spending)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'technical_innovation_heat': self.technical_innovation_heat,
            'luxury_technical_convergence': self.luxury_technical_convergence,
            'sustainability_pressure': self.sustainability_pressure,
            'economic_confidence': self.economic_confidence
        }


@dataclass
class SegmentDynamics:
    """Tracks growth and trends for each market segment"""
    segment_growth_rates: Dict[int, float] = field(default_factory=lambda: {
        1: 0.02,  # Core Technical Sportswear - mature, slow growth
        2: 0.05,  # Outdoor Technical - growing with outdoor trend
        3: 0.04,  # Athleisure - steady growth
        4: 0.08,  # Luxury Activewear - high growth
        5: 0.06,  # Athluxury - strong growth
        6: 0.10,  # High-Performance Luxury - highest growth (key segment)
        7: 0.01   # Luxury Fashion - slow growth, mature
    })
    
    segment_saturation: Dict[int, float] = field(default_factory=lambda: {
        1: 0.8,   # Core Technical - highly saturated
        2: 0.6,   # Outdoor Technical - moderate saturation
        3: 0.7,   # Athleisure - fairly saturated
        4: 0.4,   # Luxury Activewear - room to grow
        5: 0.3,   # Athluxury - early stage
        6: 0.2,   # High-Performance Luxury - nascent
        7: 0.9    # Luxury Fashion - very saturated
    })
    
    def to_dict(self) -> Dict[str, Dict[int, float]]:
        return {
            'growth_rates': self.segment_growth_rates,
            'saturation_levels': self.segment_saturation
        }


class MarketStateManager:
    """
    Manages the evolution of market conditions over time.
    Provides market intelligence to brand agents for decision-making.
    """
    
    def __init__(self, initial_seed: Optional[int] = None):
        """Initialize market state manager"""
        if initial_seed:
            random.seed(initial_seed)
            np.random.seed(initial_seed)
        
        # Core market state components
        self.consumer_preferences = ConsumerPreferences()
        self.market_indicators = MarketIndicators()
        self.segment_dynamics = SegmentDynamics()
        
        # Time tracking
        self.current_quarter = 1
        self.current_year = 1
        self.time_step = 0
        
        # Historical tracking
        self.history = {
            'consumer_preferences': [],
            'market_indicators': [],
            'segment_dynamics': []
        }
        
        # Shock event tracking
        self.active_shocks = []
        self.shock_history = []
        
        # Market segment names for reference
        self.segment_names = {
            1: "Core Technical Sportswear",
            2: "Outdoor Technical Sportswear",
            3: "Athleisure",
            4: "Luxury Activewear",
            5: "Athluxury",
            6: "High-Performance Luxury",
            7: "Luxury Fashion"
        }
        
        # Save initial state
        self._save_to_history()
        
        logger.info("📊 Market State Manager initialized")
    
    def update_market_state(self) -> None:
        """Update market state for the next time period"""
        self.time_step += 1
        self.current_quarter = ((self.time_step - 1) % 4) + 1
        self.current_year = ((self.time_step - 1) // 4) + 1
        
        # Apply natural market evolution
        self._evolve_consumer_preferences()
        self._evolve_market_indicators()
        self._evolve_segment_dynamics()
        
        # Process active shocks
        self._process_active_shocks()
        
        # Save state to history
        self._save_to_history()
        
        logger.info(f"📈 Market updated to Y{self.current_year}Q{self.current_quarter}")
    
    def _evolve_consumer_preferences(self) -> None:
        """Natural evolution of consumer preferences"""
        # Functionality importance grows with tech innovation
        if self.market_indicators.technical_innovation_heat > 0.6:
            self.consumer_preferences.functionality_importance = min(
                1.0, self.consumer_preferences.functionality_importance + 0.01
            )
        
        # Sustainability importance grows over time (long-term trend)
        self.consumer_preferences.sustainability_importance = min(
            1.0, self.consumer_preferences.sustainability_importance + 0.005
        )
        
        # Brand status importance affected by economic confidence
        if self.market_indicators.economic_confidence > 0.7:
            self.consumer_preferences.brand_status_importance = min(
                1.0, self.consumer_preferences.brand_status_importance + 0.005
            )
        else:
            self.consumer_preferences.brand_status_importance = max(
                0.3, self.consumer_preferences.brand_status_importance - 0.01
            )
        
        # Price sensitivity inversely related to economic confidence
        self.consumer_preferences.price_sensitivity = max(
            0.2, 1.0 - (self.market_indicators.economic_confidence * 0.8)
        )
        
        # Add small random fluctuations
        for attr in ['functionality_importance', 'sustainability_importance', 
                    'brand_status_importance', 'price_sensitivity']:
            current = getattr(self.consumer_preferences, attr)
            noise = np.random.normal(0, 0.01)
            setattr(self.consumer_preferences, attr, 
                   max(0.0, min(1.0, current + noise)))
    
    def _evolve_market_indicators(self) -> None:
        """Natural evolution of market indicators"""
        # Technical innovation follows innovation cycles
        innovation_cycle = np.sin(self.time_step * 0.2) * 0.1
        self.market_indicators.technical_innovation_heat = max(0.0, min(1.0,
            self.market_indicators.technical_innovation_heat + innovation_cycle * 0.1
        ))
        
        # Luxury-technical convergence grows over time (major trend)
        self.market_indicators.luxury_technical_convergence = min(
            0.8, self.market_indicators.luxury_technical_convergence + 0.01
        )
        
        # Sustainability pressure increases steadily
        self.market_indicators.sustainability_pressure = min(
            0.9, self.market_indicators.sustainability_pressure + 0.008
        )
        
        # Economic confidence has business cycles
        economic_cycle = np.sin(self.time_step * 0.15) * 0.05
        self.market_indicators.economic_confidence = max(0.2, min(1.0,
            self.market_indicators.economic_confidence + economic_cycle
        ))
    
    def _evolve_segment_dynamics(self) -> None:
        """Update segment growth rates based on market conditions"""
        # Segment 6 (HP Luxury) growth influenced by luxury-tech convergence
        base_rate_6 = 0.10
        convergence_boost = self.market_indicators.luxury_technical_convergence * 0.05
        self.segment_dynamics.segment_growth_rates[6] = base_rate_6 + convergence_boost
        
        # Technical segments (1, 2) affected by functionality importance
        tech_preference_effect = (self.consumer_preferences.functionality_importance - 0.5) * 0.02
        self.segment_dynamics.segment_growth_rates[1] += tech_preference_effect
        self.segment_dynamics.segment_growth_rates[2] += tech_preference_effect
        
        # Luxury segments (7) affected by brand status importance
        luxury_effect = (self.consumer_preferences.brand_status_importance - 0.7) * 0.01
        self.segment_dynamics.segment_growth_rates[7] += luxury_effect
        
        # Update saturation levels based on growth
        for segment_id, growth_rate in self.segment_dynamics.segment_growth_rates.items():
            current_saturation = self.segment_dynamics.segment_saturation[segment_id]
            # Higher growth leads to increasing saturation
            saturation_increase = growth_rate * 0.5 * (1 - current_saturation)
            self.segment_dynamics.segment_saturation[segment_id] = min(
                0.95, current_saturation + saturation_increase
            )
    
    def apply_market_shock(self, shock_type: str, duration: int = 4, intensity: float = 0.5) -> None:
        """
        Apply a market shock that affects conditions
        
        Args:
            shock_type: Type of shock:
                - 'recession': Economic downturn
                - 'sustainability_push': Environmental regulations/awareness
                - 'tech_boom': Technology innovation acceleration
                - 'luxury_crisis': Luxury market disruption
                - 'luxury_tech_convergence': Luxury brands embrace technical innovation
                - 'athleisure_surge': Casualization and comfort trend
                - 'supply_chain_crisis': Global supply chain disruption
                - 'digital_transformation': E-commerce and digital acceleration
                - 'gen_z_takeover': Younger consumer preferences dominate
                - 'performance_fashion': Performance becomes fashionable
            duration: How many quarters the shock lasts
            intensity: Severity of the shock (0.0 to 1.0)
        """
        shock = {
            'type': shock_type,
            'start_time': self.time_step,
            'duration': duration,
            'intensity': intensity,
            'remaining_duration': duration
        }
        
        self.active_shocks.append(shock)
        self.shock_history.append(shock.copy())
        
        # Apply immediate shock effects
        self._apply_shock_effects(shock)
        
        logger.warning(f"⚡ Market shock applied: {shock_type} (intensity: {intensity}, duration: {duration}Q)")
    
    def _apply_shock_effects(self, shock: Dict[str, Any]) -> None:
        """Apply the effects of a market shock"""
        shock_type = shock['type']
        intensity = shock['intensity']
        
        if shock_type == 'recession':
            # Immediate effects of recession
            self.market_indicators.economic_confidence *= (1 - intensity * 0.5)
            self.consumer_preferences.price_sensitivity = min(
                0.9, self.consumer_preferences.price_sensitivity + intensity * 0.3
            )
            self.consumer_preferences.brand_status_importance *= (1 - intensity * 0.2)
            # Reduce growth rates across the board
            for seg_id in self.segment_dynamics.segment_growth_rates:
                self.segment_dynamics.segment_growth_rates[seg_id] *= (1 - intensity * 0.3)
        
        elif shock_type == 'sustainability_push':
            # Regulatory or social push for sustainability
            self.market_indicators.sustainability_pressure = min(
                1.0, self.market_indicators.sustainability_pressure + intensity * 0.3
            )
            self.consumer_preferences.sustainability_importance = min(
                1.0, self.consumer_preferences.sustainability_importance + intensity * 0.2
            )
        
        elif shock_type == 'tech_boom':
            # Technology innovation acceleration
            self.market_indicators.technical_innovation_heat = min(
                1.0, self.market_indicators.technical_innovation_heat + intensity * 0.3
            )
            self.consumer_preferences.functionality_importance = min(
                1.0, self.consumer_preferences.functionality_importance + intensity * 0.2
            )
            # Boost technical segment growth
            self.segment_dynamics.segment_growth_rates[1] *= (1 + intensity * 0.2)
            self.segment_dynamics.segment_growth_rates[2] *= (1 + intensity * 0.3)
            self.segment_dynamics.segment_growth_rates[6] *= (1 + intensity * 0.4)
        
        elif shock_type == 'luxury_crisis':
            # Luxury market disruption (e.g., changing consumer values)
            self.consumer_preferences.brand_status_importance *= (1 - intensity * 0.3)
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.5)
            self.segment_dynamics.segment_growth_rates[4] *= (1 - intensity * 0.3)
        
        elif shock_type == 'luxury_tech_convergence':
            # Major trend: Luxury brands moving into technical performance
            self.market_indicators.luxury_technical_convergence = min(
                0.95, self.market_indicators.luxury_technical_convergence + intensity * 0.4
            )
            # Consumers expect both luxury AND performance
            self.consumer_preferences.functionality_importance = min(
                0.9, self.consumer_preferences.functionality_importance + intensity * 0.15
            )
            # Brand status remains important but now includes technical credibility
            self.consumer_preferences.brand_status_importance = max(
                0.6, self.consumer_preferences.brand_status_importance
            )
            # Massive growth in segment 6 (High-Performance Luxury)
            self.segment_dynamics.segment_growth_rates[6] *= (1 + intensity * 0.6)
            # Moderate growth in segment 5 (Athluxury)
            self.segment_dynamics.segment_growth_rates[5] *= (1 + intensity * 0.3)
            # Traditional luxury segment 7 feels pressure
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.2)
            # Technical innovation becomes crucial
            self.market_indicators.technical_innovation_heat = min(
                0.9, self.market_indicators.technical_innovation_heat + intensity * 0.25
            )
        
        elif shock_type == 'athleisure_surge':
            # Casualization trend accelerates (post-COVID style)
            self.segment_dynamics.segment_growth_rates[3] *= (1 + intensity * 0.5)  # Athleisure
            self.segment_dynamics.segment_growth_rates[5] *= (1 + intensity * 0.3)  # Athluxury
            # Functionality becomes more important in daily wear
            self.consumer_preferences.functionality_importance = min(
                0.8, self.consumer_preferences.functionality_importance + intensity * 0.2
            )
            # Traditional luxury suffers
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.3)
            # Price sensitivity increases slightly (value-conscious)
            self.consumer_preferences.price_sensitivity = min(
                0.7, self.consumer_preferences.price_sensitivity + intensity * 0.1
            )
        
        elif shock_type == 'supply_chain_crisis':
            # Global supply chain disruption (like COVID or Suez blockage)
            # All segments affected but luxury less so (more resources)
            for seg_id in [1, 2, 3]:  # Technical segments hit hardest
                self.segment_dynamics.segment_growth_rates[seg_id] *= (1 - intensity * 0.4)
            for seg_id in [4, 5, 6]:  # Mid-luxury segments moderately affected
                self.segment_dynamics.segment_growth_rates[seg_id] *= (1 - intensity * 0.2)
            # Luxury segment 7 least affected
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.1)
            # Economic confidence drops
            self.market_indicators.economic_confidence *= (1 - intensity * 0.3)
            # Innovation slows due to disruption
            self.market_indicators.technical_innovation_heat *= (1 - intensity * 0.2)
        
        elif shock_type == 'digital_transformation':
            # E-commerce and digital acceleration
            # Benefits technical and innovative brands
            self.segment_dynamics.segment_growth_rates[1] *= (1 + intensity * 0.2)
            self.segment_dynamics.segment_growth_rates[3] *= (1 + intensity * 0.3)  # Athleisure thrives online
            self.segment_dynamics.segment_growth_rates[6] *= (1 + intensity * 0.25)
            # Traditional luxury struggles with digital shift
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.15)
            # Price transparency increases price sensitivity
            self.consumer_preferences.price_sensitivity = min(
                0.8, self.consumer_preferences.price_sensitivity + intensity * 0.15
            )
            # Innovation perception becomes crucial online
            self.market_indicators.technical_innovation_heat = min(
                0.8, self.market_indicators.technical_innovation_heat + intensity * 0.2
            )
        
        elif shock_type == 'gen_z_takeover':
            # Younger consumer preferences dominate market
            # Sustainability becomes paramount
            self.consumer_preferences.sustainability_importance = min(
                0.9, self.consumer_preferences.sustainability_importance + intensity * 0.3
            )
            # Brand status less important than authenticity
            self.consumer_preferences.brand_status_importance *= (1 - intensity * 0.25)
            # Functionality and versatility valued
            self.consumer_preferences.functionality_importance = min(
                0.8, self.consumer_preferences.functionality_importance + intensity * 0.2
            )
            # Boost innovative segments
            self.segment_dynamics.segment_growth_rates[3] *= (1 + intensity * 0.3)  # Athleisure
            self.segment_dynamics.segment_growth_rates[5] *= (1 + intensity * 0.4)  # Athluxury
            self.segment_dynamics.segment_growth_rates[6] *= (1 + intensity * 0.35) # HP Luxury
            # Traditional luxury struggles
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.4)
            # Price consciousness increases
            self.consumer_preferences.price_sensitivity = min(
                0.75, self.consumer_preferences.price_sensitivity + intensity * 0.2
            )
        
        elif shock_type == 'performance_fashion':
            # Performance features become fashion statements
            self.consumer_preferences.functionality_importance = min(
                0.9, self.consumer_preferences.functionality_importance + intensity * 0.25
            )
            # Technical innovation becomes a luxury
            self.market_indicators.technical_innovation_heat = min(
                0.95, self.market_indicators.technical_innovation_heat + intensity * 0.3
            )
            # All technical segments benefit
            self.segment_dynamics.segment_growth_rates[1] *= (1 + intensity * 0.3)
            self.segment_dynamics.segment_growth_rates[2] *= (1 + intensity * 0.35)
            self.segment_dynamics.segment_growth_rates[6] *= (1 + intensity * 0.5)
            # Even luxury activewear benefits
            self.segment_dynamics.segment_growth_rates[4] *= (1 + intensity * 0.25)
            # Traditional fashion must adapt
            self.segment_dynamics.segment_growth_rates[7] *= (1 - intensity * 0.1)
            # Luxury-tech convergence accelerates
            self.market_indicators.luxury_technical_convergence = min(
                0.9, self.market_indicators.luxury_technical_convergence + intensity * 0.3
            )
    
    def _process_active_shocks(self) -> None:
        """Process ongoing shocks and remove expired ones"""
        ongoing_shocks = []
        
        for shock in self.active_shocks:
            shock['remaining_duration'] -= 1
            
            if shock['remaining_duration'] > 0:
                # Continue applying diminishing effects
                diminished_intensity = shock['intensity'] * (shock['remaining_duration'] / shock['duration'])
                shock_copy = shock.copy()
                shock_copy['intensity'] = diminished_intensity * 0.5  # Reduced ongoing effect
                self._apply_shock_effects(shock_copy)
                ongoing_shocks.append(shock)
            else:
                logger.info(f"📊 Market shock ended: {shock['type']}")
        
        self.active_shocks = ongoing_shocks
    
    def _save_to_history(self) -> None:
        """Save current state to history"""
        self.history['consumer_preferences'].append({
            'time_step': self.time_step,
            'year': self.current_year,
            'quarter': self.current_quarter,
            **self.consumer_preferences.to_dict()
        })
        
        self.history['market_indicators'].append({
            'time_step': self.time_step,
            'year': self.current_year,
            'quarter': self.current_quarter,
            **self.market_indicators.to_dict()
        })
        
        self.history['segment_dynamics'].append({
            'time_step': self.time_step,
            'year': self.current_year,
            'quarter': self.current_quarter,
            **self.segment_dynamics.to_dict()
        })
    
    def get_market_intelligence(self, segment_ids: List[int]) -> Dict[str, Any]:
        """
        Get market intelligence relevant for brand decision-making
        
        Args:
            segment_ids: List of segment IDs the brand operates in
            
        Returns:
            Market intelligence package
        """
        # Calculate segment-weighted metrics
        segment_weights = {}
        total_weight = 0
        for seg_id in segment_ids:
            # Weight by inverse saturation (less saturated = more important)
            weight = 1.0 - self.segment_dynamics.segment_saturation.get(seg_id, 0.5)
            segment_weights[seg_id] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            segment_weights = {k: v/total_weight for k, v in segment_weights.items()}
        
        # Calculate weighted average growth potential
        growth_potential = sum(
            self.segment_dynamics.segment_growth_rates.get(seg_id, 0) * weight
            for seg_id, weight in segment_weights.items()
        )
        
        # Identify opportunities and threats
        opportunities = []
        threats = []
        
        # Check for HP Luxury opportunity
        if 6 not in segment_ids and self.market_indicators.luxury_technical_convergence > 0.5:
            opportunities.append({
                'type': 'segment_expansion',
                'target': 'High-Performance Luxury',
                'strength': self.market_indicators.luxury_technical_convergence
            })
        
        # Check for sustainability opportunity/threat
        if self.consumer_preferences.sustainability_importance > 0.5:
            if self.market_indicators.sustainability_pressure > 0.6:
                threats.append({
                    'type': 'sustainability_compliance',
                    'urgency': self.market_indicators.sustainability_pressure
                })
            else:
                opportunities.append({
                    'type': 'sustainability_leadership',
                    'strength': self.consumer_preferences.sustainability_importance
                })
        
        # Economic threats
        if self.market_indicators.economic_confidence < 0.5:
            threats.append({
                'type': 'economic_downturn',
                'severity': 1.0 - self.market_indicators.economic_confidence
            })
        
        return {
            'consumer_preferences': self.consumer_preferences.to_dict(),
            'market_indicators': self.market_indicators.to_dict(),
            'segment_analysis': {
                'growth_rates': {seg_id: self.segment_dynamics.segment_growth_rates[seg_id] 
                               for seg_id in segment_ids},
                'saturation_levels': {seg_id: self.segment_dynamics.segment_saturation[seg_id] 
                                    for seg_id in segment_ids},
                'weighted_growth_potential': growth_potential
            },
            'opportunities': opportunities,
            'threats': threats,
            'market_timing': {
                'year': self.current_year,
                'quarter': self.current_quarter,
                'active_shocks': [s['type'] for s in self.active_shocks]
            }
        }
    
    def save_market_history(self, filepath: str) -> None:
        """Save market history to JSON file"""
        history_data = {
            'metadata': {
                'total_time_steps': self.time_step,
                'years_simulated': self.current_year,
                'shock_events': self.shock_history
            },
            'history': self.history
        }
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        logger.info(f"💾 Market history saved to {filepath}")
    
    def get_current_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current market state"""
        return {
            'time': f"Y{self.current_year}Q{self.current_quarter}",
            'consumer_preferences': self.consumer_preferences.to_dict(),
            'market_indicators': self.market_indicators.to_dict(),
            'segment_dynamics': self.segment_dynamics.to_dict(),
            'active_shocks': [{'type': s['type'], 'remaining': s['remaining_duration']} 
                            for s in self.active_shocks],
            'top_growth_segments': sorted(
                [(self.segment_names[k], v) for k, v in self.segment_dynamics.segment_growth_rates.items()],
                key=lambda x: x[1], reverse=True
            )[:3]
        }


def main():
    """Test the Market State Manager"""
    print("📊 MARKET STATE MANAGER TEST")
    print("=" * 60)
    
    # Initialize manager
    manager = MarketStateManager(initial_seed=42)
    
    # Show initial state
    print("\n🌅 Initial Market State:")
    initial_state = manager.get_current_state_summary()
    print(f"Time: {initial_state['time']}")
    print(f"Consumer Preferences: {initial_state['consumer_preferences']}")
    print(f"Top Growth Segments: {initial_state['top_growth_segments']}")
    
    # Simulate 8 quarters (2 years)
    print("\n📈 Simulating Market Evolution...")
    for quarter in range(8):
        manager.update_market_state()
        
        # Apply shock in Y1Q3
        if manager.current_year == 1 and manager.current_quarter == 3:
            manager.apply_market_shock('tech_boom', duration=4, intensity=0.7)
        
        # Apply recession in Y2Q2
        if manager.current_year == 2 and manager.current_quarter == 2:
            manager.apply_market_shock('recession', duration=3, intensity=0.5)
    
    # Show final state
    print("\n🏁 Final Market State:")
    final_state = manager.get_current_state_summary()
    print(f"Time: {final_state['time']}")
    print(f"Consumer Preferences: {final_state['consumer_preferences']}")
    print(f"Market Indicators: {final_state['market_indicators']}")
    print(f"Active Shocks: {final_state['active_shocks']}")
    
    # Test market intelligence for a luxury brand
    print("\n🔍 Market Intelligence for Luxury Brand (segments 6, 7):")
    intel = manager.get_market_intelligence([6, 7])
    print(f"Growth Potential: {intel['segment_analysis']['weighted_growth_potential']:.2%}")
    print(f"Opportunities: {len(intel['opportunities'])} identified")
    print(f"Threats: {len(intel['threats'])} identified")
    
    # Save history
    manager.save_market_history("market_history_test.json")
    print("\n✅ Market history saved")


if __name__ == "__main__":
    main() 