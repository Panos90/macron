"""
ModaMesh™ Agent Framework
========================
Multi-agent simulation system for Italian fashion market analysis.
"""

from .brand_agent import BrandAgent, load_all_brand_agents
from .macron_agent import MacronAgent, load_macron_agent
from .market_state_manager import MarketStateManager
from .simulation_orchestrator import (
    SimulationOrchestrator,
    SimulationConfig,
    MarketState
)

__all__ = [
    'BrandAgent',
    'MacronAgent',
    'MarketStateManager',
    'SimulationOrchestrator',
    'SimulationConfig',
    'MarketState',
    'load_all_brand_agents',
    'load_macron_agent'
]

__version__ = '1.0.0' 