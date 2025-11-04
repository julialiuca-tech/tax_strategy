#!/usr/bin/env python3
"""
Withdrawal Strategy Optimizer
Optimizes withdrawal strategy to maximize tax-free wealth passed to children.
"""

import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from tax_estimate import calculate_tax, get_tax_config

# Global constants
TAX_EFFICIENCY_FACTORS = {
    '401k': 0.65,  # Heirs pay ordinary income tax
    'roth_ira': 1.0,  # Completely tax-free
    'taxable_stock_rsu': 1.0,  # Step-up basis eliminates gains tax
    'taxable_stocks_nonrsu': 1.0,  # Step-up basis eliminates gains tax
    'taxable_stock_rsu_cost_basis': 0,  # Not an asset, just tracking
    'taxable_stock_nonrsu_cost_basis': 0  # Not an asset, just tracking
}


GROWTH_RATE = 0.06
INFLATION_RATE = 0.03
FILING_STATUS = 'married_jointly'

PRINT_FLAG = False  # Set to False to disable detailed printing
GROWTH_RATE_ASSETS = {
    '401k': GROWTH_RATE,
    'roth_ira': GROWTH_RATE,
    'taxable_stock_rsu': GROWTH_RATE*0.8 ,
    'taxable_stocks_nonrsu':  GROWTH_RATE,
}

# Test scenario
TestScenario = {
    'annual_income_needs': 200000,
    'base_ordinary_dividend': 50000, 
    'assets': {
        '401k': 3600000,
        'roth_ira': 0,
        'taxable_stock_rsu': 1800000,
        'taxable_stock_rsu_cost_basis': 1500000,  # 20% of current value
        'taxable_stocks_nonrsu': 0,
        'taxable_stock_nonrsu_cost_basis': 0
    }
}

def calculate_tax_free_wealth(assets):
    """
    Calculate tax-free wealth that can be passed to heirs.
    
    Args:
        assets (dict): Asset values
        
    Returns:
        float: Tax-free wealth amount
    """
    tax_free_wealth = 0
    for asset_type, value in assets.items():
        if asset_type in TAX_EFFICIENCY_FACTORS and value > 0:
            tax_free_wealth += value * TAX_EFFICIENCY_FACTORS[asset_type]
    
    return tax_free_wealth

def print_simulation_year_details(year, withdrawal_rsu, withdrawal_401k, withdrawal_nonrsu, 
                                 withdrawal_roth, tax_paid, net_income, total_assets, 
                                 asset_rsu, asset_nonrsu, asset_401k, asset_roth):
    """
    Print detailed simulation information for a single year.
    
    Args:
        year (int): Current simulation year
        withdrawal_rsu (float): RSU withdrawal amount
        withdrawal_401k (float): 401k withdrawal amount
        withdrawal_nonrsu (float): Non-RSU stock withdrawal amount
        withdrawal_roth (float): Roth IRA withdrawal amount
        tax_paid (float): Total tax paid
        net_income (float): Net income after tax
        total_assets (float): Total asset value
        asset_rsu (float): RSU asset value
        asset_nonrsu (float): Non-RSU asset value
        asset_401k (float): 401K asset value
        asset_roth (float): Roth IRA asset value
    """
    print(f"{year:4d} | "
          f"{withdrawal_rsu:8.0f} | "
          f"{withdrawal_401k:8.0f} | "
          f"{withdrawal_nonrsu:8.0f} | "
          f"{withdrawal_roth:8.0f} | "
          f"{tax_paid:8.0f} | "
          f"{net_income:8.0f} | "
          f"{total_assets:12.0f} | "
          f"{asset_rsu:10.0f} | "
          f"{asset_nonrsu:10.0f} | "
          f"{asset_401k:10.0f} | "
          f"{asset_roth:10.0f}")

def print_simulation_header():
    """Print header for simulation details."""
    print(f"{'Year':4s} | "
          f"{'RSU':8s} | "
          f"{'401k':8s} | "
          f"{'NonRSU':8s} | "
          f"{'Roth':8s} | "
          f"{'Tax':8s} | "
          f"{'Net':8s} | "
          f"{'Total':12s} | "
          f"{'asset_RSU':10s} | "
          f"{'asset_nonRSU':10s} | "
          f"{'asset_401K':10s} | "
          f"{'asset_Roth':10s}")
    print("-" * 140)



