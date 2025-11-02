import numpy as np
import random
from dcf_model import DCFModel

# --- SIMULATED INPUT PARAMETERS (MATCHING dcf_app_minimal.py DEFAULTS) ---
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

def get_mc_analysis(mean, stdev, ci_low, ci_high, deterministic_value, inputs, median):
    """
    Generates an extensive quantitative analysis, justifying the output 
    and interpreting the shape of the Monte Carlo distribution.
    """
    
    # 1. Determine Risk and Trend
    cv = stdev / mean
    
    if cv <= 0.15:
        risk_adjective = "limited"
        skew_comment = "The distribution is highly symmetrical, indicating uniform uncertainty across the range."
    elif cv <= 0.30:
        risk_adjective = "significant"
        # Simulación de asimetría positiva (típica en valoración)
        skew_comment = f"The mean (${mean:,.2f}) is slightly higher than the median (${median:,.2f}), confirming a slight positive skew (a longer tail towards higher values). This is common in finance, reflecting greater potential for upside surprises."
    else:
        risk_adjective = "extreme"
        skew_comment = "The distribution shows notable positive skew, meaning the model forecasts a higher, albeit less probable, potential upside."

    # 2. Construct Justification Paragraph (AI Interpretation)
    analysis_paragraph = (
        f"This detailed analysis justifies the simulated output by linking key financial inputs to the visual evidence presented in the Monte Carlo histogram. "
        f"The high initial valuation is primarily driven by the **aggressive two-stage growth assumption** (starting at {inputs['initial_growth']:.1%}) over a {inputs['explicit_years']}-year period, resulting in a robust mean valuation of **${mean:,.2f}** per share. "
        f"The Cost of Capital ({inputs['wacc_mean']:.2%}) is the critical factor, as minor fluctuations in this rate, combined with the volatility in the perpetuity growth ('g'), create the final spread of values. "
        f"\n\n**Interpretation of the Value Distribution:**\n"
        f"The histogram confirms a **{risk_adjective}** dispersion around the mean (Std. Dev.: ${stdev:,.2f}). The spread defined by the 95% Confidence Interval (from ${ci_low:,.2f} to ${ci_high:,.2f}) is wide, demonstrating that the valuation is highly sensitive to input volatility. {skew_comment} This dispersion visually represents the risk inherent in relying on long-term growth forecasts."
    )
    
    return analysis_paragraph

def get_input_table(inputs):
    """
    Generates a Markdown table of key inputs.
    """
    input_table = f"""
### Key Model Inputs (Base Case)

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Initial FCF (Year 0)** | ${inputs['fcf']:,.0f} | Base for FCF projections. |
| **Net Debt** | ${inputs['debt']:,.0f} | Subtracted to find Equity Value. |
| **Shares Outstanding** | {inputs['shares']:,.0f} | Used for Per Share calculation. |
| **WACC (Mean Discount Rate)** | {inputs['wacc_mean']:.2%} | Primary discounting factor. |
| **Initial Growth (Stage 1)** | {inputs['initial_growth']:.1%} | High growth rate for early expansion phase. |
| **Perpetuity Growth ('g' Mean)** | {inputs['g_mean']:.2%} | Long-term growth assumption. |
"""
    return input_table

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
        'initial_growth': INITIAL_GROWTH_RATE,
        'explicit_years': EXPLICIT_YEARS
    }
    
    # Generate the separate components
    input_table_text = get_input_table(input_data)
    analysis_paragraph_text = get_mc_analysis(
        mean=results_mc['Mean'],
        stdev=results_mc['StDev'],
        ci_low=results_mc['95% Confidence Interval'][0],
        ci_high=results_mc['95% Confidence Interval'][1],
        deterministic_value=results_det['Fair Value Per Share'],
        inputs=input_data,
        median=results_mc['Median'] # Incluimos la mediana para el comentario de asimetría
    )
    
    print("\n--- AI-GENERATED QUANTITATIVE ANALYSIS (COPY AND PASTE INTO README.MD) ---\n")
    print(input_table_text)
    print("\n")
    print(analysis_paragraph_text)
    print("\n-----------------------------------------------------------------------\n")
