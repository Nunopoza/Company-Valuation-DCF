import numpy as np
import random
from dcf_model import DCFModel

# --- SIMULATED INPUT PARAMETERS (MATCHING dcf_app_minimal.py) ---
# Estos parámetros son los nuevos valores realistas para el análisis.
INITIAL_FCF = 150_000_000.0        
NET_DEBT = 20_000_000.0           
SHARES_OUTSTANDING = 25_000_000.0 
EXPLICIT_YEARS = 5                

INITIAL_GROWTH_RATE = 0.20        
STEP_DOWN_GROWTH_RATE = 0.08      

WACC_MEAN = 0.100                 
WACC_STDEV = 0.01                 
G_DETERMINISTIC = 0.025           
G_STDEV = 0.005                   

SIMULATIONS_COUNT = 10000

# --- UTILITY FUNCTION FOR ANALYSIS ---

def get_mc_analysis(mean, stdev, ci_low, ci_high, deterministic_value, inputs):
    """
    Generates a concise quantitative analysis, including a table of key inputs, 
    mimicking an AI interpreter for the README.md.
    """
    
    # 1. Determine Risk and Trend
    cv = stdev / mean
    
    if cv <= 0.15:
        risk_text = "low volatility (Low Risk)."
    elif cv <= 0.30:
        risk_text = "moderate volatility (Moderate Risk)."
    else:
        risk_text = "high volatility (Poor Risk)."

    trend = "very close to"
    if mean > deterministic_value * 1.05:
        trend = "higher than"
    elif mean < deterministic_value * 0.95:
        trend = "lower than"

    # 2. Construct Analysis Paragraph (AI Interpretation)
    analysis_paragraph = (
        f"This analysis interprets the simulated results, focusing on risk and valuation uncertainty. "
        f"The Monte Carlo simulation, using the inputs detailed below, resulted in an average expected intrinsic value (mean) of **${mean:,.2f}**. "
        f"This mean is **{trend}** the deterministic base case value, indicating that parameter uncertainty has a significant impact on the valuation's central tendency. "
        f"The Standard Deviation of **${stdev:,.2f}** confirms the valuation's {risk_text}. "
        f"The spread of the 95% Confidence Range, spanning from **${ci_low:,.2f} to ${ci_high:,.2f}**, illustrates the broad impact that small changes in WACC and perpetuity growth ('g') assumptions can have on the final price."
    )
    
    # 3. Construct Input Table (Markdown)
    input_table = f"""
### Key Model Inputs (Base Case)

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Initial FCF (Year 0)** | ${inputs['fcf']:,.0f} | Base for FCF projections. |
| **Net Debt** | ${inputs['debt']:,.0f} | Subtracted to find Equity Value. |
| **Shares Outstanding** | {inputs['shares']:,.0f} | Used for Per Share calculation. |
| **Initial Growth (Stage 1)** | {inputs['initial_growth']:.1%} | High growth rate for early expansion. |
| **WACC (Mean Discount Rate)** | {inputs['wacc_mean']:.2%} | Primary discounting factor. |
| **Perpetuity Growth ('g' Mean)** | {inputs['g_mean']:.2%} | Long-term growth assumption. |
"""

    return input_table + analysis_paragraph

# --- EXECUTION ---

if __name__ == "__main__":
    
    # Run a quick simulation to gather result metrics
    dcf = DCFModel(
        initial_fcf=INITIAL_FCF, 
        net_debt=NET_DEBT, 
        shares_outstanding=SHARES_OUTSTANDING,
        explicit_years=EXPLICIT_YEARS
    )
    
    results_det = dcf.run_deterministic_valuation(
        wacc=WACC_MEAN,
        long_term_growth_rate=G_DETERMINISTIC,
        initial_growth=INITIAL_GROWTH_RATE,
        step_down_growth=STEP_DOWN_GROWTH_RATE
    )

    results_mc = dcf.run_monte_carlo_sensitivity(
        wacc_mean=WACC_MEAN,
        wacc_stdev=WACC_STDEV,
        g_mean=G_DETERMINISTIC,
        g_stdev=G_STDEV,
        initial_growth=INITIAL_GROWTH_RATE,
        step_down_growth=STEP_DOWN_GROWTH_RATE,
        simulations=SIMULATIONS_COUNT
    )
    
    # Gather Input Data for Table
    input_data = {
        'fcf': INITIAL_FCF,
        'debt': NET_DEBT,
        'shares': SHARES_OUTSTANDING,
        'wacc_mean': WACC_MEAN,
        'g_mean': G_DETERMINISTIC,
        'initial_growth': INITIAL_GROWTH_RATE
    }
    
    # Get the analysis text
    analysis_text = get_mc_analysis(
        mean=results_mc['Mean'],
        stdev=results_mc['StDev'],
        ci_low=results_mc['95% Confidence Interval'][0],
        ci_high=results_mc['95% Confidence Interval'][1],
        deterministic_value=results_det['Fair Value Per Share'],
        inputs=input_data
    )
    
    print("\n--- AI-GENERATED QUANTITATIVE ANALYSIS (COPY AND PASTE INTO README.MD) ---\n")
    print(analysis_text)
    print("\n-----------------------------------------------------------------------\n")