def grow_assets(assets, num_years=1):
    """
    Grow assets by their respective growth rates.
    
    Args:
        assets (dict): Asset values to grow
        num_years (int): Number of years to grow
    Returns:
        dict: Updated assets with growth applied
    """
    # Use asset-specific growth rates from GROWTH_RATE_ASSETS
    for asset_type, value in assets.items():
        if asset_type in GROWTH_RATE_ASSETS and value > 0:
            asset_growth_rate = GROWTH_RATE_ASSETS[asset_type]
            assets[asset_type] *= (1 + asset_growth_rate) ** num_years
    
    return assets

def compute_withdrawal_schedule_single_asset(total_amount_today, start_year, end_year,
                                current_year=None):
    """
    Compute inflation-adjusted withdrawals to deplete an account over a specified time horizon using the annuity formula.
    Args:
        total_amount_today (float): Current value of the asset
        start_year (int): Year to start withdrawals
        end_year (int): Year to finish withdrawals
        current_year (int): Current year (defaults to current year if None)
    Returns:
        list: List of yearly withdrawals (inflation-adjusted) that deplete the account
    """
    if current_year is None:
        current_year = datetime.now().year + 1
    if start_year < current_year:
        raise ValueError(f"Start year {start_year} cannot be before current year {current_year}")
    if end_year < start_year:
        raise ValueError(f"End year {end_year} cannot be before start year {start_year}")
    years_to_grow = start_year - current_year
    projected_value = total_amount_today * (1 + GROWTH_RATE) ** years_to_grow
    n_years = end_year - start_year + 1

    r = GROWTH_RATE
    i = INFLATION_RATE
    # Use the annuity formula for inflation-adjusted withdrawals
    if r == i:
        # Avoid division by zero if real return is zero
        withdrawal_0 = projected_value / n_years
    else:
        withdrawal_0 = projected_value * (r - i) / (1 - ((1 + i) / (1 + r)) ** n_years)
    # Build the schedule: each year, withdrawal increases by inflation
    schedule = [withdrawal_0 * (1 + i) ** k for k in range(n_years)]
    return schedule

def generate_consolidated_withdrawal_schedule(
    assets,
    withdrawal_years
):
    """
    Generate and consolidate withdrawal schedules for 401K and RSU stock.
    Args:
        assets: dict with keys '401k', 'taxable_stock_rsu' (amounts)
        withdrawal_years: dict with keys for each asset, each value is a (start, end) tuple
    Returns:
        dict: {'years': [...], '401k': [...], 'rsu': [...], 'total': [...]}
    """
    asset_keys = [k for k in withdrawal_years.keys() if k in ['401k', 'taxable_stock_rsu']]
    schedules = {}
    for key in asset_keys:
        amt = assets.get(key, 0)
        years = withdrawal_years.get(key, (0, -1))
        if years[1] < years[0]:
            schedules[key] = []
        else:
            schedules[key] = compute_withdrawal_schedule_single_asset(
                amt,
                years[0],
                years[1],
            )
    min_year = min((withdrawal_years[k][0] for k in asset_keys if withdrawal_years[k][1] >= withdrawal_years[k][0]), default=0)
    max_year = max((withdrawal_years[k][1] for k in asset_keys if withdrawal_years[k][1] >= withdrawal_years[k][0]), default=0)
    n_years = max_year - min_year + 1 if max_year >= min_year else 0
    def pad_schedule(sched, start, end):
        pre = [0]*(start-min_year)
        post = [0]*(max_year-end)
        return pre + sched + post
    sched_401k = pad_schedule(schedules['401k'], withdrawal_years['401k'][0], withdrawal_years['401k'][1]) if n_years else []
    sched_rsu = pad_schedule(schedules['taxable_stock_rsu'], withdrawal_years['taxable_stock_rsu'][0], withdrawal_years['taxable_stock_rsu'][1]) if n_years else []
    return {
        'years': [min_year + i for i in range(n_years)],
        '401k': sched_401k,
        'rsu': sched_rsu,
        'total': [sched_401k[i] + sched_rsu[i] for i in range(n_years)]
    }

