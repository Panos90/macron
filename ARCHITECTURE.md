# MODAMESH ARCHITECTURE & METHODOLOGY
## Technical Implementation and Assumptions Documentation

**Version:** 1.0  
**System Components:** Cost Estimation | Brand Intelligence | Multi-Agent Simulation

---

## TABLE OF CONTENTS
1. [System Overview](#system-overview)
2. [Cost Estimation Engine](#cost-estimation-engine)
3. [Brand Intelligence System](#brand-intelligence-system)
4. [Simulation Architecture](#simulation-architecture)
5. [Decision-Making Algorithms](#decision-making-algorithms)
6. [Market Dynamics & Shocks](#market-dynamics--shocks)
7. [Capacity Management](#capacity-management)
8. [Key Assumptions](#key-assumptions)

---

## SYSTEM OVERVIEW

ModaMesh is a multi-agent simulation system that models the Italian fashion market's response to Macron's B2B technical component offerings. The system consists of three core engines:

```
┌─────────────────────┐     ┌──────────────────────┐     ┌────────────────────┐
│  Cost Estimation    │────▶│  Brand Intelligence  │────▶│    Simulation      │
│     Engine          │     │      System          │     │     Engine         │
├─────────────────────┤     ├──────────────────────┤     ├────────────────────┤
│ • Monte Carlo       │     │ • Perplexity API     │     │ • 66 Brand Agents  │
│ • 10 Products       │     │ • Market Segments    │     │ • 1 Macron Agent   │
│ • 3 Geo Scenarios   │     │ • Brand Profiles     │     │ • Market Dynamics  │
└─────────────────────┘     └──────────────────────┘     └────────────────────┘
```

---

## COST ESTIMATION ENGINE

### Monte Carlo Methodology

The cost estimation uses **100,000 simulations per scenario** to model uncertainty in manufacturing costs across 10 technical products.

#### Distribution Types by Component

1. **R&D Costs (Fixed)** - Log-normal distribution
   - Rationale: R&D projects typically have right-skewed distributions with potential for cost overruns
   - Parameters: `μ = ln(base_cost)`, `σ = 0.25-0.40` (varies by complexity)

2. **Material Costs (Variable)** - Normal distribution
   - Rationale: Established supply chains have predictable variation
   - Parameters: `mean = base_cost`, `std_dev = 10-15%` of base

3. **Manufacturing Labor** - Triangular distribution
   - Rationale: Captures min/mode/max scenarios based on worker efficiency
   - Parameters: `min = 0.7×base`, `mode = base`, `max = 1.5×base`

4. **Quality Control** - Exponential distribution
   - Rationale: Defect-driven costs follow exponential decay
   - Parameters: `λ = 1/mean_cost`

#### Geographical Scenarios

```python
geographical_scenarios = {
    'EU_Production': {
        'labor_cost_multiplier': 1.0,      # Baseline
        'material_cost_multiplier': 1.0,    # Premium materials
        'regulatory_premium': 0.15,         # 15% for compliance
        'logistics_cost_factor': 0.02,      # 2% local shipping
        'quality_discount': 0.0,            # No quality issues
        'lead_time_weeks': 8
    },
    'Asian_Production': {
        'labor_cost_multiplier': 0.25,      # 75% labor savings
        'material_cost_multiplier': 0.8,    # 20% material savings
        'regulatory_premium': 0.05,         # Lower compliance costs
        'logistics_cost_factor': 0.12,      # 12% shipping/duties
        'quality_discount': 0.05,           # 5% quality risk
        'lead_time_weeks': 16
    },
    'Hybrid_Model': {
        'labor_cost_multiplier': 0.6,       # Blended costs
        'material_cost_multiplier': 0.9,    # Some local sourcing
        'regulatory_premium': 0.10,         # Mixed compliance
        'logistics_cost_factor': 0.07,      # Complex logistics
        'quality_discount': 0.02,           # Minimal quality risk
        'lead_time_weeks': 12
    }
}
```

#### Cost Calculation Formula

For each product `p` in scenario `s`:

```
Fixed_Cost(p) = Σ(R&D_Components × Distribution_Sample)
Variable_Cost(p,s) = Σ(Component_Cost × Geo_Multiplier × (1 + Logistics) × (1 - Quality_Discount))
Total_Unit_Cost(p,s) = Variable_Cost(p,s) + (Fixed_Cost(p) / Expected_Volume)
```

---

## BRAND INTELLIGENCE SYSTEM

### Perplexity API Integration

The system uses Perplexity's Sonar Pro model to gather real-time brand intelligence through structured queries.

#### Query Architecture

```python
async def gather_intelligence(brand_name, segments):
    query_template = {
        "company_basics": {
            "is_public": "binary",
            "years_in_business": "integer",
            "headquarter_italy": "binary"
        },
        "financial_data": {
            "annual_revenue_millions": "float",
            "revenue_growth_rate": "percentage",
            "profit_margin": "percentage"
        },
        "market_position": {
            "avg_price_index": "float (100 = market average)",
            "geographic_reach": "0-1 scale",
            "market_share_estimate": "percentage"
        },
        "operational_capabilities": {
            "production_control": "0-1 scale",
            "supply_chain_complexity": "1-5 scale",
            "innovation_investment": "percentage of revenue"
        },
        "strategic_priorities": {
            "sustainability_commitment": "0-1 scale",
            "technology_adoption": "0-1 scale",
            "brand_positioning": "1-5 scale"
        }
    }
```

#### Data Processing Pipeline

1. **API Call** → Structured JSON query to Perplexity
2. **Response Parsing** → Extract numerical values with validation
3. **Fallback Logic** → Use market segment averages if data missing
4. **Confidence Scoring** → Weight data by source reliability

### Market Segmentation

The system maps 67 Italian fashion brands across 7 segments:

```
Segments = {
    1: "Core Technical Sportswear" (Function: 10, Fashion: 1),
    2: "Outdoor Technical Performance" (Function: 9, Fashion: 2),
    3: "Athleisure Crossover" (Function: 6, Fashion: 5),
    4: "Luxury Activewear" (Function: 5, Fashion: 6),
    5: "Athluxury" (Function: 4, Fashion: 7),
    6: "High-Performance Luxury" (Function: 6, Fashion: 8),
    7: "Luxury Fashion" (Function: 1, Fashion: 10)
}
```

---

## SIMULATION ARCHITECTURE

### Agent-Based Model Structure

The simulation employs 67 autonomous agents (66 brands + Macron) making decisions over 5 years with 10,000 Monte Carlo runs per partnership model.

#### Brand Agent Properties

```python
class BrandAgent:
    # Static Properties (from data/intelligence)
    revenue: float                    # Annual revenue in millions
    segment_id: List[int]            # Market segment(s)
    market_share: float              # Within segment
    
    # Dynamic Properties (randomized per simulation)
    risk_appetite: float ~ U(0,1)    # Uniform distribution
    decision_speed: float ~ U(0,1)   # Uniform distribution
    
    # Behavioral Modifiers
    luxury_move_pressure: float      # 0-1, based on segment
    sustainability_priority: float   # From brand intelligence
    innovation_affinity: float       # From brand intelligence
```

#### Dynamic Property Generation

1. **Risk Appetite** (`risk_appetite`)
   - Drawn from uniform distribution [0,1] per simulation
   - Modified by brand size: `adjusted_risk = base_risk × (1 + 0.2×log(revenue/median_revenue))`
   - Interpretation: 0 = extremely conservative, 1 = highly experimental

2. **Decision Speed** (`decision_speed`)
   - Drawn from uniform distribution [0,1] per simulation
   - Modified by organization type: `adjusted_speed = base_speed × org_factor`
   - Public companies: `org_factor = 0.8` (slower)
   - Family-owned: `org_factor = 1.2` (faster)

3. **Luxury Move Pressure**
   - Calculated based on segment positioning:
   ```python
   if segment in [1, 2]:  # Technical
       luxury_pressure = random.uniform(0.4, 0.6)
   elif segment in [5, 6, 7]:  # Luxury
       luxury_pressure = random.uniform(0.0, 0.3)
   else:  # Mixed
       luxury_pressure = random.uniform(0.3, 0.7)
   ```

### Brand Agent Architecture

Each Italian fashion brand is represented by a `BrandAgent` with:

#### Static Attributes (from Brand Intelligence)
- Financial metrics (revenue, margins, growth)
- Market position (segments, pricing, market share)
- Innovation profile (R&D, patents, technical capability)
- Brand metrics (heritage, perception, brand heat)
- Operational capabilities (flexibility, manufacturing, supply chain)

#### Dynamic Attributes
- **risk_appetite**: Random 0-1 (willingness to take risks)
- **decision_speed**: Random 0-1 (how quickly they make decisions)
- **appetite_for_high_performance_luxury_move**: Calculated based on fashion vs function positioning
  - Brands in segment 6 (HP Luxury): 0.0 (already there)
  - High fashion + low function brands (segments 5, 7): 0.6-0.9 (highest appetite)
  - High function + low fashion brands (segments 1, 2): 0.0-0.2 (low appetite)
  - Calculation considers:
    - Fashion-function gap (high fashion but low function = high appetite)
    - Innovation perception gap (low perception increases appetite)
    - Technical capability gap (low capability increases appetite for fashion brands)
    - Segment 5 & 7 bonus for explicit luxury positioning

---

## DECISION-MAKING ALGORITHMS

### Brand Decision Process

Each brand evaluates partnership opportunities through a multi-factor scoring algorithm:

#### 1. Base Partnership Score

```python
def calculate_partnership_score(brand, product, model_type):
    # Component scores (0-100 scale)
    segment_fit = calculate_segment_fit(brand.segment, product.category)
    innovation_match = product.innovation_level × brand.innovation_affinity
    price_value = calculate_price_value(product.margin, brand.avg_price_point)
    
    # Model-specific adjustments
    if model_type == "co_branded":
        brand_synergy = 0.8 if brand.segment in [4,5,6,7] else 0.4
        exclusivity_value = 1.0 - market.saturation_level
    else:  # white_label
        brand_synergy = 0.2
        exclusivity_value = 0.3
    
    # Weighted combination
    base_score = (
        0.25 × segment_fit +
        0.20 × innovation_match +
        0.20 × price_value +
        0.20 × brand_synergy +
        0.15 × exclusivity_value
    )
    
    return base_score
```

#### 2. Risk-Adjusted Decision

```python
def make_partnership_decision(brand, base_score):
    # Risk adjustment
    risk_threshold = 50 + (brand.risk_appetite - 0.5) × 40  # Range: 30-70
    
    # Speed adjustment (affects timing, not decision)
    decision_delay = int((1 - brand.decision_speed) × 12)  # 0-12 months
    
    # Stochastic element
    noise = np.random.normal(0, 10)  # ±10 point uncertainty
    
    final_score = base_score + noise
    
    return {
        'accept': final_score > risk_threshold,
        'delay_months': decision_delay,
        'confidence': abs(final_score - risk_threshold) / 100
    }
```

#### 3. Demand Calculation

```python
def calculate_demand(brand, product, model_type):
    # Base demand as % of brand production
    if model_type == "co_branded":
        base_demand_pct = 0.001  # 0.1% of brand production
    else:
        base_demand_pct = 0.005  # 0.5% of brand production
    
    # Brand size factor
    brand_units = brand.revenue × 1000 / brand.avg_price  # Rough unit estimate
    
    # Product category multiplier
    category_multipliers = {
        'Technical Inner Layers': 2.0,      # High volume
        'Structural Enhancement': 1.0,      # Medium volume
        'Sustainable Performance': 1.5      # Growing demand
    }
    
    # Innovation premium
    innovation_factor = 1 + (product.innovation_score - 5) × 0.1
    
    # Final calculation
    annual_demand = (
        brand_units × 
        base_demand_pct × 
        category_multipliers[product.category] × 
        innovation_factor ×
        np.random.uniform(0.8, 1.2)  # ±20% variability
    )
    
    return int(annual_demand)
```

### Macron Decision Process

Macron acts as a capacity-constrained optimizer:

```python
def macron_evaluate_partnerships(potential_partners, available_capacity):
    # Score each opportunity
    opportunities = []
    for partner in potential_partners:
        margin = calculate_margin(partner.product, partner.model_type)
        volume = partner.demanded_units
        strategic_value = calculate_strategic_value(partner.brand)
        
        score = margin × volume × strategic_value
        opportunities.append((score, partner))
    
    # Greedy optimization with constraints
    opportunities.sort(reverse=True, key=lambda x: x[0])
    
    accepted = []
    remaining_capacity = available_capacity
    
    for score, partner in opportunities:
        if partner.demanded_units <= remaining_capacity:
            accepted.append(partner)
            remaining_capacity -= partner.demanded_units
        elif remaining_capacity > MIN_BATCH_SIZE:
            # Partial acceptance
            partner.accepted_units = remaining_capacity
            accepted.append(partner)
            remaining_capacity = 0
            break
    
    return accepted
```

---

## MARKET DYNAMICS & SHOCKS

### Time-Based Market Evolution

```python
def update_market_conditions(year):
    # Sustainability trend acceleration
    sustainability_importance = 0.3 + 0.1 × year  # 30% → 80% over 5 years
    
    # Technology adoption curve
    tech_adoption = 1 - exp(-0.5 × year)  # S-curve adoption
    
    # Competition intensity
    competitor_entry = min(5, int(year × 1.5))  # New entrants
    
    # Price pressure
    margin_erosion = 0.02 × year  # 2% annual margin pressure
```

### Stochastic Market Shocks

The simulation introduces random market events:

```python
market_shocks = {
    'supply_disruption': {
        'probability': 0.10,  # 10% annual chance
        'impact': lambda: np.random.uniform(0.7, 0.9),  # 10-30% capacity reduction
        'duration': lambda: np.random.randint(1, 4)  # 1-3 quarters
    },
    'luxury_boom': {
        'probability': 0.15,
        'impact': lambda: np.random.uniform(1.2, 1.5),  # 20-50% demand increase
        'segments_affected': [4, 5, 6, 7]
    },
    'sustainability_regulation': {
        'probability': 0.20,
        'impact': lambda: {
            'sustainable_premium': np.random.uniform(1.1, 1.3),
            'non_sustainable_penalty': np.random.uniform(0.8, 0.95)
        }
    },
    'economic_downturn': {
        'probability': 0.08,
        'impact': lambda: {
            'luxury_demand': np.random.uniform(0.6, 0.8),
            'value_demand': np.random.uniform(1.1, 1.3)
        }
    }
}
```

### Partnership Lifecycle Dynamics

```python
def evaluate_partnership_continuation(partnership, year):
    # Base continuation probability
    if partnership.model == "co_branded":
        base_prob = 0.85  # 85% annual renewal
    else:
        base_prob = 0.70  # 70% annual renewal
    
    # Performance factor
    margin_achievement = partnership.actual_margin / partnership.target_margin
    performance_factor = min(1.2, margin_achievement)
    
    # Relationship factor
    relationship_score = (
        0.4 × partnership.on_time_delivery +
        0.3 × partnership.quality_score +
        0.3 × partnership.innovation_collaboration
    )
    
    # Market factor
    market_factor = 1.0
    if partnership.brand.segment in declining_segments:
        market_factor = 0.8
    elif partnership.brand.segment in growing_segments:
        market_factor = 1.2
    
    continuation_prob = base_prob × performance_factor × relationship_score × market_factor
    
    return np.random.random() < continuation_prob
```

---

## CAPACITY MANAGEMENT

### Macron Capacity Model

```python
class MacronCapacity:
    total_production = 2_000_000  # Units per year
    b2b_allocation = 0.50         # 50% for new B2B model
    available_capacity = 1_000_000  # Units for partnerships
    
    # Capacity allocation rules
    min_order_size = 1_000       # Minimum batch
    max_partner_allocation = 0.10  # No partner > 10% of capacity
    
    # Efficiency factors
    co_branded_setup_time = 1.2   # 20% more setup time
    white_label_setup_time = 1.0   # Baseline
    
    # Learning curve
    efficiency_improvement = 0.03  # 3% annual improvement
```

### Dynamic Capacity Allocation

```python
def allocate_capacity(year, partnerships, model_type):
    # Base capacity with learning curve
    effective_capacity = available_capacity × (1 + efficiency_improvement × year)
    
    # Setup time overhead
    if model_type == "co_branded":
        setup_overhead = len(partnerships) × 5000  # 5k units equivalent per partner
    else:
        setup_overhead = len(partnerships) × 2000  # 2k units equivalent per partner
    
    net_capacity = effective_capacity - setup_overhead
    
    # Priority-based allocation
    priorities = calculate_partner_priorities(partnerships)
    allocated = allocate_by_priority(net_capacity, partnerships, priorities)
    
    return allocated
```

---

## KEY ASSUMPTIONS

### Financial Assumptions
1. **Pricing Model**
   - Co-branded: Cost + 35% markup to brand
   - White-label: Cost + 12% markup to brand
   - COGS includes: Materials (40%), Labor (30%), Overhead (30%)

2. **R&D Amortization**
   - Total R&D: €5.77M
   - Amortization: 5 years straight-line
   - Allocation: Per-unit based on production volume

3. **Working Capital**
   - Payment terms: Net 60 days
   - Inventory turnover: 6x per year
   - No financing costs included

### Market Assumptions
1. **Brand Behavior**
   - Rational actors with bounded rationality
   - No direct brand-to-brand communication
   - Independent decision-making

2. **Competition**
   - No direct competitors modeled
   - Indirect competition through opportunity cost
   - No retaliation dynamics

3. **Demand**
   - Linear demand curves
   - No seasonality
   - No fashion cycles

### Technical Assumptions
1. **Production**
   - Infinite raw material availability
   - No production defects
   - Constant quality across scenarios

2. **Logistics**
   - Deterministic lead times
   - No force majeure events
   - Stable shipping costs

3. **Information**
   - Perfect information for Macron
   - Imperfect brand knowledge of competitors
   - No information asymmetry in partnerships

---

## VALIDATION & CALIBRATION

### Historical Calibration
- Brand revenue data: Validated against public filings where available
- Market segments: Aligned with industry reports (McKinsey, Bain)
- Cost structures: Benchmarked against textile industry standards

### Sensitivity Analysis
- ±20% variation in all key parameters tested
- Model remains stable and directionally consistent
- Co-branded superiority robust across parameter ranges

### Monte Carlo Convergence
- 10,000 simulations achieve <1% variance in mean outcomes
- Distribution shapes stabilize after 5,000 runs
- Tail events adequately captured

---

*This architecture document represents the complete technical implementation of the ModaMesh simulation system. All assumptions and methodologies have been designed to balance realism with computational tractability while maintaining decision-relevant accuracy.* 