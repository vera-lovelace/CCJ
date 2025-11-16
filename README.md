# CCJ Detention Facility Analysis Platform

A comprehensive data analysis and visualization platform for understanding detention facility dynamics, predicting length of stay, and evaluating the Marginal Value of Public Funds (MVPF) for detention policies.

## 📋 Overview

This project provides tools for analyzing detention facility data with three main components:

1. **MVPF Calculator** - Economic framework for evaluating detention policy costs and benefits
2. **Interactive Dashboards** - Plotly Dash visualizations for exploring data and model results

## ✨ Features

### MVPF Calculator
- Calculate Marginal Value of Public Funds for detention policies
- Multi-component analysis (Detainee Values, Society Values, Government Costs)
- Scenario-based modeling with adjustable parameters
- CPI adjustment for inflation-adjusted calculations
- Flexible component selection and weighting

### Interactive Dashboards
- Real-time MVPF calculations with parameter adjustments
- Visual breakdowns of cost-benefit components
- Comparative scenario analysis
- Export capabilities for results and visualizations

## 🚀 Getting Started

### Running the Dashboard

```bash
python dashboard.py
```

Then open your browser to `http://localhost:8050`

## 📁 Project Structure

```
CCJ/
├── mvpf_package/
│   ├── __init__.py
│   ├── mvpf_calculation.py    # Core MVPF calculator
│   ├── content_loader.py      # Content management
│   ├── helpers.py             # Utility functions
│   └── graphs.py              # Visualization helpers
├── Data/
│   └── [CSV files]
├── dashboard.py               # Plotly Dash application
└── README.md
```

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
- Scenario-based analysis (baseline, optimal, enhanced)
- Parameter sensitivity testing
- Component-level breakdown
- CPI-adjusted calculations
- Batch processing for multiple scenarios

### Dashboard Features
- Real-time parameter adjustment
- Interactive visualizations
- Component drill-down
- Scenario comparison
- Export functionality

## 🔧 Configuration

### MVPF Parameters

Adjustable scenario parameters:
- `crime_rate_mult`: Crime rate multiplier (0.8 - 1.5)
- `detainee_pop_mult`: Population size multiplier (0.8 - 1.5)
- `community_size_mult`: Community impact multiplier (0.8 - 1.5)
- `length_of_stay_mult`: LoS duration multiplier (0.8 - 1.5)



## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- Additional ML algorithms (XGBoost Survival, Deep Learning)
- Enhanced temporal validation methods
- Additional MVPF components
- Dashboard improvements
- Documentation and examples

## 📝 Research Background

This project implements research-based approaches for detention facility analysis:

- **MVPF Framework**: Economic evaluation methodology for public policy

Key considerations:
- 70-day prediction window vs. full stay duration
- Time-based cross-validation strategies
- Feature availability at prediction time

Data and code to support the Cook County Jail project for the "Building Data Products for Public Impact" course (INFO 290, Fall 2025, UC Berkeley).

## 📄 License

This project is intended for research and policy analysis purposes.

## 📧 Contact

For questions or collaboration opportunities, please open an issue on GitHub.

## 🙏 Acknowledgments

- Research on detention facility length of stay prediction
- MVPF methodology and economic evaluation frameworks
- Plotly Dash for visualization capabilities

---

**Note**: This is a research tool for policy analysis. Results should be interpreted carefully with domain expertise and validated with subject matter experts before use in decision-making.