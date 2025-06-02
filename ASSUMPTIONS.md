# MODAMESH™ SIMULATION ASSUMPTIONS

This document consolidates all assumptions applied in the ModaMesh™ simulation models, agents, and analysis. These assumptions were necessary to create a computationally tractable simulation while maintaining decision-relevant accuracy.

## TABLE OF CONTENTS

1. [Financial & Economic Assumptions](#financial--economic-assumptions)
2. [Market Assumptions](#market-assumptions)
3. [Brand Agent Behavior Assumptions](#brand-agent-behavior-assumptions)
4. [Production & Capacity Assumptions](#production--capacity-assumptions)
5. [Cost Modeling Assumptions](#cost-modeling-assumptions)
6. [Partnership Model Assumptions](#partnership-model-assumptions)
7. [Market Dynamics & Evolution Assumptions](#market-dynamics--evolution-assumptions)
8. [Technical & Operational Assumptions](#technical--operational-assumptions)
9. [Simulation Design Assumptions](#simulation-design-assumptions)

---

## FINANCIAL & ECONOMIC ASSUMPTIONS

### Pricing Models
1. **Co-branded Markup**: Base margin of 35% to brand, reduced to 28% in simulation for realism
   - Brand value premium: 0-6% based on market leader score
   - Segment premiums: 0% (technical) to 12% (luxury fashion)
   - Marketing factor: 3% additional markup
   - Volume discounts: 3-5% for orders >20,000 units

2. **White-label Markup**: Base margin of 14% to brand
   - Volume adjustments: -2% to -8% based on order size
   - Lower upfront investment requirement assumed

3. **R&D Amortization**
   - Total R&D investment: €5.77M
   - Amortization period: 5 years straight-line
   - Allocation: Per-unit based on production volume

4. **Working Capital**
   - Payment terms: Net 60 days
   - Inventory turnover: 6x per year
   - No financing costs included in calculations

5. **Discount Rate**: 8% annual for NPV calculations

---

## MARKET ASSUMPTIONS

### Market Structure
1. **Brand Behavior**
   - Brands act as rational actors with bounded rationality
   - Independent decision-making (no collusion)
   - Perfect information for Macron, imperfect for brands

2. **Competition**
   - No direct competitors to Macron modeled explicitly
   - Competition manifests through opportunity cost
   - No retaliation dynamics or price wars

3. **Demand Characteristics**
   - Linear demand curves assumed
   - No seasonality effects
   - No fashion cycles modeled
   - Demand based on percentage of brand's estimated production:
     - Co-branded: 1% of brand production
     - White-label: 1.5% of brand production

4. **Market Size**
   - Italian fashion market segmented into 7 distinct segments
   - 67 brands modeled across segments
   - Segment growth rates: 1% (mature luxury) to 10% (high-performance luxury)

---

## BRAND AGENT BEHAVIOR ASSUMPTIONS

### Dynamic Attributes
1. **Risk Appetite**: Uniformly distributed [0,1]
   - Modified by brand size: larger brands slightly more risk-tolerant
   - Affects partnership acceptance threshold

2. **Decision Speed**: Uniformly distributed [0,1]
   - Modified by organization type:
     - Public companies: 20% slower (factor 0.8)
     - Family-owned: 20% faster (factor 1.2)

3. **Luxury Move Pressure**
   - Technical brands (segments 1,2): 40-60% pressure
   - Luxury brands (segments 5,6,7): 0-30% pressure
   - Mixed segments: 30-70% pressure

### Decision-Making
1. **Partnership Evaluation**
   - Brands evaluate based on weighted scoring:
     - Segment fit: 25%
     - Innovation match: 20%
     - Price value: 20%
     - Brand synergy: 20%
     - Exclusivity value: 15%
   - Stochastic element: ±10 point noise added to scores

2. **Continuation Probability**
   - Co-branded: 85% annual renewal base rate
   - White-label: 70% annual renewal base rate
   - Modified by performance and market factors

---

## PRODUCTION & CAPACITY ASSUMPTIONS

### Macron Capacity Model
1. **Total Production**: 2,000,000 units/year
2. **B2B Allocation**: 50% (1,000,000 units)
3. **Product Complexity Constraints**:
   - Low complexity: Up to 50% of capacity
   - Medium complexity: Up to 40% of capacity
   - High complexity: Up to 30% of capacity
   - Very High complexity: Up to 20% of capacity

4. **Order Constraints**
   - Minimum batch size: 1,000 units
   - Maximum per partner: 10% of total capacity
   - Co-branded setup overhead: 5,000 unit equivalents per partner
   - White-label setup overhead: 2,000 unit equivalents per partner

5. **Efficiency Improvements**: 3% annual capacity improvement through learning

---

## COST MODELING ASSUMPTIONS

### Cost Structure
1. **Cost Components**
   - Materials: 40% of COGS
   - Labor: 30% of COGS
   - Overhead: 30% of COGS

2. **Geographic Production Scenarios**
   - EU Production: +40% labor cost, 4-week lead time
   - Asian Production: -70% labor cost, 16-week lead time
   - Hybrid Model: -40% labor cost, 12-week lead time

3. **Cost Distributions** (Monte Carlo)
   - R&D costs: Log-normal distribution (research uncertainty)
   - Material costs: Normal distribution (established supply chains)
   - Manufacturing: Beta distribution (bounded efficiency)
   - Quality control: Exponential distribution (defect-driven)
   - Assembly: Triangular distribution (min/mode/max scenarios)

### Product-Specific Assumptions
1. **PCM Inserts**: €15-25/kg for phase change material pellets
2. **Jacquard Reinforcement**: 25% elastane content, €35/m² premium
3. **Magnetic Closures**: €2-3/unit for neodymium magnets
4. **Laser Processing**: 20% material waste factor

---

## PARTNERSHIP MODEL ASSUMPTIONS

### Co-Branded Model
1. **Brand Visibility**: "Powered by Macron" on all products
2. **Exclusivity**: Limited partnerships per category
3. **Premium Positioning**: 15-20% retail price premium assumed
4. **Marketing Investment**: 3% of revenue for joint marketing

### White-Label Model
1. **Complete Invisibility**: No Macron branding
2. **Volume Priority**: Higher minimum volumes expected
3. **Cost Efficiency**: 30% cost savings vs. internal development
4. **Flexibility**: Full customization available

---

## MARKET DYNAMICS & EVOLUTION ASSUMPTIONS

### Natural Evolution
1. **Consumer Preferences**
   - Sustainability importance: +0.5% per quarter
   - Functionality importance: Linked to tech innovation heat
   - Price sensitivity: Inversely related to economic confidence
   - Brand status: Affected by economic cycles

2. **Market Indicators**
   - Tech innovation: Follows sine wave cycles
   - Luxury-tech convergence: +1% per quarter (major trend)
   - Sustainability pressure: +0.8% per quarter
   - Economic confidence: Business cycle oscillations

### Market Shocks
1. **Shock Probabilities** (annual):
   - Recession: 10%
   - Sustainability push: 20%
   - Tech boom: 15%
   - Luxury crisis: 8%

2. **Shock Durations**: 1-3 quarters typically
3. **Shock Intensity**: 0.4-0.8 on normalized scale

---

## TECHNICAL & OPERATIONAL ASSUMPTIONS

### Production
1. **Raw Materials**: Infinite availability assumed
2. **Quality**: No production defects modeled
3. **Lead Times**: Deterministic (no variability)
4. **Logistics**: Stable shipping costs, no disruptions

### Information Flow
1. **Macron**: Perfect information about all opportunities
2. **Brands**: Imperfect knowledge of competitor actions
3. **Market Data**: Quarterly updates available to all
4. **No Information Asymmetry**: Within partnerships

---

## SIMULATION DESIGN ASSUMPTIONS

### Monte Carlo Parameters
1. **Simulation Runs**: 10,000 per scenario
2. **Time Horizon**: 5 years (60 months)
3. **Time Steps**: Monthly decision periods
4. **Random Seed**: Base seed 42 for reproducibility

### Agent Initialization
1. **Brand Count**: 67 Italian fashion brands
2. **Segment Distribution**: Based on actual market data
3. **Financial Data**: From public filings where available
4. **Missing Data**: Filled with segment averages

### Decision Timing
1. **Partnership Evaluation**: Monthly opportunities
2. **Market Updates**: Quarterly
3. **Shock Events**: Random timing within simulation
4. **Contract Duration**: Annual with renewal options

---

## VALIDATION & CALIBRATION

1. **Historical Calibration**
   - Brand revenues validated against public data
   - Market segments aligned with McKinsey/Bain reports
   - Cost structures benchmarked against industry standards

2. **Sensitivity Testing**
   - ±20% variation tested on all parameters
   - Model stability confirmed across ranges
   - Co-branded advantage robust to variations

3. **Convergence**
   - Mean outcomes stabilize <1% variance at 10,000 runs
   - Distribution shapes consistent after 5,000 runs
   - Tail events adequately captured

---

## KEY SIMPLIFICATIONS

1. **Market Dynamics**
   - No new market entrants during simulation
   - No mergers or acquisitions
   - No regulatory changes beyond scheduled sustainability

2. **Product Evolution**
   - Fixed product portfolio (10 products)
   - No new product development
   - No product obsolescence

3. **Geographic Scope**
   - Focus on Italian market only
   - No explicit modeling of export markets
   - Currency effects not considered

4. **Strategic Responses**
   - No competitive responses to Macron entry
   - No imitation or copying of innovations
   - No strategic alliances between brands

---
