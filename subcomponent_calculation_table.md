# Subcomponent Calculation Comparison Table

This table shows the calculation logic for each subcomponent in the MVPF dashboard, including all parameters applied during calculation.

## Table Format
- **Base Value**: From `subcomponent_values.csv`
- **CPI Adjustment**: Applied to all dollar values (2025 adjustment ≈ 1.15x from base year)
- **Parameters**: Listed in order of application
- **Result**: Final calculated value

---

## DETAINEE VALUES

### 1. det_wtp_freedom (Willingness to Pay for Freedom)
**Base Value:** $11 per day (2022)
**Unit:** dollars per day
**Sign:** negative (harm to detainees)

**Parameters Applied:**
1. `los_days` - Length of stay (60-203 days, default: 70)
2. `n_detainees_mult` - Detainee population (33,945 × multiplier)

**Calculation Formula:**
```
det_wtp_freedom = $11 × CPI(2022→2025) × los_days × (33,945 × n_detainees_mult)
                = $11 × 1.10 × 70 × (33,945 × 1.0)
                = -$28,891,595
```

**Example with different parameters:**
- LOS = 203 days (above average)
- Population multiplier = 1.2 (above average)
```
det_wtp_freedom = $11 × 1.10 × 203 × (33,945 × 1.2)
                = -$100,223,238
```

---

### 2. det_rel_harm (Relative Harm Valuation - RHV)
**Base Value:** $295,275 per day (2021)
**Unit:** dollars per day
**Sign:** negative (harm to detainees)

**Parameters Applied:**
1. `los_days` - Length of stay (60-203 days, default: 70)
2. `n_detainees_mult` - Detainee population (33,945 × multiplier)

**Calculation Formula:**
```
det_rel_harm = $295,275 × CPI(2021→2025) × los_days × (33,945 × n_detainees_mult)
             = $295,275 × 1.15 × 70 × (33,945 × 1.0)
             = -$811,690,365,318
```

**⚠️ NOTE:** There is a known issue with this calculation. The base value ($295,275/day) may already include the aggregate across all detainees, causing double-counting when multiplied by n_detainees_mult. This results in an extremely large value. Consider whether n_detainees_mult should be removed or replaced with n_detainees_adj (adjustment only, no base).

**Alternative calculation (if base is aggregate):**
```
det_rel_harm = $295,275 × CPI(2021→2025) × los_days × n_detainees_adj
             = $295,275 × 1.15 × 70 × 1.0
             = -$23,897,363
```

---

## SOCIETY VALUES

### 3. soc_court (Court Appearance Effects)
**Base Value:** $12.60 per detainee (2020)
**Unit:** dollars per detainee
**Sign:** positive (benefit to society)

**Parameters Applied:**
1. `n_detainees_mult` - Detainee population (33,945 × multiplier)

**Calculation Formula:**
```
soc_court = $12.60 × CPI(2020→2025) × (33,945 × n_detainees_mult)
          = $12.60 × 1.13 × (33,945 × 1.0)
          = $483,677
```

---

### 4. soc_crime_prevention (Crime Prevention Benefits)
**Base Value:** $0 per detainee (2018)
**Unit:** dollars per detainee
**Sign:** positive (benefit to society)

**Parameters Applied:**
1. `n_detainees_mult` - Detainee population (33,945 × multiplier)
2. `fel_rate` - Felony rate (0.5-1.0, default: 0.7)

**Calculation Formula:**
```
soc_crime_prevention = $0 × CPI(2018→2025) × (33,945 × n_detainees_mult) × fel_rate
                     = $0 × 1.17 × (33,945 × 1.0) × 0.7
                     = $0
```

**Note:** Currently set to $0 in baseline. Can be adjusted to $133,685 (max) or $75,000 for sensitivity analysis.

---

### 5. soc_victimization (Victimization Costs)
**Base Value:** $875,000 per victim (2024)
**Unit:** dollar per victim
**Sign:** negative (cost to society)

**Parameters Applied:**
1. `fel_rate` - Felony rate (0.5-1.0, default: 0.7)

**Calculation Formula:**
```
soc_victimization = $875,000 × CPI(2024→2025) × fel_rate
                  = $875,000 × 1.03 × 0.7
                  = -$630,875
```

**Note:** This is a per-victim cost, NOT multiplied by detainee or society population.

---

### 6. soc_spillover (Community Spillover Effects)
**Base Value:** $294,728 per detainee (2023)
**Unit:** dollars per detainee
**Sign:** negative (cost to society)

**Parameters Applied:**
1. `n_detainees_mult` - Detainee population (33,945 × multiplier)
2. `n_society_adj` - Society adjustment only (0.8/1.0/1.2, no base 5,171,000)

**Calculation Formula:**
```
soc_spillover = $294,728 × CPI(2023→2025) × (33,945 × n_detainees_mult) × n_society_adj
              = $294,728 × 1.07 × (33,945 × 1.0) × 1.0
              = -$10,696,584,786
```

**Example with society adjustment:**
- Society multiplier = 1.2 (above average community impact)
```
soc_spillover = $294,728 × 1.07 × (33,945 × 1.0) × 1.2
              = -$12,835,901,743
```

