# CCJ Detention Facility Analysis Platform

A comprehensive data analysis and visualization platform for evaluating the Marginal Value of Public Funds (MVPF) for detention policies using economic frameworks and interactive dashboards.

## 📋 Overview

This project provides tools for analyzing detention facility policies through:

1. **MVPF Calculator** - Economic framework for evaluating detention policy costs and benefits across multiple scenarios
2. **Interactive Dashboard** - Plotly Dash application with real-time parameter adjustment and visualization
3. **Scenario Analysis** - Compare baseline, reform, and expansion scenarios with configurable parameters

Data and code to support the Cook County Jail project for the "Building Data Products for Public Impact" course (INFO 290, Fall 2025, UC Berkeley).


## 🔬 Methodology

### MVPF Framework

The MVPF calculator evaluates detention policies across three dimensions:

**Detainee Values** (negative impacts):
- Willingness to Pay for Freedom
- Incarceration-Related Harm
- Post-Release Effects

**Society Values** (benefits):
- Crime Prevention/Displacement
- Victimization Cost Reduction
- Community & Economic Spillovers

**Government Costs**:
- Facility Operations
- Healthcare Services
- Processing & Management

**Formula:**
```
MVPF = (Detainee Values + Society Values) / Government Costs
```

**Interpretation:**
- MVPF > 1: Benefits exceed costs
- MVPF = 1: Benefits equal costs
- MVPF < 1: Costs exceed benefits

## 📈 Key Features

### MVPF Calculator Capabilities
- **Multiple Scenarios**: Baseline, conservative/least conservative, reform programs, capacity expansion
- **CSV-Driven Configuration**: Parameters and subcomponent values loaded from data files
- **CPI Adjustment**: Automatic inflation adjustment for monetary values
- **Component Registry**: Modular subcomponent system for detainee values, society values, and government costs
- **Scenario Management**: JSON-based scenario definitions with component selection and parameter overrides

### Dashboard Features
- **Interactive Parameter Controls**: CSV-driven dropdowns for felony rate, length of stay, population size
- **Real-Time Calculation**: Instant MVPF recalculation as parameters change
- **Component Breakdown**: Detailed visualization of detainee, society, and government cost components
- **Scenario Comparison**: Compare baseline against alternative policy scenarios
- **Benchmark Comparisons**: View MVPF against other public policy interventions

## 🔧 Available Scenarios

The platform includes the following pre-configured scenarios:

- **Baseline**: Current operations with neutral parameters
- **Conservative Approach**: Focus on government costs and limited societal benefits
- **Least Conservative Approach**: Emphasizing detainee and societal benefits
- **Reduced Crime Scenario**: Increased societal benefits from crime reduction
- **Increased Crime Scenario**: Decreased societal benefits from capacity reductions
- **Pre-Trial Diversion Program**: Reduced detention through community programs
- **Bail Reform**: Reduced pre-trial detention via bail reform
- **Facility Capacity Expansion**: Increased capacity to handle larger population

### Key Parameters

Dashboard parameters are CSV-driven with dropdown options:
- **Felony Rate**: Below average / Average / Above average
- **Length of Stay**: Short (days) / Average / Long (days)
- **Detainee Population Multiplier**: Adjusts total affected population
- **Society Size Multiplier**: Adjusts community impact scale


## 🚀 Getting Started

### Running the Dashboard

```bash
python Dashboard.py
```

Then open your browser to `http://localhost:8050`

## 📁 Project Structure

```
CCJ/
├── Dashboard.py               # Main Plotly Dash application
├── mvpf_calculator.py         # Core MVPF calculation engine
├── parameters.py              # Parameter registry and management
├── scenarios.py               # Scenario management system
├── subcomponents.py           # Subcomponent registry
├── content_loader.py          # Content management
├── graphs.py                  # Visualization helpers
├── helpers.py                 # Utility functions
├── cpi_adjuster.py            # CPI inflation adjustment
├── Data/
│   ├── subcomponent_values.csv      # Component cost/benefit values
│   ├── parameter_values.csv         # Parameter definitions
│   ├── parameter_mapping.csv        # Parameter-to-component mapping
│   ├── alternative_calculations.json # Scenario definitions
│   ├── mvpf_comparisons.csv         # Benchmark comparisons
│   └── CPI.csv                      # CPI adjustment data
└── Content/                   # Dashboard content and descriptions
```

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- Enhanced temporal validation of various detention facilities across the US
- Additional MVPF components
- Dashboard improvements
- Documentation and examples

## 🙏 Acknowledgments

- Research on detention facility length of stay prediction
- MVPF methodology and economic evaluation frameworks
- Plotly Dash for visualization capabilities

---

**Note**: This is a research tool for policy analysis. Results should be interpreted carefully with domain expertise and validated with subject matter experts before use in decision-making.