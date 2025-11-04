from tax_estimate import calculate_tax
from withdrawal_rsu_401K import GROWTH_RATE, INFLATION_RATE, FILING_STATUS, calculate_tax_free_wealth
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Top-level simulation parameters (already in file, but redefined for clarity)
total_asset_401k = 3600000
start_year = 2027
end_year = 2058

# Social security
ss_start_year = 2040
ss_amount_base = 80000

# Other income
ordinary_dividend_base = 50000

PRINT_DEBUG = False

def simulate_roth_conversion_scenario(current_scenario, 
                                      years, total_401k, 
                                      ss_start_year, ss_amount_base, 
                                      ordinary_dividend_base):
    """
    Simulate a Roth IRA conversion strategy over a range of years, moving assets from 401K to Roth IRA.

    For each year in the simulation:
      1. Calculate the annual conversion amount as total_401k / divisor.
      2. If the year is after ss_start_year, offset the conversion by the Social Security amount (ss_amount_base).
      3. Cap the withdrawal to the remaining 401k balance.
      4. Compute the tax using the current tax brackets (via calculate_tax), including 401k withdrawal, Social Security, and ordinary dividends.
      5. Move the withdrawal amount from 401k to Roth IRA.
      6. Grow both 401k and Roth IRA by (GROWTH_RATE - INFLATION_RATE).
      7. Accumulate the total tax paid.

    At the end, the function returns a summary of the scenario, including the final Roth IRA balance, final 401k balance, total tax paid, and net tax-free wealth (Roth + 0.65*401k - tax).

    Args:
        current_scenario (tuple): (label, divisor) where label is a string for reporting and divisor is the number of years to spread the conversion (e.g., 10 for aggressive, 25 for conservative).
        years (list of int): Years to simulate (e.g., range(start_year, end_year+1)).
        total_401k (float): Initial 401k asset value.
        ss_start_year (int): Year when Social Security starts.
        ss_amount_base (float): Annual Social Security income (in today's dollars).
        ordinary_dividend_base (float): Annual ordinary dividend income (in today's dollars).

    Returns:
        dict: {
            'label': str,                # Scenario label
            'final_roth': float,         # Final Roth IRA balance
            'final_401k': float,         # Final 401k balance
            'total_tax_paid': float,     # Total tax paid over the simulation
            'net_wealth': float          # Net tax-free wealth (tax-free value minus total tax)
        }
    """
    label, divisor = current_scenario
    assets = {'401k': total_401k, 'roth_ira': 0}
    total_tax_paid = 0
    growth = GROWTH_RATE - INFLATION_RATE

    for year in years: 
        # Determine withdrawal/conversion amount
        annual_conversion = total_401k / divisor
        ss_income = ss_amount_base if year >= ss_start_year else 0

        # Offset withdrawal by SS if applicable
        withdrawal = max(annual_conversion - ss_income, 0) if ss_income > 0 else annual_conversion
        # Cap withdrawal to remaining 401k
        withdrawal = min(withdrawal, assets['401k'])
        # Prepare income details for tax calculation
        income_details = {
            '401k_distribution': withdrawal,
            'social_security_distribution': ss_income,
            'ordinary_dividend': ordinary_dividend_base
        }
        tax_result = calculate_tax(income_details, FILING_STATUS)
        tax_paid = tax_result['total_tax']
        total_tax_paid += tax_paid
        # Move withdrawal from 401k to Roth IRA
        assets['401k'] -= withdrawal
        assets['roth_ira'] += withdrawal
        # Grow both by (growth_rate - inflation_rate)
        assets['401k'] *= (1 + growth)
        assets['roth_ira'] *= (1 + growth)
        if PRINT_DEBUG and year == years[0]:
            print(f"{'Year':>6s} | {'401k':>8s} | {'Roth IRA':>8s} | {'Tax Paid':>8s}")
            print("-" * 38)
        if PRINT_DEBUG:
            print(f"{year:6d} | {int(assets['401k']):8d} | {int(assets['roth_ira']):8d} | {int(tax_paid):8d}")
    # At the end, tax-free wealth is calculated from all assets
    tax_free_wealth = calculate_tax_free_wealth(assets)
    net_wealth = tax_free_wealth - total_tax_paid
    return {
        'label': label,
        'final_roth': assets['roth_ira'],
        'final_401k': assets['401k'],
        'total_tax_paid': total_tax_paid,
        'net_wealth': net_wealth
    }