def stock_sale_for_annual_need(annual_income_need, cost_basis_ratio, capital_gains_rate=0.20):
    """
    Calculate stock withdrawal amount needed to meet annual income needs after capital gains tax.
    The equation is: stock_withdrawal - (stock_withdrawal - cost_basis) * capital_gains_rate = annual_income_need
    Solving for stock_withdrawal:
    stock_withdrawal - stock_withdrawal * capital_gains_rate + cost_basis * capital_gains_rate = annual_income_need
    stock_withdrawal * (1 - capital_gains_rate) + cost_basis * capital_gains_rate = annual_income_need
    stock_withdrawal * (1 - capital_gains_rate) = annual_income_need - cost_basis * capital_gains_rate
    stock_withdrawal = (annual_income_need - cost_basis * capital_gains_rate) / (1 - capital_gains_rate)
    Args:
        annual_income_need (float): Required annual income after tax
        cost_basis_ratio (float): Ratio of cost basis to current stock value (0-1)
        capital_gains_rate (float): Capital gains tax rate (default 20% for long-term gains)
    Returns:
        float: Stock withdrawal amount needed
    """
    if cost_basis_ratio >= 1.0:
        return annual_income_need
    effective_tax_rate = (1 - cost_basis_ratio) * capital_gains_rate
    stock_withdrawal = annual_income_need / (1 - effective_tax_rate)
    return stock_withdrawal

def calc_deposit_growth(deposits, time_horizon):
    """
    Calculate the total value of deposits at a future time horizon.
    
    Args:
        deposits (dict): Dictionary with year keys and deposit amounts as values
                        e.g., {'2025': 1000, '2027': 1300, ...}
        time_horizon (int): Target year to calculate total value
        
    Returns:
        float: Total value at time horizon
    """
    total_value = 0.0
    
    for deposit_year_str, deposit_amount in deposits.items():
        deposit_year = int(deposit_year_str)
        
        if deposit_year > time_horizon:
            # Skip deposits after the time horizon
            continue
            
        # Calculate years of growth
        years_of_growth = time_horizon - deposit_year
        
        # Calculate future value of this deposit
        future_value = deposit_amount * (1 + GROWTH_RATE) ** years_of_growth
        total_value += future_value
    
    return total_value

