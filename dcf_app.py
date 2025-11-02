import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from dcf_model import DCFModel

# --- Configuration and Utility Functions ---

def get_mc_quality(mean: float, stdev: float) -> tuple[str, str]:
    """Determines the quality/risk level of the Monte Carlo simulation based on Std. Dev. relative to the Mean."""
    if mean == 0:
        return "N/A", "gray"
        
    cv = stdev / mean  # Coefficient of Variation (Risk relative to expected value)
    
    if cv <= 0.15:
        return "Low Risk (Good)", "green"
    elif cv <= 0.30:
        return "Moderate Risk (Fair)", "orange"
    else:
        return "High Risk (Poor)", "red"

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="DCF Valuation Model")

# --- 2. MAIN TITLE AND DESCRIPTION ---
st.title("DCF Valuation Model (Monte Carlo Sensitivity)")
st.markdown("A simple, two-stage Discounted Cash Flow (DCF) model incorporating Monte Carlo Simulation for robust risk analysis. Adjust all input parameters in the sidebar.")

# --- 3. INPUTS (SIDEBAR) ---
st.sidebar.header("1. Company Base Parameters")

# --- Absolute Value Inputs (NUEVOS VALORES REALISTAS) ---
fcf_year_0 = st.sidebar.number_input(
    "FCF Year 0 (USD):", 
    min_value=0.0, 
    value=150000000.0, # Adjusted value
    step=1000000.0, 
    format="%.0f",
    help="Latest reported Free Cash Flow. E.g., type 150000000 for $150 million."
)

net_debt = st.sidebar.number_input(
    "Net Debt (USD):", 
    min_value=0.0, 
    value=20000000.0, 
    step=1000000.0,
    format="%.0f",
    help="Total Debt minus Cash & Equivalents. E.g., type 20000000 for $20 million."
)

shares_outstanding = st.sidebar.number_input(
    "Shares Outstanding:", 
    min_value=100000.0, 
    value=25000000.0, # Adjusted value
    step=100000.0,
    format="%.0f",
    help="Total number of outstanding common shares."
)

explicit_years = st.sidebar.slider(
    "Explicit Forecast Years (T):", 
    min_value=3, 
    max_value=10, 
    value=5, 
    step=1
)

st.sidebar.header("2. Growth Assumptions (Two-Stage)")

# --- Deterministic Growth Inputs ---
initial_growth_rate = st.sidebar.slider(
    "Growth Rate (Stage 1: Years 1-2):", 
    min_value=0.0, max_value=0.25, 
    value=0.20, # Adjusted value
    step=0.01, 
    format="%.2f"
)

step_down_growth_rate = st.sidebar.slider(
    "Growth Rate (Stage 2: Years 3-T):", 
    min_value=0.0, max_value=0.15, 
    value=0.08, 
    step=0.01, 
    format="%.2f"
)

perpetuity_growth_g = st.sidebar.slider(
    "Perpetuity Growth Rate ('g'):", 
    min_value=0.01, max_value=0.05, 
    value=0.025, 
    step=0.001, 
    format="%.3f",
    help="Long-term growth rate used in the Terminal Value (Gordon Growth) calculation."
)

st.sidebar.header("3. Discount Rate & Monte Carlo")

# --- WACC and Monte Carlo Inputs ---
wacc_mean = st.sidebar.slider(
    "WACC (Mean Discount Rate):", 
    min_value=0.03, max_value=0.20, 
    value=0.100, # Adjusted value
    step=0.005, 
    format="%.3f",
    help="Weighted Average Cost of Capital, used as the discount rate."
)

st.sidebar.caption("Sensitivity Parameters (Risk)")

wacc_stdev = st.sidebar.slider(
    "WACC Standard Deviation (Volatility):", 
    min_value=0.001, max_value=0.03, 
    value=0.01, 
    step=0.001, 
    format="%.3f",
    help="Uncertainty (volatility) in the WACC."
)

g_stdev = st.sidebar.slider(
    "Perpetuity Growth 'g' Standard Deviation (Volatility):", 
    min_value=0.001, max_value=0.01, 
    value=0.005, 
    step=0.001, 
    format="%.3f",
    help="Uncertainty (volatility) in the long-term growth rate."
)

simulations = st.sidebar.slider(
    "Number of Simulations:", 
    min_value=1000, max_value=50000, 
    value=10000, 
    step=1000
)

