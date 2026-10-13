# 🌍 MacroPulse: Econometric Intelligence & Macro Analytics Engine

[![CI Pipeline](https://github.com/usufalbaz/gdp-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/usufalbaz/gdp-dashboard/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gdp-dashboard-ffnsmh66vcaoryqnqt5bna.streamlit.app/)

MacroPulse is a high-performance quantitative macroeconomic intelligence engine. Built with clean-layered Python architecture, it normalizes multi-decade time-series records, evaluates macroeconomic momentum, scores volatility regimes, and provides dynamic integration with the World Bank Open Data REST API.

---

## 🚀 Key Modules & Capabilities

* **Decoupled Quantitative Engine (src/core/metrics.py):** Pure numerical algorithms calculating Compound Annual Growth Rate (CAGR), rolling standard deviation (macro volatility proxy), and YoY percentage deltas with mathematical boundary guards (NaN, zero, negative checks).
* **Fault-Tolerant Data Pipeline (src/pipeline/loader.py):** Dynamic wide-to-long matrix melting, schema enforcement, and type casting into structured columnar records.
* **Resilient World Bank Client (src/pipeline/world_bank.py):** Dedicated, zero-dependency REST client querying World Bank endpoints directly with automatic error recovery and payload normalization.
* **Dynamic Temporal Horizon:** Automated sliding time-window scaling dynamically up to the current calendar year.
* **Continuous Integration & Testing (tests/):** Automated test coverage via Pytest with parametrized edge-case boundary validations on every commit.

---

## 📂 Repository Directory Tree

gdp-dashboard/
├── .github/
│   ├── workflows/
│   │   └── ci.yml                 # Automated matrix test runner
│   └── CODEOWNERS                 # Maintainer governance
├── data/
│   └── gdp_data.csv               # Historical World Bank benchmark records
├── src/
│   ├── core/
│   │   └── metrics.py             # Econometric pure mathematical functions
│   └── pipeline/
│       ├── loader.py              # Time-series normalization pipeline
│       └── world_bank.py          # World Bank live REST API client
├── tests/
│   ├── test_data_processing.py    # Core math & pipeline integration tests
│   └── test_world_bank.py         # REST client schema & network tests
├── streamlit_app.py               # Controller & interactive UI dashboard
├── requirements.txt               # Pin-bounded dependencies
└── README.md

---

## 🛠️ Local Installation & Development

1. Clone the repository:
   git clone https://github.com/usufalbaz/gdp-dashboard.git
   cd gdp-dashboard

2. Configure virtual environment:
   python -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run the automated test suite:
   pytest tests/

5. Launch the platform:
   streamlit run streamlit_app.py

---

## 📄 License

Distributed under the Apache License 2.0. See LICENSE for details.
