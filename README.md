## DCF Valuation Model with Monte Carlo Sensitivity

This project implements the **Discounted Cash Flow (DCF)** model — a core tool in corporate finance — to estimate a company's intrinsic equity value.  
The model is enhanced with **Monte Carlo simulation** for robust sensitivity analysis.

The project features a minimalist, interactive **web application built with Streamlit**, allowing users to adjust all financial and risk inputs in real time.

---

### Advanced Features

- **Interactive Web Interface (Streamlit):**  
  Simplifies input and provides immediate visualization of results.

- **Two-Stage Growth Model:**  
  FCF projection uses distinct growth rates, reflecting an initial high-growth period followed by maturation.

- **Monte Carlo Sensitivity Analysis:**  
  Quantifies risk and uncertainty in key valuation parameters (WACC and long-term growth *g*), yielding a range of fair values rather than a single deterministic price.

- **Risk Indicator:**  
  A color-coded indicator displays the overall risk (Standard Deviation / Mean) of the Monte Carlo simulation.

- **Visualization:**  
  Generates a histogram using Matplotlib to display the distribution of simulated share values.

---

### Skills Demonstrated

- **Quantitative Finance:** Application of stochastic modeling (Monte Carlo) to measure valuation risk.  
- **Corporate Finance:** Application of DCF, Net Present Value (NPV), Free Cash Flow (FCF), and Weighted Average Cost of Capital (WACC).  
- **Software Engineering:** Modular class design and efficient deployment using Streamlit and Python libraries for numerical computing and data visualization.

---

### Repository Structure

| File | Description |
|------|--------------|
| `dcf_model.py` | Contains the core valuation logic: FCF projection, Terminal Value calculation, and the Monte Carlo engine. This file handles the math. |
| `dcf_app_minimal.py` | Main entry point for the web application. Handles all user input (sidebar sliders) and result presentation via Streamlit. |
| `requirements.txt` | Lists Python library dependencies, including Streamlit, NumPy, and Matplotlib. |
| `README.md` | This document. |

---

### Project Setup

**1) Clone the Repository**

git clone [Your Repository URL]  
cd Company-Valuation-DCF

**2) Install Dependencies**

Install required libraries from the `requirements.txt` file.  
Note that Streamlit is now required.

pip install -r requirements.txt

**3) Run the Web Application**

Run the interactive Streamlit application using the following command:

streamlit run dcf_app_minimal.py

This will launch the application in your default web browser, allowing you to interact with the model via the sidebar inputs.

---

### Valuation Outputs

The application presents two primary outputs for a robust financial analysis:

- **Deterministic Value (Base Case):**  
  Calculates a single, implied share price based on the user's fixed mean inputs.

- **Stochastic Value (Monte Carlo):**  
  Runs thousands of scenarios, providing a comprehensive risk profile:
  - **Average Valuation:** The expected value from all simulations.  
  - **Standard Deviation:** A measure of the valuation's inherent risk.  
  - **Confidence Range:** A range of expected fair values (e.g., 95% C.I.).
