# CCJ Detention Facility Analysis Platform

A comprehensive data analysis and visualization platform for evaluating the Marginal Value of Public Funds (MVPF) for detention policies using economic frameworks and interactive dashboards.

## 📋 Overview

This project provides tools for analyzing detention facility policies through:

1. **MVPF Calculator** - Economic framework for evaluating detention policy costs and benefits across multiple scenarios
2. **Interactive Dashboard** - Plotly Dash application with real-time parameter adjustment and visualization
3. **Scenario Analysis** - Compare baseline, reform, and expansion scenarios with configurable parameters
4. **Benchmark Comparisons** - Compare results with other MVPF-based policies and interventions

Data tool for Cook County Jail was developed as part of the 'Building Data Products for Public Impact' clinic led by Diag Davenport at the University of California, Berkeley. 
It is intended to support evidence-based policymaking and research on criminal justice reform. We gratefully acknowledge the contributions of researchers, data scientists, and policy experts who made this work possible.


## 🔬 Methodology

### MVPF Framework

The MVPF calculator evaluates detention policies across three dimensions:

**Detainee Values** (negative impacts):
- Willingness to Pay for Freedom
- Incarceration-Related Harm

**Society Values** (benefits):
- Crime Prevention/Displacement
- Court appearance
- Community & Economic Spillovers

**Government Costs**:
- Facility Operations
- Crime effect-based changes

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
- **CPI Adjustment**: Automatic inflation adjustment for monetary values (2011-2025)
- **Component Registry**: Modular subcomponent system for detainee values, society values, and government costs
- **Scenario Management**: JSON-based scenario definitions with component selection and parameter overrides
- **Parameter Effects Registry**: Centralized mapping of which parameters affect which subcomponents

### Dashboard Features
- **Interactive Parameter Controls**: CSV-driven dropdowns for felony rate, length of stay, population size, crime effect
- **Real-Time Calculation**: Instant MVPF recalculation as parameters change
- **Component Breakdown**: Detailed visualization of detainee, society, and government cost components
- **Scenario Comparison**: Compare baseline against alternative policy scenarios side-by-side
- **Benchmark Comparisons**: View MVPF against other public policy interventions
- **Sensitivity Analysis**: Interactive charts showing how MVPF changes across parameter ranges
- **Data Export**: Download calculation results as CSV for further analysis

### Architecture
- **Modular Design**: Separated concerns across specialized modules
  - `mvpf_calculator.py`: Core calculation engine
  - `parameters.py`: Parameter definitions and effects registry
  - `scenarios.py`: Scenario management system
  - `subcomponents.py`: Component value registry and calculations
  - `formatting.py`: Centralized styling and color definitions
  - `graphs.py`: Chart and visualization generation
  - `helpers.py`: Utility functions for dashboard operations
  - `constants.py`: Application-wide constants and thresholds

## 🔧 Available Scenarios

The platform includes the following pre-configured scenarios:

- **Baseline**: Current operations with neutral parameters
- **Conservative Approach**: Focus on government costs and limited societal benefits
- **Least Conservative Approach**: Emphasizing detainee and societal benefits


### Key Parameters

Dashboard parameters are CSV-driven with dropdown options:
- **Felony Rate**: 10-100%
- **Length of Stay**: 1 to 365 days
- **Detainee Population Multiplier**: Adjusts total affected population
- **Crime Effect**: Adjusts the assumed impact of detention on future crime rate of detainees.


## 🚀 Getting Started

### Installation
```bash
# Clone repository
git clone <repository-url>
cd CCJ

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python Dashboard.py
```

The dashboard will be available at `http://localhost:8050`

### Project Structure
```
CCJ/
├── Dashboard.py              # Main dashboard application
├── mvpf_calculator.py        # Core MVPF calculation engine
├── parameters.py             # Parameter definitions and registry
├── scenarios.py              # Scenario management
├── subcomponents.py          # Component value calculations
├── formatting.py             # Styling constants and formatters
├── graphs.py                 # Chart generation functions
├── helpers.py                # Utility functions
├── constants.py              # Application constants
├── cpi_adjuster.py          # CPI inflation adjustment
├── content_loader.py         # Content management
└── Data/                     # CSV data files and configurations
    ├── subcomponent_values.csv
    ├── alternative_calculations.json
    ├── mvpf_comparisons.csv
    └── cpi_data.csv
```

### Key Modules

**MVPFCalculator** (`mvpf_calculator.py`)
- Main calculation engine for MVPF scores
- Scenario-based calculations with parameter overrides
- Component-level breakdown and analysis

**ParameterRegistry** (`parameters.py`)
- Centralized parameter definitions with bounds and validation
- Parameter effects mapping (which parameters affect which components)
- CSV-driven parameter configuration

**Dashboard** (`Dashboard.py`)
- Plotly Dash interactive web application
- Real-time parameter adjustment and visualization
- Multiple analysis views (KPI, scenarios, benchmarks, sensitivity)

##  Acknowledgments

- We acknowledge the foundational research in criminal justice, welfare economics, and public policy that informs our methodology.
- We thank Cook County government agencies for providing access to administrative data and operational information.
- This project also benefited from open-source software tools and libraries that enable interactive data visualization and analysis.

---

**Disclaimer**: This is a research tool for policy analysis. Results should be interpreted carefully with domain expertise and validated with subject matter experts before use in decision-making.
The views and findings presented in this tool are those of the authors and do not necessarily reflect the official positions or policies of Cook County government, funding organizations, or affiliated institutions. All estimates should be interpreted as analytical tools to inform discussion rather than definitive policy prescriptions.