def grid_search_roth_conversion(years, total_401k, 
                                ss_start_year, ss_amount_base, 
                                ordinary_dividend_base):
    """
    Perform a grid search of Roth conversion strategies from 5 to 25 years with 1-year intervals.
    
    Args:
        years (list): Years to simulate
        total_401k (float): Initial 401k balance
        ss_start_year (int): Year Social Security starts
        ss_amount_base (float): Annual Social Security amount
        ordinary_dividend_base (float): Annual ordinary dividend income
        
    Returns:
        tuple: (conversion_years, net_wealths) - lists of conversion periods and corresponding net wealth values
    """
    conversion_years = list(range(5, 26))  # 5 to 25 years
    net_wealths = []
    
    print(f"\nGrid Search: Roth Conversion from 5 to 25 years")
    print(f"{'Years':>6s} | {'Net Wealth':>12s} | {'Roth IRA':>12s} | {'401k':>12s} | {'Tax Paid':>10s}")
    print("-" * 60)
    
    for divisor in conversion_years:
        scenario = (f"{divisor} years", divisor)
        result = simulate_roth_conversion_scenario(
            scenario, years, total_401k, ss_start_year, ss_amount_base, ordinary_dividend_base
        )
        net_wealths.append(result['net_wealth'])
        print(f"{divisor:6d} | {int(result['net_wealth']):12d} | {int(result['final_roth']):12d} | {int(result['final_401k']):12d} | {int(result['total_tax_paid']):10d}")
    
    return conversion_years, net_wealths

def plot_net_wealth_curve(conversion_years, net_wealths):
    """
    Plot the net wealth impact as a function of conversion years.
    
    Args:
        conversion_years (list): List of conversion periods (5-25 years)
        net_wealths (list): Corresponding net wealth values
    """
    plt.figure(figsize=(10, 6))
    
    plt.plot(conversion_years, net_wealths, 'b-o', linewidth=2, markersize=6)
    plt.xlabel('Conversion Period (Years)')
    plt.ylabel('Net Wealth ($)')
    plt.title('Net Wealth Impact vs Roth Conversion Period')
    plt.grid(True, alpha=0.3)
    
    # Find optimal conversion period
    optimal_years = conversion_years[np.argmax(net_wealths)]
    optimal_wealth = max(net_wealths)
    plt.annotate(f'Optimal: {optimal_years} years\nNet Wealth: ${optimal_wealth:,.0f}', 
                xy=(optimal_years, optimal_wealth), 
                xytext=(optimal_years + 2, optimal_wealth - 200000),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    plt.tight_layout()
    
    # Add key press handler to close the window
    def on_key_press(event):
        plt.close()
    
    plt.gcf().canvas.mpl_connect('key_press_event', on_key_press)
    plt.show()
    
    print(f"\nOptimal conversion period: {optimal_years} years")
    print(f"Maximum net wealth: ${optimal_wealth:,.0f}")
    print(f"Wealth difference from 5-year strategy: ${optimal_wealth - net_wealths[0]:,.0f}")

def main():
    years = list(range(start_year, end_year + 1))
    
    # Original 5 scenarios
    scenarios = [
        ('Rocket (1/5)', 5),
        ('Aggressive (1/10)', 10),
        ('Intermediate (1/15)', 15),
        ('Moderate (1/20)', 20),
        ('Conservative (1/25)', 25)
    ]
    results = []
    for current_scenario in scenarios:
        result = simulate_roth_conversion_scenario(
            current_scenario, years, total_asset_401k, ss_start_year, ss_amount_base, ordinary_dividend_base
        )
        results.append(result)
    print("\nRoth Conversion Scenarios (Tax-Free Wealth minus Total Tax Paid):")
    print(f"{'Scenario':<23s} | {'Net Wealth':>12s} | {'Roth IRA':>12s} | {'401k':>12s} | {'Tax Paid':>10s}")
    print("-" * 78)
    for r in results:
        print(f"{r['label']:<23s} | {int(r['net_wealth']):12d} | {int(r['final_roth']):12d} | {int(r['final_401k']):12d} | {int(r['total_tax_paid']):10d}")
    
    # Grid search and plotting
    conversion_years, net_wealths = grid_search_roth_conversion(
        years, total_asset_401k, ss_start_year, ss_amount_base, ordinary_dividend_base
    )
    plot_net_wealth_curve(conversion_years, net_wealths)

if __name__ == "__main__":
    main()

 