def simulate_withdrawal_schedule(assets, withdrawal_schedule, annual_income_need,
                                 base_ordinary_dividend=0, current_year=None):
    """
    Simulate withdrawal process over years according to a given withdrawal schedule.
    Args:
        assets (dict): Initial asset values
        withdrawal_schedule (dict): Withdrawal schedule with 'years', '401k', 'rsu' lists
        annual_income_need (float): Annual income need (will be inflation adjusted)
        base_ordinary_dividend (float): Base ordinary dividend income to include in tax calculations
        current_year (int): Starting year for simulation
    Returns:
        dict: {
            'final_assets': sim_assets,
            'income_gaps': income_gaps,
            'total_gap': total_gap,
            'roth_conversions': total_roth_conversions,
            'taxable_additions': total_taxable_additions
        }
    """
    if current_year is None:
        current_year = datetime.now().year
    sim_assets = assets.copy()
    income_gaps = {}
    
    # Print header if PRINT_FLAG is enabled
    if PRINT_FLAG:
        print_simulation_header()
    
    for i, year in enumerate(withdrawal_schedule['years']):
        # annual income need is inflate-adjusted
        years_from_start = year - current_year
        adjusted_income_need = annual_income_need * (1 + INFLATION_RATE) ** years_from_start

        # compute the cost basis ratio, need that for tax computation and cost-basis adjustment
        if sim_assets.get( 'taxable_stock_rsu', 0) > 0 :
            rsu_cost_basis_ratio = (sim_assets.get('taxable_stock_rsu_cost_basis', 0) /
                                    sim_assets.get('taxable_stock_rsu', 1))
        else:
            rsu_cost_basis_ratio = 0

        # if sim_assets['401k'] < withdrawal_schedule['401k'][i]:
        #     break

        # compute tax from withdrawal
        k401_withdrawal = min([withdrawal_schedule['401k'][i], sim_assets.get('401k', 0)])
        rsu_withdrawal = min([withdrawal_schedule['rsu'][i], sim_assets.get('taxable_stock_rsu', 0)])
        rsu_gains = rsu_withdrawal * (1 - rsu_cost_basis_ratio)
        income_sources = {}
        if k401_withdrawal > 0:
            income_sources['401k_distribution'] = k401_withdrawal
        if rsu_gains > 0:
            income_sources['long_term_capital_gain'] = rsu_gains
        # Add base ordinary income to tax calculation
        if base_ordinary_dividend > 0:
            income_sources['ordinary_dividend'] = base_ordinary_dividend
        tax_paid = 0
        if income_sources:
            tax_result = calculate_tax(income_sources, FILING_STATUS)
            tax_paid = tax_result['total_tax']

        # withdrawal
        sim_assets['401k'] -= k401_withdrawal
        sim_assets['taxable_stock_rsu'] -= rsu_withdrawal
        sim_assets['taxable_stock_rsu_cost_basis'] =  sim_assets['taxable_stock_rsu'] * rsu_cost_basis_ratio

        # compute net_income, depending on the polarity, deposit or note gap
        net_income = k401_withdrawal + rsu_withdrawal - tax_paid
        
        # Initialize withdrawal variables for printing
        withdrawal_nonrsu = 0
        withdrawal_roth = 0
        
        if net_income < adjusted_income_need:
            gap = adjusted_income_need - net_income
            income_gaps[str(year)] = gap
        else:
            gap = 0
            surplus = net_income - adjusted_income_need
            if surplus > 0:
                roth_conversion = min(surplus, k401_withdrawal)
                sim_assets['roth_ira'] += roth_conversion
                taxable_addition = surplus - roth_conversion
                if taxable_addition > 0:
                    sim_assets['taxable_stocks_nonrsu'] += taxable_addition
                    sim_assets['taxable_stock_nonrsu_cost_basis'] += taxable_addition

        # Calculate total assets and tax-free assets for printing
        total_assets = sum(value for key, value in sim_assets.items() 
                          if not key.endswith('_cost_basis'))
        total_tax_free = calculate_tax_free_wealth(sim_assets)
        
        # Print year details if PRINT_FLAG is enabled
        if PRINT_FLAG:
            print_simulation_year_details(year, rsu_withdrawal, k401_withdrawal, withdrawal_nonrsu,
                                        withdrawal_roth, tax_paid, net_income, total_assets,
                                        sim_assets.get('taxable_stock_rsu', 0),
                                        sim_assets.get('taxable_stocks_nonrsu', 0),
                                        sim_assets.get('401k', 0),
                                        sim_assets.get('roth_ira', 0))

        sim_assets = grow_assets(sim_assets, 1)

    return {
        'sim_year': withdrawal_schedule['years'][-1],
        'sim_assets': sim_assets,
        'income_gaps': income_gaps,
        'adjusted_income_need': adjusted_income_need
    }