# --- 4. EXECUTION OF THE MODEL ---
try:
    # Initialize Model
    dcf = DCFModel(
        initial_fcf=fcf_year_0, 
        net_debt=net_debt, 
        shares_outstanding=shares_outstanding,
        explicit_years=explicit_years
    )
    
    # Run Base Case Deterministic
    results_det = dcf.run_deterministic_valuation(
        wacc=wacc_mean,
        long_term_growth_rate=perpetuity_growth_g,
        initial_growth=initial_growth_rate,
        step_down_growth=step_down_growth_rate
    )

    # Run Monte Carlo Simulation
    results_mc = dcf.run_monte_carlo_sensitivity(
        wacc_mean=wacc_mean,
        wacc_stdev=wacc_stdev,
        g_mean=perpetuity_growth_g,
        g_stdev=g_stdev,
        initial_growth=initial_growth_rate,
        step_down_growth=step_down_growth_rate,
        simulations=simulations
    )

    # Prepare Results for Display
    results_display = dcf.print_results_monte_carlo(results_det, results_mc)
    
    # Get Risk Indicator for Monte Carlo
    quality_text, quality_color = get_mc_quality(results_display['MC_Mean'], results_display['MC_StDev'])

except Exception as e:
    st.error(f"Error during model execution. Please check the inputs.")
    st.info(f"Detail: {e}")
    st.stop()


# --- 5. DISPLAY RESULTS (MAIN PANEL) ---
st.header("Implied Valuation Results")

col_det, col_mc = st.columns(2)

# --- 5.1. Column 1: Base Case ---
with col_det:
    st.subheader("1. Base Case Value")
    
    st.metric(
        label="Implied Value Per Share (Deterministic)",
        value=f"${results_display['Deterministic_Value']:,.2f}",
        help=f"Calculated using fixed inputs: WACC ({wacc_mean:.1%}) and g ({perpetuity_growth_g:.1%}) as fixed inputs."
    )
    st.markdown("This is the result based on your median assumptions.")

# --- 5.2. Column 2: Monte Carlo Sensitivity ---
with col_mc:
    # Use Markdown/HTML to display the quality indicator next to the title
    st.markdown(f"**2. Monte Carlo Sensitivity** <span style='color:{quality_color}'>({quality_text})</span>", unsafe_allow_html=True)
    
    st.metric(
        label="Average Value Per Share (from Simulation)",
        value=f"${results_display['MC_Mean']:,.2f}",
        delta=f"Std. Dev. (Risk): ${results_display['MC_StDev']:,.2f}",
        delta_color="off",
        help="The mean of all simulated outcomes. The Std. Dev. reflects valuation uncertainty."
    )
    
    ci_low = results_display['MC_CI_Low']
    ci_high = results_display['MC_CI_High']
    
    st.success(
        f"95% Confidence Range: ${ci_low:,.2f} to ${ci_high:,.2f}"
    )
    
# --- 6. VISUALIZATION ---
st.markdown("---")
st.header("Value Distribution (Risk Profile)")

# --- GENERACIÓN DEL GRÁFICO ---

# Recrear la figura
fig, ax = plt.subplots(figsize=(10, 6))

# Usamos la data guardada en el objeto dcf para plotear
if len(dcf.simulated_per_share_values) > 0:
    ax.hist(dcf.simulated_per_share_values, bins=50, density=True, alpha=0.6, color='skyblue', edgecolor='black')
    
    mean_val = results_mc['Mean']
    median_val = results_mc['Median']
    
    # Lines are in English now
    ax.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Mean: ${mean_val:,.2f}')
    ax.axvline(median_val, color='green', linestyle='dashed', linewidth=2, label=f'Median: ${median_val:,.2f}')
    
    # --- AÑADIR CONTEXTO DE INPUTS DENTRO DEL ÁREA DE LOS EJES (ESTABLE) ---
    input_text = (
        f"Assumptions:\n"
        f"FCF (Y0): ${fcf_year_0/1e6:.0f}M | Shares: {shares_outstanding/1e6:.0f}M\n"
        f"WACC (Mean): {wacc_mean:.2%} | Growth (Stage 1): {initial_growth_rate:.1%}"
    )
    
    # Colocar el texto en la esquina superior derecha de la zona de trazado (ax.text)
    # xy=(0.95, 0.95) son coordenadas relativas a los ejes (no a la figura total)
    ax.text(0.95, 0.95, input_text, transform=ax.transAxes, 
             fontsize=10, verticalalignment='top', horizontalalignment='right', 
             bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.7))

    # Títulos y Ejes en inglés
    ax.set_title('Distribution of Implied Value Per Share (Monte Carlo Simulation)', fontsize=14)
    ax.set_xlabel('Value Per Share ($)', fontsize=12)
    ax.set_ylabel('Normalized Frequency', fontsize=12)
    ax.legend()
    ax.grid(axis='y', alpha=0.5)

# Guardar la figura y mostrarla
fig.savefig("monte_carlo_distribution.png", bbox_inches='tight')
st.pyplot(fig)


# --- 7. FOOTER TECHNICAL ---
st.markdown("---")
st.caption(f"Developed by Nuno Poza Quadros (Python/Streamlit). Executed with {results_mc['Count']:,} scenarios.")
