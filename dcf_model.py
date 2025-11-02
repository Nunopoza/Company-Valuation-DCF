import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class DCFModel:
    """
    Clase para calcular el Valor Intrínseco de una empresa mediante el Flujo de Caja Descontado (DCF),
    utilizando un modelo de dos etapas y Simulación de Monte Carlo para análisis de Sensibilidad.
    """
    def __init__(self, initial_fcf, net_debt, shares_outstanding, explicit_years=5):
        """
        Inicializa el modelo DCF con los parámetros de entrada clave.

        :param initial_fcf (float): Flujo de Caja Libre (FCF) del año más reciente.
        :param net_debt (float): Deuda neta total de la empresa (Deuda - Efectivo).
        :param shares_outstanding (float): Número de acciones en circulación.
        :param explicit_years (int): Número de años para la proyección explícita.
        """
        self.initial_fcf = initial_fcf
        self.net_debt = net_debt
        self.shares_outstanding = shares_outstanding
        self.explicit_years = explicit_years
        
        # Parámetros por defecto para la Simulación de Monte Carlo
        self.simulations = 10000 
        self.simulated_per_share_values = []

        # Resultados de una sola corrida (Determinística)
        self.projected_fcfs = []
        self.pv_fcfs = 0.0
        self.terminal_value = 0.0
        self.fair_value_per_share_deterministic = 0.0

    def _project_and_discount_fcfs(self, wacc, growth_rates):
        """
        [INTERNAL] Proyecta FCFs y calcula el Valor Presente para un único escenario.
        
        :param wacc (float): Tasa de Descuento (WACC) para este escenario.
        :param growth_rates (list): Serie de tasas de crecimiento anual.
        :returns (float, float): PV de FCFs Explícitos y el FCF del último año explícito.
        """
        fcf_t = self.initial_fcf
        pv_of_explicit_flows = 0.0
        
        for t in range(1, self.explicit_years + 1):
            # Project FCF for Year t
            fcf_t *= (1 + growth_rates[t-1])
            
            # Discount FCF to present value
            discount_factor = (1 + wacc) ** t
            pv_fcf_t = fcf_t / discount_factor
            
            pv_of_explicit_flows += pv_fcf_t
            
        return pv_of_explicit_flows, fcf_t # FCF del Año T

    def _calculate_terminal_value(self, fcf_last_year, wacc, long_term_growth_rate):
        """
        [INTERNAL] Calcula el Valor Terminal (Valor de Perpetuidad) para un único escenario.
        """
        if wacc <= long_term_growth_rate:
            # En un entorno real, esto indicaría una valoración infinita o inválida.
            return 0.0 
            
        # FCF in Perpetuity (FCF_{T+1})
        fcf_in_perpetuity = fcf_last_year * (1 + long_term_growth_rate)
        
        # Gordon Growth Formula: TV_t = FCF_{t+1} / (WACC - g)
        terminal_value_at_year_T = fcf_in_perpetuity / (wacc - long_term_growth_rate)
        
        # Discount Terminal Value to present (at start of Year 1)
        discount_factor_T = (1 + wacc) ** self.explicit_years
        pv_terminal_value = terminal_value_at_year_T / discount_factor_T
        
        return pv_terminal_value

    def run_deterministic_valuation(self, wacc, long_term_growth_rate, initial_growth, step_down_growth):
        """
        Ejecuta una única valoración determinística (el caso base).
        
        :param wacc (float): WACC determinístico.
        :param long_term_growth_rate (float): Tasa de crecimiento determinística en perpetuidad.
        :param initial_growth (float): Tasa de crecimiento para la Etapa 1.
        :param step_down_growth (float): Tasa de crecimiento para la Etapa 2.
        :returns (dict): Resultados de la valoración base.
        """
        # Define la serie de crecimiento de dos etapas (simplicidad)
        growth_rates = [initial_growth] * 2 + [step_down_growth] * (self.explicit_years - 2)

        # 1. Proyección y Descuento de flujos explícitos
        pv_explicit_fcfs, fcf_last_year = self._project_and_discount_fcfs(wacc, growth_rates)
        self.pv_fcfs = pv_explicit_fcfs
        self.projected_fcfs = [self.initial_fcf] # No es el fcf real, solo para marcar el tamaño

        # 2. Cálculo y Descuento del Valor Terminal
        pv_terminal_value = self._calculate_terminal_value(fcf_last_year, wacc, long_term_growth_rate)
        self.terminal_value = pv_terminal_value
        
        # 3. Valoración Final
        enterprise_value = pv_explicit_fcfs + pv_terminal_value
        equity_value = enterprise_value - self.net_debt
        fair_value_per_share = equity_value / self.shares_outstanding

        self.fair_value_per_share_deterministic = fair_value_per_share
        
        # Guardamos la serie de FCF real para la impresión
        fcf_t = self.initial_fcf
        real_fcf_series = [fcf_t]
        for t in range(1, self.explicit_years + 1):
            fcf_t *= (1 + growth_rates[t-1])
            real_fcf_series.append(fcf_t)


        return {
            'Enterprise Value': enterprise_value,
            'Equity Value': equity_value,
            'Fair Value Per Share': fair_value_per_share,
            'PV of Explicit FCFs': pv_explicit_fcfs,
            'PV of Terminal Value': pv_terminal_value,
            'Projected FCFs (Year 0 to T)': real_fcf_series,
            'WACC': wacc,
            'Long Term Growth': long_term_growth_rate
        }

    def run_monte_carlo_sensitivity(self, wacc_mean, wacc_stdev, g_mean, g_stdev, initial_growth, step_down_growth, simulations=10000):
        """
        Ejecuta la Simulación de Monte Carlo para la sensibilidad de la valoración.
        
        :param wacc_mean (float): Media del WACC (Distribución Normal).
        :param wacc_stdev (float): Desviación estándar del WACC (Distribución Normal).
        :param g_mean (float): Media de la Tasa de Crecimiento a Largo Plazo (g) (Distribución Normal).
        :param g_stdev (float): Desviación estándar de g (Distribución Normal).
        :param initial_growth (float): Tasa de crecimiento determinística para la Etapa 1.
        :param step_down_growth (float): Tasa de crecimiento determinística para la Etapa 2.
        :param simulations (int): Número de escenarios a simular.
        """
        self.simulations = simulations
        
        # Simular distribuciones de WACC y Tasa de Crecimiento a Largo Plazo (g)
        simulated_waccs = norm.rvs(loc=wacc_mean, scale=wacc_stdev, size=self.simulations)
        simulated_gs = norm.rvs(loc=g_mean, scale=g_stdev, size=self.simulations)
        
        # Asegurarse de que las tasas tienen sentido (no negativas, WACC > g)
        simulated_waccs = np.maximum(simulated_waccs, 0.01) # WACC must be > 0
        simulated_gs = np.maximum(simulated_gs, 0.01)       # g must be > 0
        
        # Definir la serie de crecimiento para la proyección explícita (determinística)
        growth_rates = [initial_growth] * 2 + [step_down_growth] * (self.explicit_years - 2)
        
        results_list = []
        
        for i in range(self.simulations):
            wacc_i = simulated_waccs[i]
            g_i = simulated_gs[i]
            
            # Solo calcular si WACC > g para evitar errores en Gordon Growth
            if wacc_i > g_i:
                # Paso 1: Proyección y Descuento de flujos explícitos
                pv_explicit_fcfs, fcf_last_year = self._project_and_discount_fcfs(wacc_i, growth_rates)
                
                # Paso 2: Cálculo y Descuento del Valor Terminal
                pv_terminal_value = self._calculate_terminal_value(fcf_last_year, wacc_i, g_i)
                
                # Paso 3: Valor por Acción
                enterprise_value = pv_explicit_fcfs + pv_terminal_value
                equity_value = enterprise_value - self.net_debt
                
                if self.shares_outstanding > 0:
                    fair_value_per_share = equity_value / self.shares_outstanding
                    results_list.append(fair_value_per_share)
        
        self.simulated_per_share_values = np.array(results_list)

        return {
            'Count': len(results_list),
            'Mean': np.mean(self.simulated_per_share_values) if results_list else 0,
            'Median': np.median(self.simulated_per_share_values) if results_list else 0,
            'StDev': np.std(self.simulated_per_share_values) if results_list else 0,
            '95% Confidence Interval': np.percentile(self.simulated_per_share_values, [2.5, 97.5]) if results_list else [0, 0]
        }

    def plot_monte_carlo_results(self):
        """
        Genera un histograma de la distribución de los valores por acción simulados.
        Devuelve el objeto de la figura de Matplotlib para ser renderizado por Streamlit.
        """
        if len(self.simulated_per_share_values) == 0:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No hay datos para graficar (Ajusta parámetros).", 
                    ha='center', va='center')
            return fig

        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(self.simulated_per_share_values, bins=50, density=True, alpha=0.6, color='skyblue', edgecolor='black')
        
        # Añadir las estadísticas clave
        mean_val = np.mean(self.simulated_per_share_values)
        median_val = np.median(self.simulated_per_share_values)
        p5_val, p95_val = np.percentile(self.simulated_per_share_values, [5, 95])
        
        ax.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Media: ${mean_val:,.2f}')
        ax.axvline(median_val, color='green', linestyle='dashed', linewidth=2, label=f'Mediana: ${median_val:,.2f}')
        ax.axvline(p5_val, color='gray', linestyle='dotted', linewidth=1, label='Percentil 5%/95%')
        ax.axvline(p95_val, color='gray', linestyle='dotted', linewidth=1)

        ax.set_title('Distribución de Valor Implícito por Acción (Simulación Monte Carlo)', fontsize=14)
        ax.set_xlabel('Valor por Acción ($)', fontsize=12)
        ax.set_ylabel('Frecuencia Normalizada', fontsize=12)
        ax.legend()
        ax.grid(axis='y', alpha=0.5)
        
        # Devolver el objeto de la figura (necesario para Streamlit)
        return fig

    def print_results_monte_carlo(self, results_det, results_mc):
        """
        Devuelve un diccionario simple con los resultados clave, ya que la presentación
        será manejada por Streamlit.
        """
        ci_low, ci_high = results_mc['95% Confidence Interval']
        
        return {
            'Deterministic_Value': results_det['Fair Value Per Share'],
            'MC_Mean': results_mc['Mean'],
            'MC_Median': results_mc['Median'],
            'MC_StDev': results_mc['StDev'],
            'MC_CI_Low': ci_low,
            'MC_CI_High': ci_high
        }