def simulate_withdrawal_after_schedule(schedule_end_state, horizon_simulation, base_ordinary_dividend=0):
    """
    Continue simulation from the end of a withdrawal schedule to a horizon.
    
    Args:
        schedule_end_state (dict): Output from simulate_withdrawal_schedule()
        horizon_simulation (int): Year to simulate up to
        base_ordinary_dividend (float): Base ordinary dividend income to include in tax calculations
        
    Returns:
        dict: Final simulation results with tax-free wealth and gap analysis
    """
    # Initialize from schedule end state
    sim_assets = schedule_end_state['sim_assets'].copy()
    sim_year = schedule_end_state['sim_year']
    adjusted_income_need = schedule_end_state['adjusted_income_need']
    income_gaps = schedule_end_state['income_gaps'].copy()
    
    # Sanity check: 401K and RSU should be depleted
    if sim_assets.get('401k', 0) > 0.5 * adjusted_income_need:
        raise ValueError(f"401K still has ${sim_assets['401k']:,.0f} remaining, should be depleted")
    if sim_assets.get('taxable_stock_rsu', 0) > 0.5 * adjusted_income_need:
        raise ValueError(f"RSU stock still has ${sim_assets['taxable_stock_rsu']:,.0f} remaining, should be depleted")
    
    # Simulate years from sim_year+1 to horizon_simulation
    for year in range(sim_year + 1, horizon_simulation + 1):
        # Inflation adjust annual income need
        adjusted_income_need = adjusted_income_need * (1 + INFLATION_RATE)

        # Initialize withdrawal variables for printing
        withdrawal_rsu = 0
        withdrawal_401k = 0
        withdrawal_nonrsu = 0
        withdrawal_roth = 0
        tax_paid = 0
        net_income = 0
        gap = adjusted_income_need

        # Try to withdraw from non-RSU stock first
        if sim_assets.get('taxable_stocks_nonrsu', 0) > 0:
            # Calculate cost basis ratio for non-RSU stock
            nonrsu_cost_basis_ratio = (sim_assets.get('taxable_stock_nonrsu_cost_basis', 0) /
                                     sim_assets.get('taxable_stocks_nonrsu', 1)) if sim_assets.get('taxable_stocks_nonrsu', 0) > 0 else 0
            
            # Calculate withdrawal amount needed
            stock_withdrawal_needed = stock_sale_for_annual_need(adjusted_income_need, nonrsu_cost_basis_ratio)
            stock_withdrawal_amount = min([stock_withdrawal_needed, sim_assets['taxable_stocks_nonrsu']])
            withdrawal_nonrsu = stock_withdrawal_amount
            sim_assets['taxable_stocks_nonrsu'] -= stock_withdrawal_amount
            cost_basis_reduction = stock_withdrawal_amount * nonrsu_cost_basis_ratio
            sim_assets['taxable_stock_nonrsu_cost_basis'] -= cost_basis_reduction
                
            # Calculate tax on capital gains
            capital_gains = stock_withdrawal_amount* (1 - nonrsu_cost_basis_ratio)
            income_sources = {'long_term_capital_gain': capital_gains}
            # Add base ordinary income to tax calculation
            if base_ordinary_dividend > 0:
                income_sources['ordinary_dividend'] = base_ordinary_dividend
            tax_result = calculate_tax(income_sources, FILING_STATUS)
            tax_paid = tax_result['total_tax']

            net_income = stock_withdrawal_amount - tax_paid
            gap -= net_income

        if gap > 0:  # still have gap, now withdraw from ROTH IRA
            roth_withdrawal_amount = min(gap, sim_assets['roth_ira'])
            withdrawal_roth = roth_withdrawal_amount
            sim_assets['roth_ira'] -= roth_withdrawal_amount
            gap -= roth_withdrawal_amount

        if gap > 0: # still have income gap, record the gap
            income_gaps[str(year)] = gap
        else:
            gap=0

        # Calculate total assets and tax-free assets for printing
        total_assets = sum(value for key, value in sim_assets.items() 
                          if not key.endswith('_cost_basis'))
        total_tax_free = calculate_tax_free_wealth(sim_assets)
        
        # Print year details if PRINT_FLAG is enabled
        if PRINT_FLAG:
            print_simulation_year_details(year, withdrawal_rsu, withdrawal_401k, withdrawal_nonrsu,
                                        withdrawal_roth, tax_paid, net_income, total_assets,
                                        sim_assets.get('taxable_stock_rsu', 0),
                                        sim_assets.get('taxable_stocks_nonrsu', 0),
                                        sim_assets.get('401k', 0),
                                        sim_assets.get('roth_ira', 0))

        # Grow remaining assets
        sim_assets = grow_assets(sim_assets, 1)
    
    # Calculate final outcomes
    tax_free_wealth = calculate_tax_free_wealth(sim_assets)
    
    # Calculate gap growth effect
    gap_growth_effect = 0
    if income_gaps:
        # Use calc_deposit_growth to compute the effect of gaps
        # Treat gaps as "deposits" that grow at the growth rate
        gap_growth_effect = calc_deposit_growth(income_gaps, horizon_simulation)
    
    return {
        'final_assets': sim_assets,
        'tax_free_wealth': tax_free_wealth,
        'income_gaps': income_gaps,
        'gap_growth_effect': gap_growth_effect,
        'net_wealth_impact': tax_free_wealth - gap_growth_effect
    }