---

## GOVERNMENT COSTS

### 7. gov_operations (Operational Costs)
**Base Value:** $448,677,628 per year (2018)
**Unit:** dollars per year
**Sign:** positive (cost to government)

**Parameters Applied:**
- **NONE** - Fixed cost, not scaled by any parameters

**Calculation Formula:**
```
gov_operations = $448,677,628 × CPI(2018→2025)
               = $448,677,628 × 1.17
               = $524,952,825
```

**Note:** This is the total annual funding for Cook County Jail, independent of detainee population or LOS.

---

### 8. gov_health (Post-Release Health Spending)
**Base Value:** $300 per detainee (2018)
**Unit:** dollar per detainee
**Sign:** positive (cost to government)

**Parameters Applied:**
1. `n_detainees_mult` - Detainee population (33,945 × multiplier)
2. `los_days` - Length of stay (60-203 days, default: 70)

**Calculation Formula:**
```
gov_health = $300 × CPI(2018→2025) × (33,945 × n_detainees_mult) × los_days
           = $300 × 1.17 × (33,945 × 1.0) × 70
           = $835,174,650
```

**Example with different parameters:**
- LOS = 60 days (below average)
- Population multiplier = 0.8 (below average)
```
gov_health = $300 × 1.17 × (33,945 × 0.8) × 60
           = $572,263,440
```

---

## SUMMARY TABLE

| Subcomponent | Base Value | CPI Year→2025 | Parameters | Baseline Result (approx) |
|--------------|------------|---------------|------------|--------------------------|
| **DETAINEE VALUES** | | | | |
| det_wtp_freedom | $11/day | 2022 (1.10x) | los_days, n_detainees_mult | -$28,891,595 |
| det_rel_harm | $295,275/day | 2021 (1.15x) | los_days, n_detainees_mult | -$811,690,365,318 ⚠️ |
| **SOCIETY VALUES** | | | | |
| soc_court | $12.60/detainee | 2020 (1.13x) | n_detainees_mult | $483,677 |
| soc_crime_prevention | $0/detainee | 2018 (1.17x) | n_detainees_mult, fel_rate | $0 |
| soc_victimization | $875,000/victim | 2024 (1.03x) | fel_rate | -$630,875 |
| soc_spillover | $294,728/detainee | 2023 (1.07x) | n_detainees_mult, n_society_adj | -$10,696,584,786 |
| **GOVERNMENT COSTS** | | | | |
| gov_operations | $448,677,628/year | 2018 (1.17x) | NONE | $524,952,825 |
| gov_health | $300/detainee | 2018 (1.17x) | n_detainees_mult, los_days | $835,174,650 |

---

## Parameter Definitions

### Population Parameters
- **n_detainees_mult**: Base (33,945) × multiplier (0.8/1.0/1.2)
  - Below: 33,945 × 0.8 = 27,156
  - Average: 33,945 × 1.0 = 33,945
  - Above: 33,945 × 1.2 = 40,734

- **n_detainees_adj**: Adjustment only (0.8/1.0/1.2), no base multiplication
  - Below: 0.8
  - Average: 1.0
  - Above: 1.2

- **n_society_mult**: Base (5,171,000) × multiplier (0.8/1.0/1.2)
  - Below: 5,171,000 × 0.8 = 4,136,800
  - Average: 5,171,000 × 1.0 = 5,171,000
  - Above: 5,171,000 × 1.2 = 6,205,200

- **n_society_adj**: Adjustment only (0.8/1.0/1.2), no base multiplication
  - Below: 0.8
  - Average: 1.0
  - Above: 1.2

### Other Parameters
- **los_days**: Length of stay in days
  - Below: 60 days
  - Average: 70 days
  - Above: 203 days

- **fel_rate**: Felony rate (proportion)
  - Below: 0.5 (50%)
  - Average: 0.7 (70%)
  - Above: 1.0 (100%)

- **crime_effect**: Crime impact multiplier
  - Large Decrease: -4
  - No Effect: 0
  - Moderate Increase: 5
  - Large Increase: 14
  - **Note:** Not yet applied to any subcomponents (to be added manually)

---

## Notes on CPI Adjustment

CPI adjustments are estimated based on typical annual inflation rates from the source year to 2025:
- 2024→2025: ~1.03x
- 2023→2025: ~1.07x
- 2022→2025: ~1.10x
- 2021→2025: ~1.15x
- 2020→2025: ~1.13x
- 2018→2025: ~1.17x

Actual CPI values should be verified with official Bureau of Labor Statistics data.

---

## Critical Issues Identified

1. **det_rel_harm** appears to be double-counting the detainee population, resulting in an unrealistically large value (-$811 billion). Review whether:
   - The base value already includes aggregate population
   - Should use `n_detainees_adj` instead of `n_detainees_mult`
   - Or if this is the intended calculation

2. **soc_crime_prevention** is currently set to $0, making it ineffective in the calculation. Consider using the max value ($133,685) or mid-range value ($75,000) for more realistic scenarios.

3. **crime_effect** parameter has been defined but not yet applied to any subcomponents. Manual integration needed.