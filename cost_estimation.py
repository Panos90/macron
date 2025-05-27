#!/usr/bin/env python3
"""
MONTE CARLO COST ANALYSIS
=========================
Comprehensive analysis for all 10 Macron products across 3 geographical scenarios
Integrates all assumptions and cost parameters developed in the analysis
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import warnings
import os
warnings.filterwarnings('ignore')

class MonteCarloCostAnalysis:
    def __init__(self, n_simulations=100000):
        self.n_simulations = n_simulations
        self.products = {}
        self.results = {}
        
        # Geographical scenarios with comprehensive cost multipliers
        self.geographical_scenarios = {
            'EU_Production': {
                'labor_cost_multiplier': 1.0,
                'material_cost_multiplier': 1.0,
                'regulatory_premium': 0.15,  # 15% premium for EU compliance
                'logistics_cost_factor': 0.02,  # 2% of total costs
                'quality_discount': 0.0,  # No quality discount
                'lead_time_weeks': 8,
                'description': 'Full EU production with highest quality standards'
            },
            'Asian_Production': {
                'labor_cost_multiplier': 0.25,  # 75% lower labor costs
                'material_cost_multiplier': 0.8,  # 20% lower material costs
                'regulatory_premium': 0.05,  # 5% premium for export compliance
                'logistics_cost_factor': 0.12,  # 12% of total costs
                'quality_discount': 0.05,  # 5% quality risk discount
                'lead_time_weeks': 16,
                'description': 'Asian production with cost optimization'
            },
            'Hybrid_Model': {
                'labor_cost_multiplier': 0.6,  # Mixed labor costs
                'material_cost_multiplier': 0.9,  # Mixed material costs
                'regulatory_premium': 0.10,  # 10% premium for mixed compliance
                'logistics_cost_factor': 0.07,  # 7% of total costs
                'quality_discount': 0.02,  # 2% quality risk discount
                'lead_time_weeks': 12,
                'description': 'Hybrid model: EU R&D + Asian manufacturing'
            }
        }
        
        # Comprehensive cost assumptions for all 10 products
        self.cost_assumptions = {
            'Hydrotex Moisture-Control Liners': {
                'category': 'Technical Inner Layers & Insulation Systems',
                'complexity': 'Very High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for research projects)
                    'membrane_rd': {
                        'base': 400000, 
                        'distribution': 'lognormal', 
                        'sigma': 0.3,  # Log-normal parameter
                        'description': 'Ultra-thin membrane R&D - high uncertainty due to breakthrough technology'
                    },
                    'moisture_testing': {
                        'base': 100000, 
                        'distribution': 'gamma', 
                        'shape': 4, 'scale': 25000,  # Gamma parameters
                        'description': 'Sweat transport testing - equipment & protocol development'
                    },
                    'regulatory_compliance': {
                        'base': 75000, 
                        'distribution': 'uniform', 
                        'low': 60000, 'high': 90000,  # Known regulatory range
                        'description': 'EU textile regulation compliance & certification'
                    }
                },
                'variable_components': {
                    # Material costs: Normal distribution (well-established supply chains)
                    'hydroflex_membrane': {
                        'base_per_sqm': 15.0,  # €15 per square meter as specified
                        'distribution': 'normal',
                        'std_dev': 2.0,  # €2 standard deviation (supplier variation)
                        'description': 'Hydroflex membrane material cost per square meter - includes material + processing'
                    },
                    # Manufacturing costs: Beta distribution (bounded process efficiency)
                    'laser_cutting': {
                        'base_per_sqcm': 0.5,  # €0.5 per square centimeter as specified  
                        'distribution': 'beta',
                        'alpha': 5, 'beta': 2,  # Skewed toward lower costs with experience
                        'scale': 0.3,  # Scale factor for beta distribution
                        'description': 'Precision laser cutting cost per square centimeter - high precision required'
                    },
                    # Quality control: Exponential distribution (defect-driven)
                    'quality_control': {
                        'base': 8.0,
                        'distribution': 'exponential',
                        'rate': 0.125,  # 1/8 = 0.125 (mean = 8)
                        'description': 'Per-unit quality testing - waterproofing & breathability validation'
                    },
                    # Assembly: Triangular distribution (best/worst/most likely scenario)
                    'assembly_labor': {
                        'min': 5.0, 'mode': 8.0, 'max': 15.0,
                        'distribution': 'triangular',
                        'description': 'Assembly labor cost - varies with worker skill & complexity'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'typical_area_sqm': 0.8,  # Typical liner covers 0.8 m² per garment
                    'cutting_complexity_sqcm': 200,  # 200 cm² of precision cutting per unit
                    'description': 'Technical specifications for cost calculations'
                }
            },
            'EcoMesh Ventilation Panels': {
                'category': 'Technical Inner Layers & Insulation Systems',
                'complexity': 'High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for research projects)
                    'laser_perforation_rd': {
                        'base': 150000,
                        'distribution': 'lognormal',
                        'sigma': 0.25,  # Log-normal parameter (lower uncertainty than breakthrough tech)
                        'description': 'Laser perforation pattern development - advanced manufacturing R&D'
                    },
                    'eco_material_certification': {
                        'base': 50000,
                        'distribution': 'uniform',
                        'low': 40000, 'high': 60000,  # Known certification cost range
                        'description': 'Eco-material certification & sustainability validation'
                    },
                    'breathability_testing': {
                        'base': 75000,
                        'distribution': 'gamma',
                        'shape': 3, 'scale': 25000,  # Gamma parameters
                        'description': 'Airflow optimization & breathability testing protocols'
                    }
                },
                'variable_components': {
                    # Laser operation: Triangular distribution (min/mode/max scenario)
                    'laser_operation': {
                        'min': 3.0, 'mode': 4.0, 'max': 5.0,  # €3-5/unit as specified
                        'distribution': 'triangular',
                        'description': 'Laser perforation operation cost per unit - precision manufacturing'
                    },
                    # EcoMesh premium: Normal distribution around 15%
                    'ecomesh_premium_factor': {
                        'base': 0.15,  # 15% premium as specified
                        'distribution': 'normal',
                        'std_dev': 0.03,  # ±3% uncertainty (12-18% range)
                        'description': 'EcoMesh premium factor - sustainable material cost multiplier'
                    },
                    # Base mesh material: Normal distribution
                    'mesh_base_material': {
                        'base': 20.0,
                        'distribution': 'normal',
                        'std_dev': 3.0,  # €3 standard deviation
                        'description': 'Base mesh material cost per unit before eco-premium'
                    },
                    # Assembly: Triangular distribution
                    'assembly_labor': {
                        'min': 6.0, 'mode': 10.0, 'max': 16.0,
                        'distribution': 'triangular',
                        'description': 'Panel assembly & integration labor cost'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'perforation_complexity': 'high',  # Affects laser operation time
                    'eco_certification_required': True,
                    'description': 'Technical specifications for EcoMesh panels'
                }
            },
            'HD Bonded Insulation Pads': {
                'category': 'Technical Inner Layers & Insulation Systems',
                'complexity': 'High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for research projects)
                    'thermal_mapping_rd': {
                        'base': 100000,
                        'distribution': 'lognormal',
                        'sigma': 0.28,  # Log-normal parameter (moderate uncertainty for thermal mapping)
                        'description': 'Thermal zone mapping R&D - body heat distribution analysis & optimization'
                    },
                    'bonding_process_development': {
                        'base': 85000,
                        'distribution': 'lognormal',
                        'sigma': 0.32,  # Higher uncertainty for new bonding technology
                        'description': 'HD bonding process development - advanced adhesion technology R&D'
                    },
                    'weight_optimization_testing': {
                        'base': 45000,
                        'distribution': 'gamma',
                        'shape': 2.5, 'scale': 18000,  # Gamma parameters for testing protocols
                        'description': '85g/m² target achievement - weight optimization testing & validation'
                    }
                },
                'variable_components': {
                    # PU foam material: Normal distribution (established material supply)
                    'pu_foam_material': {
                        'base_per_kg': 8.0,  # €8 per kg as specified
                        'distribution': 'normal',
                        'std_dev': 1.2,  # €1.2 standard deviation (supplier & quality variation)
                        'description': 'Polyurethane foam material cost per kilogram - lightweight insulation'
                    },
                    # Precision laser cutting: Beta distribution with waste factor
                    'precision_laser_cutting': {
                        'base_cost_per_unit': 12.0,  # Base cutting cost before waste
                        'distribution': 'beta',
                        'alpha': 3, 'beta': 2,  # Beta parameters (cutting efficiency)
                        'scale': 4.0,  # Scale factor for beta distribution
                        'waste_factor': 0.20,  # 20% waste as specified
                        'description': 'Precision laser cutting with 20% material waste - complex pattern cutting'
                    },
                    # Bonding process: Triangular distribution (process variability)
                    'hd_bonding_process': {
                        'min': 8.0, 'mode': 12.0, 'max': 18.0,
                        'distribution': 'triangular',
                        'description': 'HD bonding process cost per unit - advanced adhesion application'
                    },
                    # Quality testing: Exponential distribution (defect-based)
                    'thermal_validation': {
                        'base': 6.0,
                        'distribution': 'exponential',
                        'rate': 0.167,  # 1/6 = 0.167 (mean = 6)
                        'description': 'Per-unit thermal validation - insulation performance testing'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'foam_weight_per_unit_kg': 0.15,  # 150g of PU foam per insulation pad
                    'target_weight_per_sqm': 85,  # 85g/m² target as mentioned
                    'bonding_complexity': 'high',  # Affects bonding process time
                    'description': 'Technical specifications for HD bonded insulation pads'
                }
            },
            'Phase Change Material (PCM) Inserts': {
                'category': 'Technical Inner Layers & Insulation Systems',
                'complexity': 'Very High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for advanced research projects)
                    'pcm_formulation_rd': {
                        'base': 200000,
                        'distribution': 'lognormal',
                        'sigma': 0.35,  # Higher uncertainty for breakthrough PCM technology
                        'description': 'PCM formulation R&D - phase change material development for 31°C regulation'
                    },
                    'thermal_imaging_systems': {
                        'base': 300000,
                        'distribution': 'lognormal',
                        'sigma': 0.28,  # Moderate uncertainty for thermal imaging equipment
                        'description': 'Thermal imaging systems R&D - microclimate mapping & validation technology'
                    },
                    'microclimate_testing': {
                        'base': 150000,
                        'distribution': 'gamma',
                        'shape': 3, 'scale': 50000,  # Gamma parameters for testing protocols
                        'description': 'Body temperature regulation testing - 31°C maintenance validation protocols'
                    },
                    'encapsulation_durability': {
                        'base': 100000,
                        'distribution': 'uniform',
                        'low': 80000, 'high': 120000,  # Known testing range for durability
                        'description': 'PCM encapsulation durability testing - wash cycle & wear resistance validation'
                    }
                },
                'variable_components': {
                    # PCM pellets: Triangular distribution (€15-25/kg range specified)
                    'pcm_pellets': {
                        'min': 15.0, 'mode': 18.0, 'max': 25.0,  # €15-25/kg as specified
                        'distribution': 'triangular',
                        'description': 'Phase change material pellets per kilogram - specialized temperature-regulating material'
                    },
                    # Micro-encapsulation: Beta distribution (complex manufacturing process)
                    'micro_encapsulation_process': {
                        'base_cost_per_unit': 12.0,  # Base encapsulation cost
                        'distribution': 'beta',
                        'alpha': 4, 'beta': 3,  # Beta parameters for process efficiency
                        'scale': 6.0,  # Scale factor for beta distribution (€6-18/unit range)
                        'description': 'Micro-encapsulation manufacturing process - PCM pellet encapsulation per unit'
                    },
                    # Thermal validation: Exponential distribution (performance-driven)
                    'thermal_performance_testing': {
                        'base': 10.0,
                        'distribution': 'exponential',
                        'rate': 0.1,  # 1/10 = 0.1 (mean = 10)
                        'description': 'Per-unit thermal performance validation - 31°C regulation testing'
                    },
                    # Integration assembly: Triangular distribution (assembly complexity)
                    'pcm_integration_assembly': {
                        'min': 8.0, 'mode': 12.0, 'max': 20.0,
                        'distribution': 'triangular',
                        'description': 'PCM insert integration & assembly into garment systems'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'pcm_weight_per_unit_kg': 0.25,  # 250g of PCM pellets per insert
                    'target_temperature_celsius': 31,  # Target regulation temperature
                    'encapsulation_efficiency': 0.92,  # 92% encapsulation success rate
                    'thermal_zones_per_garment': 3,  # Typical number of thermal zones
                    'description': 'Technical specifications for PCM inserts - body temperature regulation'
                }
            },
            'Performance Jacquard Reinforcement': {
                'category': 'Structural Enhancement Solutions',
                'complexity': 'High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for advanced textile research)
                    'jacquard_pattern_rd': {
                        'base': 250000,
                        'distribution': 'lognormal',
                        'sigma': 0.30,  # Moderate uncertainty for jacquard pattern development
                        'description': 'Jacquard pattern R&D - complex weave architecture & performance optimization'
                    },
                    'four_way_stretch_rd': {
                        'base': 200000,
                        'distribution': 'lognormal',
                        'sigma': 0.32,  # Higher uncertainty for breakthrough stretch technology
                        'description': '4-way stretch R&D - multi-directional elasticity engineering & validation'
                    },
                    'weight_reduction_rd': {
                        'base': 150000,
                        'distribution': 'gamma',
                        'shape': 3, 'scale': 50000,  # Gamma parameters for weight optimization
                        'description': '23% weight reduction R&D - material density optimization without strength loss'
                    },
                    'stretch_performance_testing': {
                        'base': 120000,
                        'distribution': 'uniform',
                        'low': 100000, 'high': 140000,  # Known testing range for stretch validation
                        'description': '4-way stretch performance testing - multi-axis stress & recovery validation'
                    }
                },
                'variable_components': {
                    # Jacquard fabric base: Normal distribution (established weaving technology)
                    'jacquard_fabric_base': {
                        'base_per_sqm': 45.0,  # €45 per square meter base fabric
                        'distribution': 'normal',
                        'std_dev': 6.0,  # €6 standard deviation (supplier & quality variation)
                        'description': 'Performance jacquard fabric base cost per square meter - complex weave structure'
                    },
                    # Elastane content: Triangular distribution (25% elastane content specified)
                    'elastane_premium': {
                        'elastane_percentage': 0.25,  # 25% elastane content as specified
                        'base_premium_per_sqm': 35.0,  # €35/m² premium for 25% elastane
                        'distribution': 'triangular',
                        'min': 30.0, 'mode': 35.0, 'max': 42.0,  # €30-42/m² range for elastane premium
                        'description': '25% elastane content premium - high-performance stretch material integration'
                    },
                    # 4-way stretch processing: Beta distribution (complex manufacturing process)
                    'four_way_stretch_processing': {
                        'base_cost_per_sqm': 18.0,  # Base processing cost per square meter
                        'distribution': 'beta',
                        'alpha': 4, 'beta': 2,  # Beta parameters for process efficiency (skewed toward lower costs)
                        'scale': 8.0,  # Scale factor for beta distribution (€10-26/m² range)
                        'description': '4-way stretch processing - multi-directional elasticity treatment per square meter'
                    },
                    # Quality validation: Exponential distribution (performance-driven)
                    'stretch_quality_validation': {
                        'base': 12.0,
                        'distribution': 'exponential',
                        'rate': 0.083,  # 1/12 = 0.083 (mean = 12)
                        'description': 'Per-unit 4-way stretch quality validation - elasticity & recovery testing'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'fabric_area_per_unit_sqm': 1.2,  # 1.2 m² of jacquard fabric per reinforcement unit
                    'elastane_content_percentage': 25,  # 25% elastane content as specified
                    'stretch_directions': 4,  # 4-way stretch capability
                    'weight_reduction_target': 0.23,  # 23% weight reduction target
                    'stretch_recovery_percentage': 95,  # 95% stretch recovery requirement
                    'description': 'Technical specifications for Performance Jacquard Reinforcement'
                }
            },
            'Abrasion-Resistant Bonding': {
                'category': 'Structural Enhancement Solutions',
                'complexity': 'High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for durability research)
                    'astm_d4966_testing_rigs': {
                        'base': 100000,
                        'distribution': 'lognormal',
                        'sigma': 0.25,  # Moderate uncertainty for standardized testing equipment
                        'description': 'ASTM D4966 testing rigs - abrasion resistance validation equipment & protocols'
                    },
                    'polymer_testing_rd': {
                        'base': 80000,
                        'distribution': 'lognormal',
                        'sigma': 0.30,  # Higher uncertainty for polymer R&D
                        'description': 'Polymer testing R&D - high-density material durability & bonding chemistry'
                    },
                    'abrasion_cycle_validation': {
                        'base': 120000,
                        'distribution': 'gamma',
                        'shape': 4, 'scale': 30000,  # Gamma parameters for cycle testing
                        'description': '50,000+ abrasion cycle validation - long-term durability testing protocols'
                    },
                    'bonding_strength_optimization': {
                        'base': 90000,
                        'distribution': 'uniform',
                        'low': 75000, 'high': 105000,  # Known optimization range
                        'description': 'Bonding strength optimization - adhesion performance under stress testing'
                    }
                },
                'variable_components': {
                    # High-density polyamide: Triangular distribution (€10-15/m² range specified)
                    'high_density_polyamide': {
                        'min': 10.0, 'mode': 12.0, 'max': 15.0,  # €10-15/m² as specified
                        'distribution': 'triangular',
                        'description': 'High-density polyamide material per square meter - abrasion-resistant substrate'
                    },
                    # Bonding process: Beta distribution (complex manufacturing process)
                    'abrasion_bonding_process': {
                        'base_cost_per_sqm': 14.0,  # Base bonding cost per square meter
                        'distribution': 'beta',
                        'alpha': 3, 'beta': 2,  # Beta parameters for process efficiency
                        'scale': 6.0,  # Scale factor for beta distribution (€8-20/m² range)
                        'description': 'Abrasion-resistant bonding process - specialized adhesion per square meter'
                    },
                    # Cycle testing validation: Exponential distribution (durability-driven)
                    'abrasion_cycle_testing': {
                        'base': 15.0,
                        'distribution': 'exponential',
                        'rate': 0.067,  # 1/15 = 0.067 (mean = 15)
                        'description': 'Per-unit abrasion cycle testing - 50,000+ cycle durability validation'
                    },
                    # Quality assurance: Triangular distribution (QA complexity)
                    'durability_qa_inspection': {
                        'min': 6.0, 'mode': 9.0, 'max': 14.0,
                        'distribution': 'triangular',
                        'description': 'Durability QA inspection - per-unit bonding strength & abrasion validation'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'bonding_area_per_unit_sqm': 0.8,  # 0.8 m² of bonding area per unit
                    'abrasion_cycles_target': 50000,  # 50,000+ cycles as mentioned
                    'polyamide_density_gsm': 180,  # 180 g/m² high-density specification
                    'bonding_strength_target_n': 25,  # 25N minimum bonding strength
                    'wear_resistance_grade': 'commercial_heavy_duty',  # Commercial heavy-duty grade
                    'description': 'Technical specifications for Abrasion-Resistant Bonding'
                }
            },
            'MacronLock Magnetic Closures': {
                'category': 'Structural Enhancement Solutions',
                'complexity': 'Medium',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for precision engineering research)
                    'magnetic_strength_testing_8n': {
                        'base': 135000,
                        'distribution': 'lognormal',
                        'sigma': 0.28,  # Moderate uncertainty for specialized magnetic testing equipment
                        'description': '8N strength testing R&D - magnetic hold force validation equipment & protocols'
                    },
                    'concealed_mechanism_design': {
                        'base': 200000,
                        'distribution': 'lognormal',
                        'sigma': 0.35,  # Higher uncertainty for innovative concealment design R&D
                        'description': 'Concealed mechanism design R&D - seamless integration & aesthetic engineering'
                    },
                    'magnetic_field_optimization': {
                        'base': 90000,
                        'distribution': 'gamma',
                        'shape': 3, 'scale': 30000,  # Gamma parameters for magnetic field engineering
                        'description': 'Magnetic field optimization - neodymium magnet configuration & efficiency testing'
                    },
                    'durability_cycle_testing': {
                        'base': 75000,
                        'distribution': 'uniform',
                        'low': 60000, 'high': 90000,  # Known testing range for closure durability
                        'description': 'Magnetic closure durability testing - repeated opening/closing cycle validation'
                    }
                },
                'variable_components': {
                    # Neodymium magnets: Triangular distribution (€2-3/unit range specified)
                    'neodymium_magnets': {
                        'min': 2.0, 'mode': 2.4, 'max': 3.0,  # €2-3/unit as specified
                        'distribution': 'triangular',
                        'description': 'Neodymium magnets per unit - rare earth magnetic elements for 8N hold strength'
                    },
                    # CNC machining: Beta distribution with waste factor (precision manufacturing)
                    'cnc_machining_housing': {
                        'base_cost_per_unit': 10.0,  # Base CNC machining cost per unit
                        'distribution': 'beta',
                        'alpha': 4, 'beta': 2,  # Beta parameters for machining efficiency
                        'scale': 3.0,  # Scale factor for beta distribution (€7-13/unit range)
                        'waste_factor': 0.18,  # 18% material waste for precision CNC operations
                        'description': 'CNC machining housing with 18% material waste - precision closure mechanism'
                    },
                    # Assembly & calibration: Triangular distribution (skilled assembly required)
                    'magnetic_assembly_calibration': {
                        'min': 4.0, 'mode': 6.0, 'max': 9.0,
                        'distribution': 'triangular',
                        'description': 'Magnetic assembly & field calibration - precision alignment for 8N strength'
                    },
                    # Quality validation: Exponential distribution (strength-driven testing)
                    'magnetic_strength_validation': {
                        'base': 5.0,
                        'distribution': 'exponential',
                        'rate': 0.2,  # 1/5 = 0.2 (mean = 5)
                        'description': 'Per-unit magnetic strength validation - 8N hold force verification'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'magnetic_hold_strength_n': 8,  # 8N hold strength requirement
                    'concealment_level': 'seamless',  # Seamless visual integration
                    'magnet_pairs_per_unit': 2,  # Typical magnetic closure uses 2 magnet pairs
                    'cnc_tolerance_microns': 50,  # 50-micron machining tolerance for precision fit
                    'housing_material': 'aluminum_alloy',  # Lightweight, non-magnetic housing material
                    'durability_cycles_target': 10000,  # 10,000 opening/closing cycles
                    'description': 'Technical specifications for MacronLock Magnetic Closures'
                }
            },
            'Auto-Tension Drawstrings': {
                'category': 'Structural Enhancement Solutions',
                'complexity': 'Medium',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for mechanical engineering research)
                    'silicone_grip_rd': {
                        'base': 110000,
                        'distribution': 'lognormal',
                        'sigma': 0.32,  # Higher uncertainty for specialized silicone material engineering
                        'description': 'Silicone grip R&D - non-slip surface technology & adhesion optimization'
                    },
                    'tension_control_mechanisms_rd': {
                        'base': 165000,
                        'distribution': 'lognormal',
                        'sigma': 0.28,  # Moderate uncertainty for mechanical precision engineering
                        'description': 'Tension control mechanisms R&D - auto-adjustment engineering & spring calibration'
                    },
                    'precision_adjustment_testing': {
                        'base': 75000,
                        'distribution': 'gamma',
                        'shape': 3, 'scale': 25000,  # Gamma parameters for precision testing protocols
                        'description': 'Precision adjustment testing - tension calibration & consistency validation'
                    },
                    'durability_stress_testing': {
                        'base': 65000,
                        'distribution': 'uniform',
                        'low': 50000, 'high': 80000,  # Known testing range for mechanical durability
                        'description': 'Durability stress testing - repeated tension cycles & material fatigue validation'
                    }
                },
                'variable_components': {
                    # Adaptive spring system: Triangular distribution (€3-5/unit range specified)
                    'adaptive_spring_system': {
                        'min': 3.0, 'mode': 3.8, 'max': 5.0,  # €3-5/unit as specified
                        'distribution': 'triangular',
                        'description': 'Adaptive spring system per unit - precision tension regulation mechanism'
                    },
                    # High-performance drawstring: Normal distribution (premium cord material)
                    'high_performance_drawstring': {
                        'base_per_meter': 18.0,  # €18 per meter for high-performance cord
                        'distribution': 'normal',
                        'std_dev': 2.5,  # €2.5 standard deviation (supplier & quality variation)
                        'description': 'High-performance drawstring material per meter - strength & elasticity optimized'
                    },
                    # Silicone grip application: Beta distribution (process efficiency)
                    'silicone_grip_application': {
                        'base_cost_per_unit': 9.0,  # Base silicone application cost per unit
                        'distribution': 'beta',
                        'alpha': 3, 'beta': 2,  # Beta parameters for application efficiency
                        'scale': 4.0,  # Scale factor for beta distribution (€5-13/unit range)
                        'description': 'Silicone grip application process - non-slip surface coating per unit'
                    },
                    # Mechanism assembly: Triangular distribution (skilled assembly required)
                    'tension_mechanism_assembly': {
                        'min': 6.0, 'mode': 9.0, 'max': 14.0,
                        'distribution': 'triangular',
                        'description': 'Tension mechanism assembly - spring integration & calibration per unit'
                    },
                    # Quality validation: Exponential distribution (tension-performance driven)
                    'tension_performance_validation': {
                        'base': 7.0,
                        'distribution': 'exponential',
                        'rate': 0.143,  # 1/7 = 0.143 (mean = 7)
                        'description': 'Per-unit tension performance validation - auto-adjustment & consistency testing'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'drawstring_length_per_unit_m': 1.5,  # 1.5 meters of drawstring per unit
                    'tension_range_n': [2, 12],  # 2-12N tension adjustment range
                    'adjustment_precision_percent': 5,  # ±5% tension precision
                    'spring_cycles_target': 25000,  # 25,000 tension adjustment cycles
                    'silicone_grip_area_sqcm': 15,  # 15 cm² of silicone grip surface
                    'temperature_range_celsius': [-20, 60],  # Operating temperature range
                    'description': 'Technical specifications for Auto-Tension Drawstrings'
                }
            },
            '100% Recycled Performance Jacquard': {
                'category': 'Sustainable Performance Materials',
                'complexity': 'Very High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for breakthrough sustainability research)
                    'pet_recycling_process_rd': {
                        'base': 400000,  # €400k as specified
                        'distribution': 'lognormal',
                        'sigma': 0.35,  # Higher uncertainty for innovative recycling technology
                        'description': 'PET recycling process R&D - bottle-to-fiber conversion technology & quality optimization'
                    },
                    'co2_certification': {
                        'base': 135000,  # CO₂ lifecycle assessment and certification
                        'distribution': 'lognormal',
                        'sigma': 0.30,  # Moderate uncertainty for environmental certification processes
                        'description': 'CO₂ certification & lifecycle assessment - 37% carbon reduction validation'
                    },
                    'fiber_quality_optimization_rd': {
                        'base': 200000,
                        'distribution': 'gamma',
                        'shape': 4, 'scale': 50000,  # Gamma parameters for quality optimization research
                        'description': 'Recycled fiber quality optimization - performance matching virgin material standards'
                    },
                    'circular_economy_compliance': {
                        'base': 85000,
                        'distribution': 'uniform',
                        'low': 70000, 'high': 100000,  # Known compliance range for circular economy standards
                        'description': 'Circular economy compliance & sustainability certification protocols'
                    }
                },
                'variable_components': {
                    # PET bottle processing: Triangular distribution (complex multi-stage process)
                    'pet_bottle_processing_12_bottles_per_sqm': {
                        'bottles_per_sqm': 12,  # 12 PET bottles per square meter as specified
                        'min_cost_per_sqm': 8.0, 'mode_cost_per_sqm': 12.0, 'max_cost_per_sqm': 18.0,  # €8-18/m² processing
                        'distribution': 'triangular',
                        'description': '12 PET bottles/m² processing - collection, cleaning, shredding, melting & spinning'
                    },
                    # Recycled fiber spinning: Beta distribution (process efficiency affects quality)
                    'recycled_fiber_spinning': {
                        'base_cost_per_sqm': 25.0,  # Base spinning cost per square meter
                        'distribution': 'beta',
                        'alpha': 3, 'beta': 2,  # Beta parameters for spinning efficiency
                        'scale': 10.0,  # Scale factor for beta distribution (€15-35/m² range)
                        'description': 'Recycled fiber spinning process - PET flakes to performance fibers per square meter'
                    },
                    # Jacquard weaving: Normal distribution (established weaving technology adapted for recycled fibers)
                    'recycled_jacquard_weaving': {
                        'base_per_sqm': 35.0,  # €35 per square meter for recycled jacquard weaving
                        'distribution': 'normal',
                        'std_dev': 5.0,  # €5 standard deviation (process variation with recycled fibers)
                        'description': 'Recycled jacquard weaving per square meter - complex pattern weaving with recycled fibers'
                    },
                    # Carbon footprint validation: Exponential distribution (environmental testing)
                    'carbon_footprint_validation': {
                        'base': 15.0,
                        'distribution': 'exponential',
                        'rate': 0.067,  # 1/15 = 0.067 (mean = 15)
                        'description': 'Per-unit carbon footprint validation - 37% reduction verification testing'
                    },
                    # Quality control for recycled performance: Triangular distribution (enhanced QC required)
                    'recycled_performance_qa': {
                        'min': 10.0, 'mode': 16.0, 'max': 25.0,
                        'distribution': 'triangular',
                        'description': 'Recycled performance QA - ensuring recycled fabric meets virgin material standards'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'pet_bottles_per_sqm': 12,  # 12 PET bottles per square meter as specified
                    'fabric_area_per_unit_sqm': 1.0,  # 1.0 m² of fabric per unit
                    'carbon_reduction_percentage': 37,  # 37% carbon reduction target
                    'bottle_weight_avg_grams': 50,  # Average PET bottle weight: 50g
                    'recycled_content_percentage': 100,  # 100% recycled content
                    'performance_match_target': 95,  # 95% performance match to virgin material
                    'circular_economy_grade': 'A+',  # Highest circular economy rating
                    'description': 'Technical specifications for 100% Recycled Performance Jacquard'
                }
            },
            'Bio-Based Water Repellents': {
                'category': 'Sustainable Performance Materials',
                'complexity': 'Very High',
                'fixed_components': {
                    # R&D costs follow log-normal distribution (typical for breakthrough environmental chemistry research)
                    'c6_free_chemistry_development': {
                        'base': 400000,  # €400k as specified - C6-free chemistry development
                        'distribution': 'lognormal',
                        'sigma': 0.40,  # High uncertainty for breakthrough environmental chemistry technology
                        'description': 'C6-free chemistry development R&D - PFAS-free DWR breakthrough technology'
                    },
                    'hydrostatic_testing_equipment': {
                        'base': 200000,  # €200k estimated for specialized 20,000mm pressure testing
                        'distribution': 'lognormal',
                        'sigma': 0.35,  # Moderate uncertainty for specialized testing equipment
                        'description': 'Hydrostatic testing equipment & protocols - 20,000mm pressure validation systems'
                    },
                    'bio_polymer_formulation_rd': {
                        'base': 180000,
                        'distribution': 'gamma',
                        'shape': 3, 'scale': 60000,  # Gamma parameters for bio-polymer R&D
                        'description': 'Bio-polymer formulation R&D - plant-based water repellent chemistry development'
                    },
                    'environmental_compliance_certification': {
                        'base': 120000,
                        'distribution': 'uniform',
                        'low': 100000, 'high': 140000,  # Known environmental certification range
                        'description': 'Environmental compliance & certification - PFAS-free validation & eco-standards'
                    }
                },
                'variable_components': {
                    # Bio-based polymers: Triangular distribution with 20% premium specified
                    'bio_based_polymers_20_percent_premium': {
                        'conventional_base_cost_per_sqm': 45.0,  # Base conventional polymer cost per m²
                        'premium_percentage': 0.20,  # 20% premium as specified
                        'distribution': 'triangular',
                        'min_premium': 0.15, 'mode_premium': 0.20, 'max_premium': 0.28,  # 15-28% premium range
                        'description': '20% bio-polymer premium - plant-based water repellent polymers per square meter'
                    },
                    # DWR application process: Beta distribution (process efficiency)
                    'dwr_application_process': {
                        'base_cost_per_sqm': 22.0,  # Base application cost per square meter
                        'distribution': 'beta',
                        'alpha': 4, 'beta': 2,  # Beta parameters for application efficiency
                        'scale': 8.0,  # Scale factor for beta distribution (€14-30/m² range)
                        'description': 'Bio-DWR application process - specialized coating application per square meter'
                    },
                    # Hydrostatic pressure validation: Exponential distribution (performance-driven)
                    'hydrostatic_pressure_validation_20000mm': {
                        'base': 25.0,
                        'distribution': 'exponential',
                        'rate': 0.04,  # 1/25 = 0.04 (mean = 25)
                        'description': 'Per-unit 20,000mm hydrostatic pressure validation - waterproofing performance testing'
                    },
                    # Environmental validation: Triangular distribution (certification complexity)
                    'environmental_impact_validation': {
                        'min': 12.0, 'mode': 18.0, 'max': 28.0,
                        'distribution': 'triangular',
                        'description': 'Environmental impact validation - PFAS-free & biodegradability certification per unit'
                    },
                    # Quality assurance: Normal distribution (established QA for DWR coatings)
                    'bio_dwr_quality_assurance': {
                        'base': 15.0,
                        'distribution': 'normal',
                        'std_dev': 3.0,  # €3 standard deviation
                        'description': 'Bio-DWR quality assurance - performance consistency & durability validation'
                    }
                },
                # Technical specifications for cost calculation
                'technical_specs': {
                    'target_pressure_resistance_mm': 20000,  # 20,000mm hydrostatic pressure target
                    'fabric_area_per_unit_sqm': 0.9,  # 0.9 m² of treated fabric per unit
                    'bio_polymer_content_percentage': 85,  # 85% bio-based polymer content
                    'conventional_polymer_replacement': 100,  # 100% replacement of conventional polymers
                    'environmental_certification_grade': 'PFAS_free_A+',  # Highest environmental grade
                    'durability_wash_cycles': 50,  # 50 wash cycles maintaining 20,000mm performance
                    'biodegradability_percentage': 75,  # 75% biodegradable within 2 years
                    'description': 'Technical specifications for Bio-Based Water Repellents - C6-free DWR performance'
                }
            }
        }
    
    def load_products(self):
        """Load product definitions from JSON file"""
        try:
            with open('macron_products.json', 'r') as f:
                product_data = json.load(f)
            
            # Extract all 10 products
            products = []
            for category, subcategories in product_data.items():
                for subcategory, items in subcategories.items():
                    for item in items:
                        products.append(item['name'])
            
            print(f"✅ Loaded {len(products)} products from JSON:")
            for i, product in enumerate(products, 1):
                print(f"   {i}. {product}")
            
            return products
        except FileNotFoundError:
            print("❌ macron_products.json not found. Using predefined product list.")
            return list(self.cost_assumptions.keys())
    
    def calculate_costs(self, product_name, scenario_name, scenario_params):
        """Calculate costs for a product under a specific geographical scenario"""
        if product_name not in self.cost_assumptions:
            print(f"⚠️  Warning: No cost assumptions for {product_name}")
            return {'fixed_costs': np.zeros(self.n_simulations), 
                   'variable_costs': np.zeros(self.n_simulations)}
        
        assumptions = self.cost_assumptions[product_name]
        
        # Calculate fixed costs (R&D) using different distributions
        fixed_costs = np.zeros(self.n_simulations)
        for component, params in assumptions['fixed_components'].items():
            
            if 'distribution' in params:
                # Use specified distribution
                dist_type = params['distribution']
                
                if dist_type == 'lognormal':
                    # Log-normal distribution for R&D projects (right-skewed, no negative values)
                    mu = np.log(params['base'])
                    sigma = params['sigma']
                    component_costs = np.random.lognormal(mu, sigma, self.n_simulations)
                    
                elif dist_type == 'gamma':
                    # Gamma distribution for testing costs (positive, flexible shape)
                    shape = params['shape']
                    scale = params['scale']
                    component_costs = np.random.gamma(shape, scale, self.n_simulations)
                    
                elif dist_type == 'uniform':
                    # Uniform distribution for known regulatory ranges
                    low = params['low']
                    high = params['high']
                    component_costs = np.random.uniform(low, high, self.n_simulations)
                    
                else:
                    # Fallback to normal distribution
                    base_cost = params['base']
                    uncertainty = params.get('uncertainty', 0.2)
                    component_costs = np.random.normal(base_cost, base_cost * uncertainty, self.n_simulations)
                    component_costs = np.maximum(component_costs, base_cost * 0.3)
            else:
                # Legacy format - normal distribution
                base_cost = params['base']
                uncertainty = params['uncertainty']
                component_costs = np.random.normal(base_cost, base_cost * uncertainty, self.n_simulations)
                component_costs = np.maximum(component_costs, base_cost * 0.3)
            
            fixed_costs += component_costs
        
        # Calculate variable costs (per unit) using different distributions
        variable_costs = np.zeros(self.n_simulations)
        
        # Handle new detailed cost structure for Moisture-Control Liners
        if product_name == 'Hydrotex Moisture-Control Liners':
            tech_specs = assumptions.get('technical_specs', {})
            area_sqm = tech_specs.get('typical_area_sqm', 0.8)
            cutting_sqcm = tech_specs.get('cutting_complexity_sqcm', 200)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'hydroflex_membrane':
                    # Normal distribution for material costs (€15/m² base)
                    base_per_sqm = params['base_per_sqm']
                    std_dev = params['std_dev']
                    cost_per_sqm = np.random.normal(base_per_sqm, std_dev, self.n_simulations)
                    cost_per_sqm = np.maximum(cost_per_sqm, base_per_sqm * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers
                    cost_per_sqm *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for typical area
                    component_costs = cost_per_sqm * area_sqm
                    
                elif component == 'laser_cutting':
                    # Beta distribution for manufacturing efficiency (€0.5/cm² base)
                    base_per_sqcm = params['base_per_sqcm']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution scaled and shifted
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    cost_per_sqcm = base_per_sqcm + (beta_values - 0.5) * scale
                    cost_per_sqcm = np.maximum(cost_per_sqcm, base_per_sqcm * 0.3)
                    
                    # Apply geographical multipliers
                    cost_per_sqcm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total cost for cutting complexity
                    component_costs = cost_per_sqcm * cutting_sqcm
                    
                elif component == 'quality_control':
                    # Exponential distribution for quality control (defect-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'assembly_labor':
                    # Triangular distribution for assembly costs
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for EcoMesh Ventilation Panels
        elif product_name == 'EcoMesh Ventilation Panels':
            base_variable_costs = np.zeros(self.n_simulations)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'laser_operation':
                    # Triangular distribution for laser operation (€3-5/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (manufacturing cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    base_variable_costs += component_costs
                    
                elif component == 'mesh_base_material':
                    # Normal distribution for base mesh material (€20 base)
                    base_cost = params['base']
                    std_dev = params['std_dev']
                    component_costs = np.random.normal(base_cost, std_dev, self.n_simulations)
                    component_costs = np.maximum(component_costs, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers (material cost)
                    component_costs *= scenario_params['material_cost_multiplier']
                    base_variable_costs += component_costs
                    
                elif component == 'assembly_labor':
                    # Triangular distribution for assembly costs (€6-16/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    base_variable_costs += component_costs
                
                elif component == 'ecomesh_premium_factor':
                    # Normal distribution for EcoMesh premium (15% ± 3%)
                    premium_factor = params['base']
                    std_dev = params['std_dev']
                    premium_factors = np.random.normal(premium_factor, std_dev, self.n_simulations)
                    premium_factors = np.maximum(premium_factors, 0.05)  # Minimum 5% premium
                    premium_factors = np.minimum(premium_factors, 0.25)  # Maximum 25% premium
                    
                    # Apply EcoMesh premium to base variable costs
                    eco_premium_costs = base_variable_costs * premium_factors
                    variable_costs += eco_premium_costs
            
            # Add base variable costs
            variable_costs += base_variable_costs
        
        # Handle new detailed cost structure for HD Bonded Insulation Pads
        elif product_name == 'HD Bonded Insulation Pads':
            tech_specs = assumptions.get('technical_specs', {})
            foam_weight_kg = tech_specs.get('foam_weight_per_unit_kg', 0.15)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'pu_foam_material':
                    # Normal distribution for PU foam material (€8/kg)
                    base_per_kg = params['base_per_kg']
                    std_dev = params['std_dev']
                    cost_per_kg = np.random.normal(base_per_kg, std_dev, self.n_simulations)
                    cost_per_kg = np.maximum(cost_per_kg, base_per_kg * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers (material cost)
                    cost_per_kg *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for foam weight per unit
                    component_costs = cost_per_kg * foam_weight_kg
                    
                elif component == 'precision_laser_cutting':
                    # Beta distribution for cutting efficiency with 20% waste factor
                    base_cost = params['base_cost_per_unit']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    waste_factor = params['waste_factor']
                    
                    # Beta distribution for cutting efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    cutting_costs = base_cost + (beta_values - 0.5) * scale
                    cutting_costs = np.maximum(cutting_costs, base_cost * 0.4)  # Floor at 40%
                    
                    # Apply 20% waste factor
                    cutting_costs *= (1 + waste_factor)
                    
                    # Apply geographical multipliers (manufacturing cost)
                    cutting_costs *= scenario_params['labor_cost_multiplier']
                    component_costs = cutting_costs
                    
                elif component == 'hd_bonding_process':
                    # Triangular distribution for HD bonding process (€8-18/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (manufacturing cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'thermal_validation':
                    # Exponential distribution for thermal validation (defect-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (testing cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for Phase Change Material (PCM) Inserts
        elif product_name == 'Phase Change Material (PCM) Inserts':
            tech_specs = assumptions.get('technical_specs', {})
            pcm_weight_kg = tech_specs.get('pcm_weight_per_unit_kg', 0.25)
            encapsulation_efficiency = tech_specs.get('encapsulation_efficiency', 0.92)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'pcm_pellets':
                    # Triangular distribution for PCM pellets (€15-25/kg)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    cost_per_kg = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (material cost)
                    cost_per_kg *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for PCM weight per unit
                    component_costs = cost_per_kg * pcm_weight_kg
                    
                elif component == 'micro_encapsulation_process':
                    # Beta distribution for micro-encapsulation process (€6-18/unit range)
                    base_cost = params['base_cost_per_unit']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution for encapsulation efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    encapsulation_costs = base_cost + (beta_values - 0.5) * scale
                    encapsulation_costs = np.maximum(encapsulation_costs, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply encapsulation efficiency factor
                    encapsulation_costs *= (1 / encapsulation_efficiency)  # Higher cost for lower efficiency
                    
                    # Apply geographical multipliers (manufacturing cost)
                    encapsulation_costs *= scenario_params['labor_cost_multiplier']
                    component_costs = encapsulation_costs
                    
                elif component == 'thermal_performance_testing':
                    # Exponential distribution for thermal performance testing (performance-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (testing cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'pcm_integration_assembly':
                    # Triangular distribution for PCM integration assembly (€8-20/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (assembly cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for Performance Jacquard Reinforcement
        elif product_name == 'Performance Jacquard Reinforcement':
            tech_specs = assumptions.get('technical_specs', {})
            fabric_area_sqm = tech_specs.get('fabric_area_per_unit_sqm', 1.2)
            elastane_percentage = tech_specs.get('elastane_content_percentage', 25)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'jacquard_fabric_base':
                    # Normal distribution for jacquard fabric base (€45/m²)
                    base_per_sqm = params['base_per_sqm']
                    std_dev = params['std_dev']
                    cost_per_sqm = np.random.normal(base_per_sqm, std_dev, self.n_simulations)
                    cost_per_sqm = np.maximum(cost_per_sqm, base_per_sqm * 0.6)  # Floor at 60%
                    
                    # Apply geographical multipliers (material cost)
                    cost_per_sqm *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for fabric area per unit
                    component_costs = cost_per_sqm * fabric_area_sqm
                    
                elif component == 'elastane_premium':
                    # Triangular distribution for elastane premium (€30-42/m² for 25% content)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    premium_per_sqm = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (material cost)
                    premium_per_sqm *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total elastane premium for fabric area
                    component_costs = premium_per_sqm * fabric_area_sqm
                    
                elif component == 'four_way_stretch_processing':
                    # Beta distribution for 4-way stretch processing (€10-26/m² range)
                    base_cost = params['base_cost_per_sqm']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution for processing efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    processing_cost_per_sqm = base_cost + (beta_values - 0.5) * scale
                    processing_cost_per_sqm = np.maximum(processing_cost_per_sqm, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers (manufacturing cost)
                    processing_cost_per_sqm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total processing cost for fabric area
                    component_costs = processing_cost_per_sqm * fabric_area_sqm
                    
                elif component == 'stretch_quality_validation':
                    # Exponential distribution for stretch quality validation (performance-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (testing cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for Abrasion-Resistant Bonding
        elif product_name == 'Abrasion-Resistant Bonding':
            tech_specs = assumptions.get('technical_specs', {})
            bonding_area_sqm = tech_specs.get('bonding_area_per_unit_sqm', 0.8)
            abrasion_cycles = tech_specs.get('abrasion_cycles_target', 50000)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'high_density_polyamide':
                    # Triangular distribution for high-density polyamide (€10-15/m²)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    cost_per_sqm = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (material cost)
                    cost_per_sqm *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for bonding area per unit
                    component_costs = cost_per_sqm * bonding_area_sqm
                    
                elif component == 'abrasion_bonding_process':
                    # Beta distribution for abrasion bonding process (€8-20/m² range)
                    base_cost = params['base_cost_per_sqm']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution for bonding process efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    bonding_cost_per_sqm = base_cost + (beta_values - 0.5) * scale
                    bonding_cost_per_sqm = np.maximum(bonding_cost_per_sqm, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers (manufacturing cost)
                    bonding_cost_per_sqm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total bonding cost for bonding area
                    component_costs = bonding_cost_per_sqm * bonding_area_sqm
                    
                elif component == 'abrasion_cycle_testing':
                    # Exponential distribution for abrasion cycle testing (durability-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (testing cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'durability_qa_inspection':
                    # Triangular distribution for durability QA inspection (€6-14/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (QA cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for MacronLock Magnetic Closures
        elif product_name == 'MacronLock Magnetic Closures':
            tech_specs = assumptions.get('technical_specs', {})
            magnet_pairs = tech_specs.get('magnet_pairs_per_unit', 2)
            hold_strength_n = tech_specs.get('magnetic_hold_strength_n', 8)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'neodymium_magnets':
                    # Triangular distribution for neodymium magnets (€2-3/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    cost_per_magnet = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (material cost - rare earth materials)
                    cost_per_magnet *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for magnet pairs per unit
                    component_costs = cost_per_magnet * magnet_pairs
                    
                elif component == 'cnc_machining_housing':
                    # Beta distribution for CNC machining with 18% waste factor
                    base_cost = params['base_cost_per_unit']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    waste_factor = params['waste_factor']
                    
                    # Beta distribution for machining efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    machining_costs = base_cost + (beta_values - 0.5) * scale
                    machining_costs = np.maximum(machining_costs, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply 18% waste factor for precision CNC operations
                    machining_costs *= (1 + waste_factor)
                    
                    # Apply geographical multipliers (manufacturing cost)
                    machining_costs *= scenario_params['labor_cost_multiplier']
                    component_costs = machining_costs
                    
                elif component == 'magnetic_assembly_calibration':
                    # Triangular distribution for magnetic assembly & calibration (€4-9/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (skilled assembly - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'magnetic_strength_validation':
                    # Exponential distribution for magnetic strength validation (strength-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (testing cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for Auto-Tension Drawstrings
        elif product_name == 'Auto-Tension Drawstrings':
            tech_specs = assumptions.get('technical_specs', {})
            drawstring_length_m = tech_specs.get('drawstring_length_per_unit_m', 1.5)
            tension_range = tech_specs.get('tension_range_n', [2, 12])
            silicone_area_sqcm = tech_specs.get('silicone_grip_area_sqcm', 15)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'adaptive_spring_system':
                    # Triangular distribution for adaptive spring system (€3-5/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (precision manufacturing - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'high_performance_drawstring':
                    # Normal distribution for high-performance drawstring material (€18/m)
                    base_per_meter = params['base_per_meter']
                    std_dev = params['std_dev']
                    cost_per_meter = np.random.normal(base_per_meter, std_dev, self.n_simulations)
                    cost_per_meter = np.maximum(cost_per_meter, base_per_meter * 0.6)  # Floor at 60%
                    
                    # Apply geographical multipliers (material cost)
                    cost_per_meter *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for drawstring length per unit
                    component_costs = cost_per_meter * drawstring_length_m
                    
                elif component == 'silicone_grip_application':
                    # Beta distribution for silicone grip application process (€5-13/unit range)
                    base_cost = params['base_cost_per_unit']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution for application efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    application_costs = base_cost + (beta_values - 0.5) * scale
                    application_costs = np.maximum(application_costs, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers (specialized manufacturing - labor cost)
                    application_costs *= scenario_params['labor_cost_multiplier']
                    component_costs = application_costs
                    
                elif component == 'tension_mechanism_assembly':
                    # Triangular distribution for tension mechanism assembly (€6-14/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (skilled assembly - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'tension_performance_validation':
                    # Exponential distribution for tension performance validation (performance-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (testing cost - labor)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for 100% Recycled Performance Jacquard
        elif product_name == '100% Recycled Performance Jacquard':
            tech_specs = assumptions.get('technical_specs', {})
            fabric_area_sqm = tech_specs.get('fabric_area_per_unit_sqm', 1.0)
            bottles_per_sqm = tech_specs.get('pet_bottles_per_sqm', 12)
            carbon_reduction_target = tech_specs.get('carbon_reduction_percentage', 37)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'pet_bottle_processing_12_bottles_per_sqm':
                    # Triangular distribution for PET bottle processing (€8-18/m²)
                    min_cost = params['min_cost_per_sqm']
                    mode_cost = params['mode_cost_per_sqm']
                    max_cost = params['max_cost_per_sqm']
                    cost_per_sqm = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (specialized recycling - labor cost)
                    cost_per_sqm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total cost for fabric area per unit
                    component_costs = cost_per_sqm * fabric_area_sqm
                    
                elif component == 'recycled_fiber_spinning':
                    # Beta distribution for recycled fiber spinning (€15-35/m² range)
                    base_cost = params['base_cost_per_sqm']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution for spinning efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    spinning_cost_per_sqm = base_cost + (beta_values - 0.5) * scale
                    spinning_cost_per_sqm = np.maximum(spinning_cost_per_sqm, base_cost * 0.6)  # Floor at 60%
                    
                    # Apply geographical multipliers (manufacturing cost)
                    spinning_cost_per_sqm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total spinning cost for fabric area
                    component_costs = spinning_cost_per_sqm * fabric_area_sqm
                    
                elif component == 'recycled_jacquard_weaving':
                    # Normal distribution for recycled jacquard weaving (€35/m²)
                    base_per_sqm = params['base_per_sqm']
                    std_dev = params['std_dev']
                    cost_per_sqm = np.random.normal(base_per_sqm, std_dev, self.n_simulations)
                    cost_per_sqm = np.maximum(cost_per_sqm, base_per_sqm * 0.7)  # Floor at 70%
                    
                    # Apply geographical multipliers (specialized weaving - labor cost)
                    cost_per_sqm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total weaving cost for fabric area
                    component_costs = cost_per_sqm * fabric_area_sqm
                    
                elif component == 'carbon_footprint_validation':
                    # Exponential distribution for carbon footprint validation (environmental testing)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (environmental testing - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'recycled_performance_qa':
                    # Triangular distribution for recycled performance QA (€10-25/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (quality assurance - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        # Handle new detailed cost structure for Bio-Based Water Repellents
        elif product_name == 'Bio-Based Water Repellents':
            tech_specs = assumptions.get('technical_specs', {})
            fabric_area_sqm = tech_specs.get('fabric_area_per_unit_sqm', 0.9)
            pressure_target_mm = tech_specs.get('target_pressure_resistance_mm', 20000)
            bio_polymer_percentage = tech_specs.get('bio_polymer_content_percentage', 85)
            
            for component, params in assumptions['variable_components'].items():
                dist_type = params.get('distribution', 'normal')
                
                if component == 'bio_based_polymers_20_percent_premium':
                    # Triangular distribution for bio-polymer premium (15-28% range)
                    conventional_base = params['conventional_base_cost_per_sqm']
                    min_premium = params['min_premium']
                    mode_premium = params['mode_premium']
                    max_premium = params['max_premium']
                    
                    # Generate premium percentage using triangular distribution
                    premium_factors = np.random.triangular(min_premium, mode_premium, max_premium, self.n_simulations)
                    
                    # Calculate bio-polymer cost with premium
                    bio_polymer_cost_per_sqm = conventional_base * (1 + premium_factors)
                    
                    # Apply geographical multipliers (advanced material cost)
                    bio_polymer_cost_per_sqm *= scenario_params['material_cost_multiplier']
                    
                    # Calculate total cost for fabric area per unit
                    component_costs = bio_polymer_cost_per_sqm * fabric_area_sqm
                    
                elif component == 'dwr_application_process':
                    # Beta distribution for DWR application process (€14-30/m² range)
                    base_cost = params['base_cost_per_sqm']
                    alpha = params['alpha']
                    beta_param = params['beta']
                    scale = params['scale']
                    
                    # Beta distribution for application efficiency
                    beta_values = np.random.beta(alpha, beta_param, self.n_simulations)
                    application_cost_per_sqm = base_cost + (beta_values - 0.5) * scale
                    application_cost_per_sqm = np.maximum(application_cost_per_sqm, base_cost * 0.6)  # Floor at 60%
                    
                    # Apply geographical multipliers (specialized manufacturing - labor cost)
                    application_cost_per_sqm *= scenario_params['labor_cost_multiplier']
                    
                    # Calculate total application cost for fabric area
                    component_costs = application_cost_per_sqm * fabric_area_sqm
                    
                elif component == 'hydrostatic_pressure_validation_20000mm':
                    # Exponential distribution for 20,000mm pressure validation (performance-driven)
                    rate = params['rate']
                    component_costs = np.random.exponential(1/rate, self.n_simulations)
                    
                    # Apply geographical multipliers (specialized testing - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'environmental_impact_validation':
                    # Triangular distribution for environmental impact validation (€12-28/unit)
                    min_cost = params['min']
                    mode_cost = params['mode']
                    max_cost = params['max']
                    component_costs = np.random.triangular(min_cost, mode_cost, max_cost, self.n_simulations)
                    
                    # Apply geographical multipliers (environmental certification - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                    
                elif component == 'bio_dwr_quality_assurance':
                    # Normal distribution for bio-DWR quality assurance (€15 ± €3)
                    base_cost = params['base']
                    std_dev = params['std_dev']
                    component_costs = np.random.normal(base_cost, std_dev, self.n_simulations)
                    component_costs = np.maximum(component_costs, base_cost * 0.5)  # Floor at 50%
                    
                    # Apply geographical multipliers (quality assurance - labor cost)
                    component_costs *= scenario_params['labor_cost_multiplier']
                
                variable_costs += component_costs
        
        else:
            # Legacy calculation for other products
            for component, params in assumptions['variable_components'].items():
                # Apply legacy logic for other products
                if component in ['elastane_premium', 'four_way_stretch_processing', 'stretch_quality_validation']:
                    # These are multipliers, not direct costs
                    base_cost = params['base']
                    uncertainty = params['uncertainty']
                    factor_values = np.random.normal(base_cost, base_cost * uncertainty, self.n_simulations)
                    factor_values = np.maximum(factor_values, 0.01)  # Minimum factor
                    
                    if component == 'elastane_premium':
                        # Elastane factor affects material costs
                        base_material_cost = 50  # Base material cost for elastane-containing products
                        elastane_costs = base_material_cost * factor_values
                        elastane_costs *= scenario_params['material_cost_multiplier']
                        variable_costs += elastane_costs
                    elif component == 'four_way_stretch_processing':
                        # Stretch processing affects material costs
                        base_stretch_cost = 18  # Base stretch cost per square meter
                        stretch_costs = base_stretch_cost * factor_values
                        stretch_costs *= scenario_params['material_cost_multiplier']
                        variable_costs += stretch_costs
                    elif component == 'stretch_quality_validation':
                        # Stretch quality validation affects testing costs
                        base_validation_cost = 12  # Base validation cost per unit
                        validation_costs = base_validation_cost * factor_values
                        validation_costs *= scenario_params['labor_cost_multiplier']
                        variable_costs += validation_costs
                else:
                    # Regular cost components
                    base_cost = params['base']
                    uncertainty = params['uncertainty']
                    component_costs = np.random.normal(base_cost, base_cost * uncertainty, self.n_simulations)
                    component_costs = np.maximum(component_costs, base_cost * 0.2)  # Floor at 20%
                    
                    # Apply geographical multipliers
                    if 'material' in component or 'fabric' in component:
                        component_costs *= scenario_params['material_cost_multiplier']
                    else:
                        component_costs *= scenario_params['labor_cost_multiplier']
                    
                    variable_costs += component_costs
        
        # Apply logistics costs and quality discounts
        total_variable_costs = variable_costs * (1 + scenario_params['logistics_cost_factor'])
        total_variable_costs *= (1 - scenario_params['quality_discount'])
        
        return {
            'fixed_costs': fixed_costs,
            'variable_costs': total_variable_costs
        }
    
    def run_analysis(self):
        """Run comprehensive Monte Carlo analysis for all products and scenarios"""
        print(f"\n🚀 MONTE CARLO ANALYSIS")
        print(f"📊 Simulations: {self.n_simulations:,}")
        print(f"🌍 Scenarios: {len(self.geographical_scenarios)}")
        
        # Load products
        products = self.load_products()
        print(f"🏭 Products: {len(products)}")
        
        # Run analysis for each scenario
        for scenario_name, scenario_params in self.geographical_scenarios.items():
            print(f"\n🌍 Analyzing {scenario_name}...")
            print(f"   {scenario_params['description']}")
            
            scenario_results = {
                'products': {},
                'portfolio_summary': {},
                'scenario_params': scenario_params
            }
            
            total_fixed_costs = np.zeros(self.n_simulations)
            total_variable_costs = np.zeros(self.n_simulations)
            
            for product in products:
                costs = self.calculate_costs(product, scenario_name, scenario_params)
                
                # Store product-level results
                scenario_results['products'][product] = {
                    'fixed_costs': {
                        'mean': float(np.mean(costs['fixed_costs'])),
                        'std': float(np.std(costs['fixed_costs'])),
                        'p5': float(np.percentile(costs['fixed_costs'], 5)),
                        'p95': float(np.percentile(costs['fixed_costs'], 95)),
                        'var_95': float(np.percentile(costs['fixed_costs'], 95))
                    },
                    'variable_costs': {
                        'mean': float(np.mean(costs['variable_costs'])),
                        'std': float(np.std(costs['variable_costs'])),
                        'p5': float(np.percentile(costs['variable_costs'], 5)),
                        'p95': float(np.percentile(costs['variable_costs'], 95))
                    },
                    'category': self.cost_assumptions.get(product, {}).get('category', 'Unknown'),
                    'complexity': self.cost_assumptions.get(product, {}).get('complexity', 'Unknown')
                }
                
                total_fixed_costs += costs['fixed_costs']
                total_variable_costs += costs['variable_costs']
            
            # Portfolio-level summary
            scenario_results['portfolio_summary'] = {
                'total_rd_investment': {
                    'mean': float(np.mean(total_fixed_costs)),
                    'std': float(np.std(total_fixed_costs)),
                    'confidence_90': [float(np.percentile(total_fixed_costs, 5)), 
                                    float(np.percentile(total_fixed_costs, 95))],
                    'var_95': float(np.percentile(total_fixed_costs, 95))
                },
                'lead_time_weeks': scenario_params['lead_time_weeks'],
                'products_analyzed': len(products)
            }
            
            self.results[scenario_name] = scenario_results
            
            # Print summary
            print(f"   💰 Total R&D Investment: €{np.mean(total_fixed_costs)/1e6:.2f}M")
            print(f"   ⏱️  Lead Time: {scenario_params['lead_time_weeks']} weeks")
    
    def generate_comparison_report(self):
        """Generate comprehensive comparison report"""
        print(f"\n📋 COST ANALYSIS REPORT")
        print(f"=" * 60)
        
        # Scenario comparison table - showing R&D only (variable costs are per product)
        comparison_data = []
        for scenario_name, results in self.results.items():
            portfolio = results['portfolio_summary']
            comparison_data.append({
                'Scenario': scenario_name.replace('_', ' '),
                'R&D Investment (€M)': f"{portfolio['total_rd_investment']['mean']/1e6:.2f}",
                'Lead Time (weeks)': portfolio['lead_time_weeks'],
                'VaR 95% (€M)': f"{portfolio['total_rd_investment']['var_95']/1e6:.2f}"
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        print("\n🌍 GEOGRAPHICAL SCENARIO COMPARISON:")
        print(df_comparison.to_string(index=False))
        
        # Show variable costs per product for each scenario
        print(f"\n💰 VARIABLE COSTS PER PRODUCT (€/unit):")
        print("=" * 80)
        
        for scenario_name, results in self.results.items():
            print(f"\n🌍 {scenario_name.replace('_', ' ')}:")
            print(f"   {'Product':<35} {'Variable Cost (€/unit)':<20} {'Category'}")
            print(f"   {'-'*35} {'-'*20} {'-'*30}")
            
            product_costs = []
            for product, data in results['products'].items():
                var_cost = data['variable_costs']['mean']
                category = data['category']
                product_costs.append({
                    'product': product,
                    'cost': var_cost,
                    'category': category
                })
                print(f"   {product:<35} €{var_cost:<19.2f} {category}")
            
            # Show category averages
            categories = {}
            for item in product_costs:
                cat = item['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item['cost'])
            
            print(f"\n   📊 Category Averages:")
            for cat, costs in categories.items():
                avg_cost = sum(costs) / len(costs)
                print(f"   {cat}: €{avg_cost:.2f}/unit")
        
        # Cost savings analysis for R&D only
        eu_rd = self.results['EU_Production']['portfolio_summary']['total_rd_investment']['mean']
        asian_rd = self.results['Asian_Production']['portfolio_summary']['total_rd_investment']['mean']
        hybrid_rd = self.results['Hybrid_Model']['portfolio_summary']['total_rd_investment']['mean']
        
        print(f"\n💡 R&D COST ANALYSIS:")
        print(f"   All scenarios: €{eu_rd/1e6:.2f}M (R&D happens only in Europe)")
        print(f"   Asian vs EU R&D Savings: {((eu_rd - asian_rd) / eu_rd * 100):.1f}%")
        
        # Variable cost savings examples
        print(f"\n💡 VARIABLE COST SAVINGS EXAMPLES:")
        eu_results = self.results['EU_Production']['products']
        asian_results = self.results['Asian_Production']['products']
        
        print(f"   {'Product':<35} {'EU Cost':<12} {'Asian Cost':<12} {'Savings'}")
        print(f"   {'-'*35} {'-'*12} {'-'*12} {'-'*10}")
        
        for product in list(eu_results.keys())[:5]:  # Show top 5 products
            eu_cost = eu_results[product]['variable_costs']['mean']
            asian_cost = asian_results[product]['variable_costs']['mean']
            savings = ((eu_cost - asian_cost) / eu_cost * 100)
            print(f"   {product:<35} €{eu_cost:<11.2f} €{asian_cost:<11.2f} {savings:.1f}%")
        
        # Product risk ranking
        print(f"\n🎯 TOP RISK PRODUCTS (by R&D VaR 95%):")
        risk_products = []
        for product, data in self.results['EU_Production']['products'].items():
            risk_products.append({
                'Product': product,
                'VaR 95% (€K)': data['fixed_costs']['var_95'] / 1000,
                'Category': data['category'],
                'Complexity': data['complexity']
            })
        
        risk_df = pd.DataFrame(risk_products).sort_values('VaR 95% (€K)', ascending=False)
        print(risk_df.head().to_string(index=False))
    
    def export_results(self):
        """Export comprehensive results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create product_costs directory
        results_dir = Path("product_costs")
        results_dir.mkdir(exist_ok=True)
        
        # Export comprehensive JSON
        output_file = results_dir / f"analysis_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'analysis_type': 'Monte Carlo Cost Analysis',
                'timestamp': timestamp,
                'simulations': self.n_simulations,
                'products_analyzed': len(self.cost_assumptions),
                'geographical_scenarios': len(self.geographical_scenarios)
            },
            'scenarios': self.results,
            'cost_assumptions': self.cost_assumptions
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n💾 Results exported to: {output_file}")
        return output_file

    def generate_executive_summary(self):
        """Generate executive summary with strategic insights per product"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create product_costs directory
        results_dir = Path("product_costs")
        results_dir.mkdir(exist_ok=True)
        
        # Get EU and Asian results for comparison
        eu_results = self.results['EU_Production']['products']
        asian_results = self.results['Asian_Production']['products']
        hybrid_results = self.results['Hybrid_Model']['products']
        
        executive_summary = {
            'metadata': {
                'document_type': 'Executive Strategic Summary',
                'timestamp': timestamp,
                'analysis_scope': 'Macron Portfolio Cost Optimization',
                'products_analyzed': len(self.cost_assumptions),
                'key_focus': 'Per-Component Strategic Insights & Cost Optimization'
            },
            'portfolio_overview': {
                'total_rd_investment': f"€{self.results['EU_Production']['portfolio_summary']['total_rd_investment']['mean']/1000000:.2f}M",
                'geographical_scenarios': 3,
                'cost_optimization_potential': "Up to 71.9% variable cost savings through geographical optimization",
                'risk_management': "VaR-based risk assessment across all products"
            },
            'product_insights': {}
        }
        
        # Define strategic insights for each product
        product_insights = {
            'Hydrotex Moisture-Control Liners': {
                'strategic_positioning': 'Premium moisture management solution with highest technical complexity',
                'cost_performance': {
                    'eu_production': f"€{eu_results['Hydrotex Moisture-Control Liners']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['Hydrotex Moisture-Control Liners']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['Hydrotex Moisture-Control Liners']['variable_costs']['mean'] - asian_results['Hydrotex Moisture-Control Liners']['variable_costs']['mean']) / eu_results['Hydrotex Moisture-Control Liners']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'Hydrotex membrane technology (€12-20/m²)',
                    'Nano-fiber blending R&D (6-8 months)',
                    'Precision laser cutting with minimal waste',
                    'EU lab testing premium (30%)'
                ],
                'technical_specifications': {
                    'moisture_transfer_rate': '15,000g/m²/24h',
                    'breathability_rating': 'RET < 6',
                    'durability_cycles': '50,000+ flex cycles',
                    'weight_target': '<150g/m²'
                },
                'strategic_insights': [
                    'Excellent geographical cost optimization (69.1% savings)',
                    'High R&D investment justified by premium positioning',
                    'Material costs dominate - focus on supplier optimization',
                    'Quality testing critical for brand differentiation'
                ],
                'risk_assessment': 'High complexity requires careful quality control in Asian production',
                'recommendations': [
                    'Prioritize Asian production for cost optimization',
                    'Maintain EU R&D and testing standards',
                    'Invest in supplier quality certification programs'
                ]
            },
            
            'EcoMesh Ventilation Panels': {
                'strategic_positioning': 'Sustainable ventilation solution with moderate complexity',
                'cost_performance': {
                    'eu_production': f"€{eu_results['EcoMesh Ventilation Panels']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['EcoMesh Ventilation Panels']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['EcoMesh Ventilation Panels']['variable_costs']['mean'] - asian_results['EcoMesh Ventilation Panels']['variable_costs']['mean']) / eu_results['EcoMesh Ventilation Panels']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'EcoMesh material premium (15%)',
                    'Laser perforation development (€150k)',
                    'Eco-material certification costs',
                    'Precision laser operation (€3-5/unit)'
                ],
                'technical_specifications': {
                    'airflow_rate': '2,500L/min/m²',
                    'perforation_pattern': 'Optimized hexagonal',
                    'eco_content': '75% recycled materials',
                    'weight_reduction': '40% vs traditional'
                },
                'strategic_insights': [
                    'Good cost optimization potential (41.4% savings)',
                    'Sustainability focus aligns with market trends',
                    'Moderate R&D investment with proven technology',
                    'Laser technology enables precision manufacturing'
                ],
                'risk_assessment': 'Medium risk - established technology with eco-certification requirements',
                'recommendations': [
                    'Hybrid model optimal for sustainability compliance',
                    'Focus on eco-certification in target markets',
                    'Scale laser perforation technology'
                ]
            },
            
            'HD Bonded Insulation Pads': {
                'strategic_positioning': 'High-performance thermal regulation with excellent cost optimization',
                'cost_performance': {
                    'eu_production': f"€{eu_results['HD Bonded Insulation Pads']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['HD Bonded Insulation Pads']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['HD Bonded Insulation Pads']['variable_costs']['mean'] - asian_results['HD Bonded Insulation Pads']['variable_costs']['mean']) / eu_results['HD Bonded Insulation Pads']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'PU foam material (€8/kg)',
                    'Thermal mapping R&D (€100k)',
                    'Precision laser cutting (20% waste factor)',
                    'Bonding process development'
                ],
                'technical_specifications': {
                    'thermal_resistance': 'R-value 4.2',
                    'compression_recovery': '>95% after 24h',
                    'temperature_range': '-40°C to +60°C',
                    'thickness_tolerance': '±0.5mm'
                },
                'strategic_insights': [
                    'Outstanding cost optimization (71.9% savings)',
                    'Material-intensive product benefits from Asian sourcing',
                    'Proven thermal technology reduces R&D risk',
                    'Laser cutting precision critical for performance'
                ],
                'risk_assessment': 'Low-medium risk - established materials with proven processes',
                'recommendations': [
                    'Prioritize Asian production for maximum savings',
                    'Optimize foam supplier relationships',
                    'Standardize cutting processes across facilities'
                ]
            },
            
            'Phase Change Material (PCM) Inserts': {
                'strategic_positioning': 'Advanced thermal regulation technology with high innovation content',
                'cost_performance': {
                    'eu_production': f"€{eu_results['Phase Change Material (PCM) Inserts']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['Phase Change Material (PCM) Inserts']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['Phase Change Material (PCM) Inserts']['variable_costs']['mean'] - asian_results['Phase Change Material (PCM) Inserts']['variable_costs']['mean']) / eu_results['Phase Change Material (PCM) Inserts']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'PCM pellets (€15-25/kg)',
                    'PCM formulation R&D (€200k)',
                    'Thermal imaging systems (€300k)',
                    'Micro-encapsulation process'
                ],
                'technical_specifications': {
                    'phase_change_temperature': '32°C ±2°C',
                    'thermal_storage_capacity': '180 J/g',
                    'encapsulation_efficiency': '>98%',
                    'cycle_durability': '10,000+ cycles'
                },
                'strategic_insights': [
                    'Strong cost optimization (67.2% savings)',
                    'High R&D investment in cutting-edge technology',
                    'Material costs significant but manageable',
                    'Thermal imaging validation critical for quality'
                ],
                'risk_assessment': 'High risk - advanced technology requiring specialized manufacturing',
                'recommendations': [
                    'Maintain EU R&D leadership',
                    'Carefully validate Asian manufacturing capabilities',
                    'Invest in thermal testing infrastructure'
                ]
            },
            
            'Performance Jacquard Reinforcement': {
                'strategic_positioning': 'Premium structural enhancement with complex textile engineering',
                'cost_performance': {
                    'eu_production': f"€{eu_results['Performance Jacquard Reinforcement']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['Performance Jacquard Reinforcement']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['Performance Jacquard Reinforcement']['variable_costs']['mean'] - asian_results['Performance Jacquard Reinforcement']['variable_costs']['mean']) / eu_results['Performance Jacquard Reinforcement']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'Jacquard fabric base (€54 base cost)',
                    'Elastane premium (€36-50)',
                    '4-way stretch processing (€12-31)',
                    'Stretch quality validation (€12/unit average)'
                ],
                'technical_specifications': {
                    'fabric_area': '0.8m² per unit',
                    'elastane_content': '25%',
                    'stretch_directions': '4-way',
                    'weight_reduction_target': '15%',
                    'stretch_recovery': '>95%'
                },
                'strategic_insights': [
                    'Moderate cost optimization (31.9% savings)',
                    'Complex textile engineering requires expertise',
                    'Material costs dominate overall structure',
                    'Quality validation critical for performance'
                ],
                'risk_assessment': 'Medium-high risk - complex textile engineering with quality requirements',
                'recommendations': [
                    'Hybrid model balances cost and quality',
                    'Focus on elastane supplier optimization',
                    'Invest in stretch testing capabilities'
                ]
            },
            
            'Abrasion-Resistant Bonding': {
                'strategic_positioning': 'Durability-focused structural solution with proven technology',
                'cost_performance': {
                    'eu_production': f"€{eu_results['Abrasion-Resistant Bonding']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['Abrasion-Resistant Bonding']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['Abrasion-Resistant Bonding']['variable_costs']['mean'] - asian_results['Abrasion-Resistant Bonding']['variable_costs']['mean']) / eu_results['Abrasion-Resistant Bonding']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'High-density polyamide (€10-15/m²)',
                    'ASTM D4966 testing rigs (€100k)',
                    'Polymer R&D development',
                    'Bonding process optimization'
                ],
                'technical_specifications': {
                    'abrasion_resistance': '>50,000 cycles',
                    'bond_strength': '25N/cm minimum',
                    'temperature_stability': '-20°C to +80°C',
                    'chemical_resistance': 'pH 4-9'
                },
                'strategic_insights': [
                    'Excellent cost optimization (61.7% savings)',
                    'Proven durability technology',
                    'Material costs benefit from Asian sourcing',
                    'Testing infrastructure investment required'
                ],
                'risk_assessment': 'Low-medium risk - established technology with proven durability',
                'recommendations': [
                    'Asian production for cost optimization',
                    'Standardize testing protocols globally',
                    'Focus on polyamide supplier relationships'
                ]
            },
            
            'MacronLock Magnetic Closures': {
                'strategic_positioning': 'Precision closure system with excellent cost optimization potential',
                'cost_performance': {
                    'eu_production': f"€{eu_results['MacronLock Magnetic Closures']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['MacronLock Magnetic Closures']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['MacronLock Magnetic Closures']['variable_costs']['mean'] - asian_results['MacronLock Magnetic Closures']['variable_costs']['mean']) / eu_results['MacronLock Magnetic Closures']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'Neodymium magnets (€2-3/unit)',
                    'CNC machining with 18% waste factor',
                    'Magnetic assembly calibration (€4-9/unit)',
                    'Magnetic strength validation'
                ],
                'technical_specifications': {
                    'magnetic_hold_strength': '8N minimum',
                    'concealment_level': '100% hidden',
                    'durability_target': '10,000+ open/close cycles',
                    'temperature_range': '-10°C to +50°C'
                },
                'strategic_insights': [
                    'Outstanding cost optimization (64.0% savings)',
                    'Precision manufacturing benefits from Asian capabilities',
                    'Established technology reduces risk',
                    'Material costs significant but manageable'
                ],
                'risk_assessment': 'Low-medium risk - established technology with proven testing protocols',
                'recommendations': [
                    'Asian production for maximum cost benefit',
                    'Invest in CNC process optimization',
                    'Standardize magnetic testing procedures'
                ]
            },
            
            'Auto-Tension Drawstrings': {
                'strategic_positioning': 'Adaptive closure system with moderate complexity',
                'cost_performance': {
                    'eu_production': f"€{eu_results['Auto-Tension Drawstrings']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['Auto-Tension Drawstrings']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['Auto-Tension Drawstrings']['variable_costs']['mean'] - asian_results['Auto-Tension Drawstrings']['variable_costs']['mean']) / eu_results['Auto-Tension Drawstrings']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'Adaptive spring system (€3-5/unit)',
                    'Silicone grip R&D development',
                    'Tension control mechanisms',
                    'Assembly and calibration processes'
                ],
                'technical_specifications': {
                    'tension_range': '2-15N adjustable',
                    'adjustment_precision': '±0.5N',
                    'grip_material': 'Medical-grade silicone',
                    'durability_target': '5,000+ adjustment cycles'
                },
                'strategic_insights': [
                    'Good cost optimization (46.8% savings)',
                    'Moderate complexity with proven components',
                    'Assembly processes benefit from Asian labor costs',
                    'Silicone technology well-established'
                ],
                'risk_assessment': 'Medium risk - mechanical components require quality control',
                'recommendations': [
                    'Hybrid model for balanced cost-quality',
                    'Focus on spring system reliability',
                    'Standardize assembly procedures'
                ]
            },
            
            '100% Recycled Performance Jacquard': {
                'strategic_positioning': 'Sustainability-focused premium fabric with complex recycling process',
                'cost_performance': {
                    'eu_production': f"€{eu_results['100% Recycled Performance Jacquard']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['100% Recycled Performance Jacquard']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['100% Recycled Performance Jacquard']['variable_costs']['mean'] - asian_results['100% Recycled Performance Jacquard']['variable_costs']['mean']) / eu_results['100% Recycled Performance Jacquard']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'PET bottle processing (€8-18/m²)',
                    'PET recycling process R&D (€500k)',
                    'CO₂ certification requirements',
                    '12 PET bottles/m² processing cost'
                ],
                'technical_specifications': {
                    'recycled_content': '100% post-consumer PET',
                    'pet_bottles_per_sqm': '12 bottles',
                    'carbon_reduction': '60% vs virgin materials',
                    'performance_retention': '>95% vs virgin'
                },
                'strategic_insights': [
                    'Exceptional cost optimization (73.9% savings)',
                    'High sustainability value proposition',
                    'Complex recycling process requires expertise',
                    'Carbon certification adds market value'
                ],
                'risk_assessment': 'High risk - complex recycling technology with sustainability compliance',
                'recommendations': [
                    'Asian production for cost optimization',
                    'Maintain EU sustainability certification',
                    'Invest in PET processing technology'
                ]
            },
            
            'Bio-Based Water Repellents': {
                'strategic_positioning': 'Advanced sustainable chemistry with premium environmental positioning',
                'cost_performance': {
                    'eu_production': f"€{eu_results['Bio-Based Water Repellents']['variable_costs']['mean']:.2f}/unit",
                    'asian_production': f"€{asian_results['Bio-Based Water Repellents']['variable_costs']['mean']:.2f}/unit",
                    'cost_savings_potential': f"{((eu_results['Bio-Based Water Repellents']['variable_costs']['mean'] - asian_results['Bio-Based Water Repellents']['variable_costs']['mean']) / eu_results['Bio-Based Water Repellents']['variable_costs']['mean'] * 100):.1f}%"
                },
                'key_cost_drivers': [
                    'Bio-based polymers (20% premium)',
                    'C6-free chemistry development (€400k)',
                    'Hydrostatic testing requirements',
                    'Environmental compliance certification'
                ],
                'technical_specifications': {
                    'water_repellency': '>1000mm hydrostatic head',
                    'bio_content': '70% bio-based materials',
                    'pfas_free': '100% C6-free chemistry',
                    'durability_cycles': '50+ wash cycles'
                },
                'strategic_insights': [
                    'Strong cost optimization (52.2% savings)',
                    'Highest R&D investment reflects innovation complexity',
                    'Environmental compliance critical for market access',
                    'Bio-based materials command premium pricing'
                ],
                'risk_assessment': 'Very high risk - cutting-edge chemistry with regulatory complexity',
                'recommendations': [
                    'Maintain EU R&D and regulatory leadership',
                    'Carefully validate Asian manufacturing capabilities',
                    'Invest in environmental testing infrastructure'
                ]
            }
        }
        
        # Add insights to executive summary
        executive_summary['product_insights'] = product_insights
        
        # Add portfolio-level strategic recommendations
        executive_summary['strategic_recommendations'] = {
            'geographical_optimization': {
                'high_savings_products': [
                    'HD Bonded Insulation Pads (71.9% savings)',
                    '100% Recycled Performance Jacquard (73.9% savings)',
                    'Hydrotex Moisture-Control Liners (69.1% savings)'
                ],
                'moderate_savings_products': [
                    'MacronLock Magnetic Closures (64.0% savings)',
                    'Auto-Tension Drawstrings (46.8% savings)',
                    'Bio-Based Water Repellents (52.2% savings)'
                ],
                'complex_products_requiring_care': [
                    'Performance Jacquard Reinforcement (31.9% savings)',
                    'Phase Change Material (PCM) Inserts (67.2% savings)'
                ]
            },
            'risk_management': {
                'high_risk_products': [
                    'Bio-Based Water Repellents - regulatory complexity',
                    'Phase Change Material (PCM) Inserts - advanced technology',
                    '100% Recycled Performance Jacquard - sustainability compliance'
                ],
                'medium_risk_products': [
                    'Performance Jacquard Reinforcement - textile engineering',
                    'Hydrotex Moisture-Control Liners - quality control'
                ],
                'low_risk_products': [
                    'MacronLock Magnetic Closures - established technology',
                    'HD Bonded Insulation Pads - proven materials'
                ]
            },
            'investment_priorities': [
                'Prioritize Asian production for material-intensive products',
                'Maintain EU R&D leadership for advanced technologies',
                'Invest in quality control systems for complex products',
                'Focus on supplier relationships for critical materials',
                'Develop hybrid models for balanced cost-quality optimization'
            ]
        }
        
        # Export executive summary
        summary_file = results_dir / f"executive_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(executive_summary, f, indent=2)
        
        print(f"\n📋 Executive Summary exported to: {summary_file}")
        return summary_file

    def generate_visualizations(self):
        """Generate visualization plots for fixed costs and COGS analysis"""
        print("\n📊 Generating visualization plots...")
        
        # Create product_costs directory if it doesn't exist
        results_dir = Path("product_costs")
        results_dir.mkdir(exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Extract data for plotting
        product_names = []
        fixed_costs = []
        eu_costs = []
        asia_costs = []
        hybrid_costs = []
        
        # Get product names from EU Production results (all scenarios have same products)
        eu_products = self.results['EU_Production']['products']
        
        for product_name, product_data in eu_products.items():
            product_names.append(product_name.replace(' ', '\n'))  # Line breaks for better display
            
            # Fixed costs (same across all scenarios, so use EU data)
            fixed_costs.append(product_data['fixed_costs']['mean'])
            
            # Variable costs by scenario
            eu_costs.append(self.results['EU_Production']['products'][product_name]['variable_costs']['mean'])
            asia_costs.append(self.results['Asian_Production']['products'][product_name]['variable_costs']['mean'])
            hybrid_costs.append(self.results['Hybrid_Model']['products'][product_name]['variable_costs']['mean'])
        
        # Create timestamp for file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Plot 1: Fixed Costs
        plt.figure(figsize=(16, 10))
        bars = plt.bar(range(len(product_names)), fixed_costs, 
                      color='steelblue', alpha=0.8, edgecolor='navy', linewidth=1.5)
        
        # Customize the plot
        plt.title('Fixed R&D Costs by Product Component\nMonte Carlo Analysis (100,000 simulations)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Product Components', fontsize=14, fontweight='bold')
        plt.ylabel('Mean Fixed R&D Costs (€)', fontsize=14, fontweight='bold')
        
        # Set x-axis labels with rotation for better readability
        plt.xticks(range(len(product_names)), product_names, rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=12)
        
        # Add value labels on top of bars
        for i, (bar, cost) in enumerate(zip(bars, fixed_costs)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(fixed_costs)*0.01,
                    f'€{cost/1000:.0f}K', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Format y-axis to show values in thousands
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x/1000:.0f}K'))
        
        plt.tight_layout()
        
        # Save the plot
        fixed_costs_file = results_dir / f"fixed_costs_analysis_{timestamp}.png"
        plt.savefig(fixed_costs_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Fixed costs plot saved to: {fixed_costs_file}")
        plt.close()
        
        # Plot 2: COGS (Cost of Goods Produced) - Variable Costs by Scenario
        plt.figure(figsize=(18, 12))
        
        # Set up positions for grouped bars
        x = np.arange(len(product_names))
        width = 0.25
        
        # Create grouped bars
        bars1 = plt.bar(x - width, eu_costs, width, label='EU Production', 
                       color='#FF6B6B', alpha=0.8, edgecolor='darkred', linewidth=1)
        bars2 = plt.bar(x, asia_costs, width, label='Asian Production', 
                       color='#4ECDC4', alpha=0.8, edgecolor='darkgreen', linewidth=1)
        bars3 = plt.bar(x + width, hybrid_costs, width, label='Hybrid Model', 
                       color='#45B7D1', alpha=0.8, edgecolor='darkblue', linewidth=1)
        
        # Customize the plot
        plt.title('Variable Costs (COGS) by Production Scenario\nMonte Carlo Analysis (100,000 simulations)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Product Components', fontsize=14, fontweight='bold')
        plt.ylabel('Mean Variable Cost per Unit (€)', fontsize=14, fontweight='bold')
        
        # Set x-axis labels
        plt.xticks(x, product_names, rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=12)
        
        # Add value labels on top of bars
        def add_value_labels(bars, costs):
            for bar, cost in zip(bars, costs):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2, height + max(max(eu_costs), max(asia_costs), max(hybrid_costs))*0.01,
                        f'€{cost:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
        
        add_value_labels(bars1, eu_costs)
        add_value_labels(bars2, asia_costs)
        add_value_labels(bars3, hybrid_costs)
        
        # Add legend
        plt.legend(loc='upper left', fontsize=12, framealpha=0.9)
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add savings annotations for key products
        for i, (eu, asia) in enumerate(zip(eu_costs, asia_costs)):
            if eu > 0:  # Avoid division by zero
                savings = ((eu - asia) / eu) * 100
                if savings > 50:  # Only annotate significant savings
                    plt.annotate(f'{savings:.1f}% savings', 
                               xy=(i, asia), xytext=(i, asia + max(asia_costs)*0.15),
                               ha='center', fontsize=8, color='darkgreen', fontweight='bold',
                               arrowprops=dict(arrowstyle='->', color='darkgreen', alpha=0.7))
        
        plt.tight_layout()
        
        # Save the plot
        cogs_file = results_dir / f"cogs_analysis_{timestamp}.png"
        plt.savefig(cogs_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 COGS analysis plot saved to: {cogs_file}")
        plt.close()
        
        print(f"✅ Visualization plots generated successfully!")
        return fixed_costs_file, cogs_file

def main():
    """Run the Monte Carlo analysis"""
    print("🎯 MONTE CARLO COST ANALYSIS")
    print("=" * 50)
    
    # Initialize and run analysis
    analysis = MonteCarloCostAnalysis(n_simulations=100000)
    analysis.run_analysis()
    analysis.generate_comparison_report()
    analysis.export_results()
    analysis.generate_executive_summary()
    analysis.generate_visualizations()
    
    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"📊 All 10 products analyzed across 3 geographical scenarios")
    print(f"📈 Visualization plots generated")
    print(f"🎯 Ready for ModaMesh Phase 2 integration")

if __name__ == "__main__":
    main() 