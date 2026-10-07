# 🌍 Global GDP Analytics Engine

[![CI Pipeline](https://github.com/usufalbaz/gdp-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/usufalbaz/gdp-dashboard/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An interactive, high-performance macroeconomic data analytics platform for longitudinal GDP comparison and growth rate profiling across 200+ nations (World Bank Dataset 1960–2022).

---

## 🚀 Key Features

* **Time-Series Normalization:** Dynamic melting and type-casting of unnormalized World Bank matrix datasets into high-efficiency columnar time-series records.
* **Compound Annual Growth Rate (CAGR) Engine:** Automated multi-decade growth benchmarking with mathematical boundary checks.
* **Interactive Data Visualization:** Multi-tenant country comparison charts built with Plotly Express.
* **Continuous Integration:** Fully automated Pytest test suites validating financial calculations and schema sanity on every commit.

---

## 🛠️ Tech Stack

* **Runtime:** Python 3.11
* **Framework:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly Express
* **Testing & CI:** Pytest, GitHub Actions

---

## 📦 Local Installation & Setup

1. Clone the repository:
    git clone https://github.com/usufalbaz/gdp-dashboard.git
    cd gdp-dashboard

2. Create a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
    pip install -r requirements.txt

4. Run the automated test suite:
    pytest tests/

5. Launch the dashboard:
    streamlit run streamlit_app.py

---

## 📄 License

Distributed under the Apache License 2.0. See LICENSE for details.