def simulate_withdrawal_scenario(initial_assets, annual_income_need, base_ordinary_dividend,
                       start_401K_year, end_401K_year, start_rsu_year, end_rsu_year, horizon_year=2040):
    """
    Simulate a single withdrawal strategy and return the result.
    
    Args:
        initial_assets (dict): Initial asset values
        annual_income_need (float): Annual income need
        base_ordinary_dividend (float): Base ordinary dividend income
        start_401K_year (int): 401K start year
        end_401K_year (int): 401K end year
        start_rsu_year (int): RSU start year
        end_rsu_year (int): RSU end year
        horizon_year (int): Year to simulate up to
        
    Returns:
        dict: Simulation result with parameters and net wealth impact
    """
    # Generate withdrawal schedule
    withdrawal_years = {
        '401k': (start_401K_year, end_401K_year),
        'taxable_stock_rsu': (start_rsu_year, end_rsu_year)
    }

    # generate the withdrawal schedule
    schedule = generate_consolidated_withdrawal_schedule(
        initial_assets, 
        withdrawal_years)

    # Simulate withdrawal process
    simulation_result_sched = simulate_withdrawal_schedule(
        assets=initial_assets,
        withdrawal_schedule=schedule,
        annual_income_need=annual_income_need,
        base_ordinary_dividend=base_ordinary_dividend
    )
    # simulate after the 401K -> roth and rsu -> non-rsu conversion are complete
    simulation_result_after = simulate_withdrawal_after_schedule(
        simulation_result_sched, 
        horizon_year, 
        base_ordinary_dividend)
    
    return {
        '401K start from': start_401K_year, 
        '401K withdrawal to': end_401K_year,
        'rsu withdrawal from': start_rsu_year,
        'rsu withdrawal to': end_rsu_year,
        'net_wealth_impact': simulation_result_after['net_wealth_impact'],
        'final_assets': simulation_result_after['final_assets']
    }


