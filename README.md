DCF Valuation Model with Monte Carlo Sensitivity

This project implements the Discounted Cash Flow (DCF) model, a core tool in corporate finance, to estimate a company's intrinsic equity value. The model is enhanced with Monte Carlo simulation for robust sensitivity analysis.

Advanced Features:

Two-Stage Growth Model: FCF projection uses distinct growth rates, reflecting an initial high-growth period followed by maturation.

Monte Carlo Sensitivity Analysis: The model uses Monte Carlo simulation to quantify risk and uncertainty in key valuation parameters (WACC and long-term growth 'g'). This yields a range of fair values rather than a single deterministic price.

Visualization: Generates a histogram using Matplotlib to display the distribution of simulated share values.

Skills Demonstrated:

Quantitative Finance: Application of stochastic modeling (Monte Carlo) to measure valuation risk.

Corporate Finance: Application of DCF, Net Present Value (NPV), Free Cash Flow (FCF), and Weighted Average Cost of Capital (WACC).

Software Engineering: Modular class design and efficient use of Python libraries for numerical computing and data visualization.

Repository Structure

File

Description

dcf_model.py

Contains the core logic: FCF projection, Terminal Value calculation, and the Monte Carlo engine.

main.py

Entry point script that defines parameters (deterministic and distribution inputs) and executes the model.

requirements.txt

Lists Python library dependencies.

README.md

This document.

Project Setup

Clone the Repository:

git clone [Your Repository URL]


Dependencies:
Install required libraries from the Canvas file requirements.txt:

pip install -r requirements.txt


Execution:
Run the main script to perform the deterministic valuation and the Monte Carlo simulation:

python main.py


Model Inputs

The model requires defining key financial inputs for both the base case and the risk analysis:

Deterministic Case Inputs

Initial Free Cash Flow (FCF): Last year's FCF.

Explicit Growth Rates: Specific growth rates for the explicit projection period (e.g., Year 1-2 vs. Year 3-5).

WACC (Base): Weighted Average Cost of Capital used for discounting.

Long-Term Growth (g Base): Growth rate assumed for the perpetuity calculation.

Net Debt & Shares Outstanding: Used to derive the final Fair Value Per Share.

Sensitivity Analysis (Monte Carlo)

WACC Mean / WACC StDev: Mean and Standard Deviation for the WACC distribution.

G Mean / G StDev: Mean and Standard Deviation for the Long-Term Growth rate distribution.

Valuation Methodology

The model provides two outputs:

Deterministic Value (Base Case): Calculates a single, implied share price based on the fixed average inputs.

Stochastic Value (Monte Carlo): Runs thousands of scenarios by sampling WACC and 'g' from normal distributions. This provides:

Mean and Median Valuation: The expected value and central tendency.

Standard Deviation: A measure of the valuation's inherent risk.

Confidence Intervals: A range of expected fair values (e.g., 95% C.I.).