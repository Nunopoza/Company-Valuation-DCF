# Este archivo sirve como un punto de entrada para demostrar el uso de la clase DCFModel avanzada.

from dcf_model import DCFModel

# --- 1. Definición de Parámetros de la Empresa ---
# Los valores simulan una empresa de tamaño medio para el ejemplo.
INITIAL_FCF = 50_000_000.0        # $50,000,000 (Flujo de Caja Libre del Año 0)
NET_DEBT = 20_000_000.0           # $20,000,000 (Deuda Neta)
SHARES_OUTSTANDING = 10_000_000.0 # 10,000,000 (Acciones en Circulación)
EXPLICIT_YEARS = 5                # 5 Años de Proyección Explícita

# --- 2. Parámetros Determinísticos (Caso Base) ---
# Tasa de crecimiento para la Etapa 1 (ej. Años 1-2)
INITIAL_GROWTH_RATE = 0.15 # 15%
# Tasa de crecimiento para la Etapa 2 (ej. Años 3-5)
STEP_DOWN_GROWTH_RATE = 0.08 # 8%

# Caso Base para el Descuento
WACC_DETERMINISTIC = 0.085    # 8.5%
G_DETERMINISTIC = 0.025       # 2.5% (Tasa de Crecimiento en Perpetuidad del caso base)

# --- 3. Parámetros para Simulación de Monte Carlo ---
# Distribución de la Tasa de Descuento (WACC)
WACC_MEAN = 0.085             # Media del WACC
WACC_STDEV = 0.01             # Desviación estándar del WACC (Simulando incertidumbre)

# Distribución de la Tasa de Crecimiento a Largo Plazo (g)
G_MEAN = 0.025                # Media de 'g'
G_STDEV = 0.005               # Desviación estándar de 'g'

# --- 4. Inicialización y Ejecución del Modelo ---
def run_dcf_valuation_advanced():
    """
    Función principal para inicializar, ejecutar y mostrar los resultados del modelo DCF avanzado.
    """
    dcf = DCFModel(
        initial_fcf=INITIAL_FCF, 
        net_debt=NET_DEBT, 
        shares_outstanding=SHARES_OUTSTANDING,
        explicit_years=EXPLICIT_YEARS
    )

    try:
        # 1. Ejecución del Caso Base (Determinístico)
        results_det = dcf.run_deterministic_valuation(
            wacc=WACC_DETERMINISTIC,
            long_term_growth_rate=G_DETERMINISTIC,
            initial_growth=INITIAL_GROWTH_RATE,
            step_down_growth=STEP_DOWN_GROWTH_RATE
        )
        
        # 2. Ejecución de la Simulación de Monte Carlo
        results_mc = dcf.run_monte_carlo_sensitivity(
            wacc_mean=WACC_MEAN,
            wacc_stdev=WACC_STDEV,
            g_mean=G_MEAN,
            g_stdev=G_STDEV,
            initial_growth=INITIAL_GROWTH_RATE,
            step_down_growth=STEP_DOWN_GROWTH_RATE
        )
        
        # 3. Impresión de Resultados
        dcf.print_results_monte_carlo(results_det, results_mc)
        
        # 4. Visualización de Resultados
        dcf.plot_monte_carlo_results()
        
    except ValueError as e:
        print("\n" + "="*70)
        print(f"ERROR: No se pudo completar la valoración. Detalle: {e}")
        print("="*70)

if __name__ == "__main__":
    run_dcf_valuation_advanced()