def exhaustive_search_with_visualization(initial_assets, annual_income_need, base_ordinary_dividend, 
                                       start_rsu_year=2026, start_401k_range=(2026, 2031), 
                                       end_401k_range_offset=10, end_rsu_range_offset=10, 
                                       horizon_year=2040, target_end_rsu_year=2028):
    """
    Perform exhaustive search over withdrawal strategies and visualize results.
    
    Args:
        initial_assets (dict): Initial asset values
        annual_income_need (float): Annual income need
        base_ordinary_dividend (float): Base ordinary dividend income
        start_rsu_year (int): RSU start year
        start_401k_range (tuple): Range for 401K start years (start, end)
        end_401k_range_offset (int): Number of years to extend 401K withdrawal
        end_rsu_range_offset (int): Number of years to extend RSU withdrawal
        horizon_year (int): Year to simulate up to
        target_end_rsu_year (int): Target RSU withdrawal end year to filter for visualization
        
    Returns:
        list: Simulation record with all results
    """
    simulation_record = []
    
    for start_401K_year in range(start_401k_range[0], start_401k_range[1]):
        for end_401K_year in range(start_401K_year, start_401K_year+end_401k_range_offset):
            for end_rsu_year in range(start_rsu_year, start_rsu_year+end_rsu_range_offset):

                # Simulate this withdrawal strategy
                result = simulate_withdrawal_scenario(
                    initial_assets, annual_income_need, base_ordinary_dividend,
                    start_401K_year, end_401K_year, start_rsu_year, end_rsu_year, horizon_year
                )
                simulation_record.append(result)
    
    # Filter simulation results for the target end_rsu_year
    filtered_results = [result for result in simulation_record if result['rsu withdrawal to'] == target_end_rsu_year]
    
    if filtered_results:
        print(f"\n3-D Visualization for RSU withdrawal ending in {target_end_rsu_year}")
        print(f"Number of data points: {len(filtered_results)}")
        
        # Extract data for 3-D plot
        start_401k_years = [result['401K start from'] for result in filtered_results]
        end_401k_years = [result['401K withdrawal to'] for result in filtered_results]
        net_wealth_impacts = [result['net_wealth_impact'] for result in filtered_results]
        
        # Calculate number of years for 401K withdrawal
        withdrawal_years = [(end_401k_years[i] - start_401k_years[i] + 1) for i in range(len(start_401k_years))]
        
        # Create 3-D scatter plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Group data by start_401K_year
        start_years = sorted(set(start_401k_years))
        colors = plt.cm.viridis(np.linspace(0, 1, len(start_years)))
        
        # Plot lines connecting dots with same start_401K_year
        for i, start_year in enumerate(start_years):
            # Filter data for this start year
            mask = [j for j, x in enumerate(start_401k_years) if x == start_year]
            if len(mask) > 1:  # Only draw lines if there are multiple points
                x_line = [start_401k_years[j] for j in mask]
                y_line = [withdrawal_years[j] for j in mask]
                z_line = [net_wealth_impacts[j] for j in mask]
                
                # Sort by withdrawal years for proper line connection
                sorted_indices = sorted(range(len(y_line)), key=lambda k: y_line[k])
                x_sorted = [x_line[i] for i in sorted_indices]
                y_sorted = [y_line[i] for i in sorted_indices]
                z_sorted = [z_line[i] for i in sorted_indices]
                
                # Draw line connecting points
                ax.plot(x_sorted, y_sorted, z_sorted, 
                       color=colors[i], linewidth=2, alpha=0.7, 
                       label=f'Start {start_year}')
        
        # Add scatter plot on top
        scatter = ax.scatter(start_401k_years, withdrawal_years, net_wealth_impacts, 
                           c=net_wealth_impacts, cmap='viridis', s=50, alpha=0.8)
        
        ax.set_xlabel('401K Start Year')
        ax.set_ylabel('Number of Years for 401K Withdrawal')
        ax.set_zlabel('Net Wealth Impact ($)')
        ax.set_title(f'3-D Visualization: 401K Withdrawal Duration vs Net Wealth Impact\n(RSU withdrawal ending in {target_end_rsu_year})')
        
        # Add legend
        ax.legend()
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=20)
        cbar.set_label('Net Wealth Impact ($)')
        
        # Format z-axis labels as currency
        ax.zaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
        
        plt.tight_layout()
        
        # Add key press handler to close the window
        def on_key_press(event):
            plt.close()
        
        fig.canvas.mpl_connect('key_press_event', on_key_press)
        plt.show()
        
        # Print summary statistics
        print(f"\nSummary for RSU withdrawal ending in {target_end_rsu_year}:")
        print(f"  Best net wealth impact: ${max(net_wealth_impacts):,.0f}")
        print(f"  Worst net wealth impact: ${min(net_wealth_impacts):,.0f}")
        print(f"  Average net wealth impact: ${np.mean(net_wealth_impacts):,.0f}")
        
    else:
        print(f"\nNo simulation results found for RSU withdrawal ending in {target_end_rsu_year}")
        print(f"Available end_rsu_years: {sorted(set(result['rsu withdrawal to'] for result in simulation_record))}")
    
    return simulation_record


def compare_withdrawal_scenarios(initial_assets, annual_income_need, base_ordinary_dividend, 
                               scenario1_params, scenario2_params, horizon_year=2040):
    """
    Compare two specific withdrawal scenarios and show detailed results.
    
    Args:
        initial_assets (dict): Initial asset values
        annual_income_need (float): Annual income need
        base_ordinary_dividend (float): Base ordinary dividend income
        scenario1_params (dict): Parameters for scenario 1
        scenario2_params (dict): Parameters for scenario 2
        horizon_year (int): Year to simulate up to
        
    Returns:
        dict: Comparison results with both scenarios
    """
    global PRINT_FLAG
    original_print_flag = PRINT_FLAG
    
    print("\n" + "="*80)
    print("COMPARING TWO WITHDRAWAL SCENARIOS")
    print("="*80)
    
    # Simulate scenario 1
    print(f"\nSCENARIO 1:")
    print(f"  RSU: {scenario1_params['start_rsu_year']} to {scenario1_params['end_rsu_year']}")
    print(f"  401K: {scenario1_params['start_401K_year']} to {scenario1_params['end_401K_year']}")
    print("-" * 80)
    
    result1 = simulate_withdrawal_scenario(
        initial_assets, annual_income_need, base_ordinary_dividend,
        scenario1_params['start_401K_year'], scenario1_params['end_401K_year'],
        scenario1_params['start_rsu_year'], scenario1_params['end_rsu_year'], horizon_year
    )
    
    # Simulate scenario 2
    print(f"\nSCENARIO 2:")
    print(f"  RSU: {scenario2_params['start_rsu_year']} to {scenario2_params['end_rsu_year']}")
    print(f"  401K: {scenario2_params['start_401K_year']} to {scenario2_params['end_401K_year']}")
    print("-" * 80)
    
    result2 = simulate_withdrawal_scenario(
        initial_assets, annual_income_need, base_ordinary_dividend,
        scenario2_params['start_401K_year'], scenario2_params['end_401K_year'],
        scenario2_params['start_rsu_year'], scenario2_params['end_rsu_year'], horizon_year
    )
    
    # Compare results
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80)
    print(f"Scenario 1 Net Wealth Impact: ${result1['net_wealth_impact']:,.0f}")
    print(f"Scenario 2 Net Wealth Impact: ${result2['net_wealth_impact']:,.0f}")
    
    difference = result2['net_wealth_impact'] - result1['net_wealth_impact']
    print(f"Difference (Scenario 2 - Scenario 1): ${difference:,.0f}")
    
    if difference > 0:
        print(f"Scenario 2 is BETTER by ${difference:,.0f}")
    elif difference < 0:
        print(f"Scenario 1 is BETTER by ${abs(difference):,.0f}")
    else:
        print("Both scenarios have the SAME net wealth impact")
    
    print("="*80)
    
    # Restore original print flag
    PRINT_FLAG = original_print_flag
    
    return {
        'scenario1': result1,
        'scenario2': result2,
        'difference': difference
    }


if __name__ == "__main__":

    print("\n" + "="*80)
    print("EXAMPLE 1: EXHAUSTIVE SEARCH WITH VISUALIZATION")
    print("="*80)

    # Initial assets
    initial_assets = TestScenario['assets'].copy()
    annual_income_need = TestScenario['annual_income_needs']

    # Run exhaustive search with visualization
    simulation_results = exhaustive_search_with_visualization(
        initial_assets, annual_income_need, TestScenario['base_ordinary_dividend']
    )

    # Print asset values for the best strategy
    if simulation_results:
        best_result = max(simulation_results, key=lambda x: x['net_wealth_impact'])
        print("\nBest withdrawal strategy asset values:")
        for asset, value in best_result['final_assets'].items():
            print(f"  {asset}: ${value:,.2f}")

    # print("\n" + "="*80)
    # print("EXAMPLE 2: COMPARE TWO WITHDRAWAL STRATEGIES")
    # print("="*80)

    # # Define the two scenarios to compare
    # scenario1_params = {
    #     'start_rsu_year': 2026,
    #     'end_rsu_year': 2026,
    #     'start_401K_year': 2027,
    #     'end_401K_year': 2036
    # }
    
    # scenario2_params = {
    #     'start_rsu_year': 2026,
    #     'end_rsu_year': 2026,
    #     'start_401K_year': 2030,
    #     'end_401K_year': 2039
    # }
    
    # # Compare the two scenarios
    # comparison_results = compare_withdrawal_scenarios(
    #     initial_assets, annual_income_need, TestScenario['base_ordinary_dividend'],
    #     scenario1_params, scenario2_params
    # )
 
