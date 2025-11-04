# =============================================================================
# TAX ESTIMATOR - FEDERAL AND CALIFORNIA STATE TAX CALCULATOR
# =============================================================================
# This module calculates federal and California state taxes for various income sources
# including wages, dividends, capital gains, rental income, and retirement distributions
# 
# DEFAULT: 2023 Tax Year
# To use 2024: import get_tax_config from tax_configs and pass get_tax_config(2024)

from tax_configs import TAX_CONFIG, get_tax_config, get_available_tax_years


def get_federal_tax(taxable_income, filing_status, qualified_dividend_capital_gain_income=0, tax_config=None):
    """
    Estimates Federal Income Tax for the specified tax year.
    Applies standard ordinary income tax brackets and qualified dividend/long-term
    capital gain rates.
    
    Args:
        taxable_income (float): Total taxable income
        filing_status (str): Filing status ("single", "married_jointly", "married_separately", "head_of_household")
        qualified_dividend_capital_gain_income (float): Amount of qualified dividends and long-term capital gains
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)
        
    Returns:
        float: Estimated federal tax amount
    """
    if tax_config is None:
        tax_config = TAX_CONFIG
    
    tax_owed = 0.0

    # Get tax brackets from configuration
    federal_ordinary_brackets = tax_config["federal_ordinary_brackets"]
    federal_qdi_ltcg_brackets = tax_config["federal_qdi_ltcg_brackets"]

    # --- Calculate tax on Qualified Dividends and Long-Term Capital Gains (QDI/LTCG) ---
    # QDI/LTCG are taxed at preferential rates based on your TOTAL taxable income level.
    # The rate is determined by which bracket your total taxable income falls into.
    qdi_ltcg_tax = 0.0

    # The actual income that is subject to QDI/LTCG rates cannot exceed total taxable income
    taxable_qdi_ltcg = min(qualified_dividend_capital_gain_income, taxable_income)

    if filing_status in federal_qdi_ltcg_brackets:
        # Find the appropriate rate based on total taxable income
        qdi_ltcg_rate = 0.0
        
        for lower_bound, upper_bound, rate in federal_qdi_ltcg_brackets[filing_status]:
            if lower_bound <= taxable_income <= upper_bound:
                qdi_ltcg_rate = rate
                break
            elif lower_bound <= taxable_income and upper_bound == float('inf'):
                qdi_ltcg_rate = rate
                break
        
        # Apply the determined rate to the QDI/LTCG amount
        qdi_ltcg_tax = taxable_qdi_ltcg * qdi_ltcg_rate
        
    else:
        print(f"Warning: Federal filing status '{filing_status}' not recognized for QDI/LTCG tax calculation.")

    # --- Calculate tax on Ordinary Income ---
    # The remaining taxable income (total taxable income minus QDI/LTCG taxed preferentially)
    # is taxed at ordinary income rates.
    ordinary_taxable_income = taxable_income - taxable_qdi_ltcg

    if filing_status in federal_ordinary_brackets:
        current_ordinary_income_to_tax = ordinary_taxable_income
        for lower_bound, upper_bound, rate in federal_ordinary_brackets[filing_status]:
            if current_ordinary_income_to_tax <= 0:
                break

            # The amount of ordinary income that falls into this specific bracket
            amount_in_bracket = min(current_ordinary_income_to_tax, upper_bound - lower_bound + 1)
            tax_owed += amount_in_bracket * rate
            current_ordinary_income_to_tax -= amount_in_bracket
    else:
        print(f"Warning: Federal filing status '{filing_status}' not recognized for ordinary income tax calculation.")


    fed_tax_estimate = round(tax_owed + qdi_ltcg_tax, 2)
    return fed_tax_estimate


def get_california_state_tax(taxable_income, filing_status, tax_config=None):
    """
    Estimates California State Income Tax for the specified tax year.
    California taxes all income (including capital gains and qualified dividends) as ordinary income.
    Does NOT include the 1% Mental Health Services Tax on income over $1,000,000 for simplicity.
    
    Args:
        taxable_income (float): Total taxable income
        filing_status (str): Filing status ("single", "married_jointly", "married_separately", "head_of_household")
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)
        
    Returns:
        float: Estimated California state tax amount
    """
    if tax_config is None:
        tax_config = TAX_CONFIG
    
    tax_owed = 0.0

    # Get California tax brackets from configuration
    california_brackets = tax_config["california_brackets"]

    if filing_status in california_brackets:
        current_income_to_tax = taxable_income
        for lower_bound, upper_bound, rate in california_brackets[filing_status]:
            if current_income_to_tax <= 0:
                break

            # Amount of income within the current bracket
            amount_in_bracket = min(current_income_to_tax, upper_bound - lower_bound + 1)
            tax_owed += amount_in_bracket * rate
            current_income_to_tax -= amount_in_bracket
    else:
        print(f"Warning: California filing status '{filing_status}' not recognized for tax calculation.")
        return 0

    return round(tax_owed, 2)


def calculate_medicare_tax(wages, filing_status, tax_config=None):
    """
    Calculates Additional Medicare Tax (Form 8959) for the specified tax year.
    
    Args:
        wages (float): W-2 wages and self-employment income
        filing_status (str): Filing status
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)
        
    Returns:
        float: Additional Medicare Tax amount
    """
    if tax_config is None:
        tax_config = TAX_CONFIG
    
    # Get thresholds and rates from configuration
    thresholds = tax_config["medicare_tax_thresholds"]
    medicare_rate = tax_config["tax_rates"]["medicare_additional_rate"]
    
    threshold = thresholds.get(filing_status, 0)
    if threshold == 0:
        print(f"Warning: Medicare tax threshold not defined for filing status '{filing_status}'.")
        return 0
    
    # Additional Medicare Tax is 0.9% on wages above the threshold
    excess_wages = max(0, wages - threshold)
    medicare_tax = excess_wages * medicare_rate
    
    return round(medicare_tax, 2)


def calculate_net_investment_income_tax(income_details, filing_status, federal_agi, tax_config=None):
    """
    Calculates Net Investment Income Tax (Form 8960) for the specified tax year.
    
    Args:
        income_details (dict): Income details dictionary
        filing_status (str): Filing status
        federal_agi (float): Federal Adjusted Gross Income
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)
        
    Returns:
        float: Net Investment Income Tax amount
    """
    if tax_config is None:
        tax_config = TAX_CONFIG
    
    # Get thresholds and rates from configuration
    thresholds = tax_config["niit_thresholds"]
    niit_rate = tax_config["tax_rates"]["niit_rate"]
    
    threshold = thresholds.get(filing_status, 0)
    if threshold == 0:
        print(f"Warning: NIIT threshold not defined for filing status '{filing_status}'.")
        return 0
    
    # Calculate Net Investment Income (NII)
    net_investment_income = (
        income_details.get('ordinary_dividend', 0) +  # This already includes qualified dividends
        income_details.get('short_term_capital_gain', 0) +
        income_details.get('long_term_capital_gain', 0) +
        income_details.get('rental_net_income', 0)
        # Note: 401K distributions and NCQDP are generally not considered investment income
        # Social Security benefits are also not investment income
    )
    
    # Calculate Modified Adjusted Gross Income (MAGI)
    # For most taxpayers, MAGI = AGI
    magi = federal_agi
    
    # NIIT is 3.8% on the lesser of:
    # 1. Net Investment Income, OR
    # 2. MAGI over the threshold
    excess_magi = max(0, magi - threshold)
    niit_base = min(net_investment_income, excess_magi)
    niit_tax = niit_base * niit_rate
    
    return round(niit_tax, 2)


def calculate_social_security_taxable_portion(ss_distribution, gross_income_before_ss, filing_status, tax_config=None):
    """
    Calculates the taxable portion of Social Security benefits for federal tax purposes.
    
    Args:
        ss_distribution (float): Total Social Security benefits received
        gross_income_before_ss (float): Gross income before Social Security adjustment
        filing_status (str): Filing status
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)
        
    Returns:
        float: Taxable portion of Social Security benefits
    """
    if tax_config is None:
        tax_config = TAX_CONFIG
    
    if ss_distribution <= 0:
        return 0
    
    # Get thresholds and rates from configuration
    ss_thresholds = tax_config["social_security_thresholds"]
    ss_50_rate = tax_config["tax_rates"]["social_security_taxable_50_percent"]
    ss_85_rate = tax_config["tax_rates"]["social_security_taxable_85_percent"]
    
    # "Combined income" for Social Security taxability rules
    # Combined income = AGI (before SS) + non-taxable interest + 50% of SS benefits
    combined_income = gross_income_before_ss + (ss_50_rate * ss_distribution)
    
    social_security_taxable_federal = 0
    
    if filing_status in ss_thresholds:
        thresholds = ss_thresholds[filing_status]
        first_threshold = thresholds["first_threshold"]
        second_threshold = thresholds["second_threshold"]
        
        if combined_income <= first_threshold:
            social_security_taxable_federal = 0
        elif first_threshold < combined_income <= second_threshold:
            social_security_taxable_federal = min(ss_50_rate * ss_distribution, 
                                                ss_50_rate * (combined_income - first_threshold))
        else:  # combined_income > second_threshold
            social_security_taxable_federal = min(
                ss_85_rate * ss_distribution,
                (ss_85_rate * (combined_income - second_threshold)) + (ss_50_rate * (second_threshold - first_threshold))
            )
    
    # Social Security taxable portion cannot exceed 85% of the benefits
    social_security_taxable_federal = min(social_security_taxable_federal, ss_85_rate * ss_distribution)
    social_security_taxable_federal = max(0, social_security_taxable_federal)  # ensure not negative
    
    return social_security_taxable_federal


def calculate_tax(income_details, filing_status, tax_config=None):
    """
    Calculates estimated Federal and California state tax for the specified tax year.
    
    This function handles all the income sources you mentioned:
    - Wage/salary income
    - 401K distributions (taxed as ordinary income)
    - NCQDP (Non-Qualified Deferred Compensation) distributions
    - Capital gains (both short-term and long-term)
    - Ordinary dividends
    - Qualified dividends (taxed at preferential rates federally)
    - Rental income (net income after expenses)
    - Social Security benefits (with federal taxability rules)
    
    PLUS additional taxes for high-income earners:
    - Additional Medicare Tax (Form 8959)
    - Net Investment Income Tax (Form 8960)

    Args:
        income_details (dict): A dictionary with income types and amounts:
            {
                'salary': float,                    # W-2 wage income
                'rental_net_income': float,         # Net rental income (after expenses)
                'ordinary_dividend': float,         # Non-qualified dividends
                'qualified_dividend': float,        # Qualified dividends (preferential rates)
                'short_term_capital_gain': float,   # STCG (taxed as ordinary income)
                'long_term_capital_gain': float,    # LTCG (preferential rates federally)
                '401k_distribution': float,         # Traditional 401K/IRA distributions
                'social_security_distribution': float,  # Social Security benefits
                'ncqdp_distribution': float         # Non-Qualified Deferred Compensation
            }
        filing_status (str): Filing status - "single", "married_jointly", 
                           "married_separately", or "head_of_household"
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)

    Returns:
        dict: A dictionary containing estimated federal and state tax breakdowns:
            {
                'federal_taxable_income': float,
                'estimated_federal_income_tax': float,
                'california_taxable_income': float,
                'estimated_california_state_tax': float,
                'social_security_taxable_federal_portion': float,
                'medicare_tax': float,
                'net_investment_income_tax': float,
                'total_federal_tax': float,
                'total_tax': float,
                'effective_federal_rate': float,
                'effective_california_rate': float,
                'combined_effective_rate': float
            }
    """
    if tax_config is None:
        tax_config = TAX_CONFIG

    # --- Step 1: Calculate Gross Income (before Social Security taxability rules) ---
    # Note: Ordinary dividends already include qualified dividends, so we don't add them separately
    gross_income_before_ss_adjustment = (
            income_details.get('salary', 0) +
            income_details.get('rental_net_income', 0) +
            income_details.get('ordinary_dividend', 0) +  
            income_details.get('short_term_capital_gain', 0) +
            income_details.get('long_term_capital_gain', 0) +
            income_details.get('401k_distribution', 0) +
            income_details.get('ncqdp_distribution', 0)
    )

    # --- Step 2: Determine Taxable Portion of Social Security Benefits (Federal) ---
    ss_distribution = income_details.get('social_security_distribution', 0)
    social_security_taxable_federal = calculate_social_security_taxable_portion(
        ss_distribution, gross_income_before_ss_adjustment, filing_status, tax_config
    )

    # --- Step 3: Calculate Adjusted Gross Income (AGI) ---
    # For this simplified model, AGI is essentially gross income plus the taxable portion of SS.
    # In a real scenario, AGI has more "above-the-line" deductions.
    federal_agi = gross_income_before_ss_adjustment + social_security_taxable_federal

    # --- Step 4: Determine Federal Taxable Income ---
    federal_standard_deduction = tax_config["federal_standard_deduction"]
    std_deduction_federal = federal_standard_deduction.get(filing_status, 0)
    if std_deduction_federal == 0:
        print(f"Error: Federal standard deduction not defined for filing status '{filing_status}'.")
        return None

    federal_taxable_income = max(0, federal_agi - std_deduction_federal)

    # --- Step 5: Calculate Federal Income Tax ---
    # Qualified dividends and long-term capital gains are taxed at preferential rates federally.
    # Sum them up for special treatment.
    qualified_dividends_and_LTCG_federal = (
            income_details.get('qualified_dividend', 0) +
            income_details.get('long_term_capital_gain', 0)
    )

    # Only the portion of QDI/LTCG that is actually part of taxable income gets preferential rates.
    # The amount subject to preferential rates cannot exceed the AGI (before deduction) or total QDI/LTCG.
    qualified_dividends_and_LTCG_for_tax = min(qualified_dividends_and_LTCG_federal, federal_agi)

    estimated_federal_income_tax = get_federal_tax(federal_taxable_income,
                                                   filing_status,
                                                   qualified_dividends_and_LTCG_for_tax,
                                                   tax_config)

    # --- Step 6: Calculate Additional Medicare Tax ---
    wages = income_details.get('salary', 0)
    medicare_tax = calculate_medicare_tax(wages, filing_status, tax_config)

    # --- Step 7: Calculate Net Investment Income Tax ---
    niit_tax = calculate_net_investment_income_tax(income_details, filing_status, federal_agi, tax_config)

    # --- Step 8: Calculate Total Federal Tax ---
    total_federal_tax = estimated_federal_income_tax + medicare_tax + niit_tax

    # --- Step 9: Determine California State Taxable Income ---
    # California does NOT tax Social Security benefits.
    # California has its own standard deduction.
    # All capital gains and qualified dividends are taxed as ordinary income in CA.

    california_standard_deduction = tax_config["california_standard_deduction"]
    std_deduction_ca = california_standard_deduction.get(filing_status, 0)
    if std_deduction_ca == 0:
        print(f"Error: California standard deduction not defined for filing status '{filing_status}'.")
        return None

    california_agi = gross_income_before_ss_adjustment  # SS is not taxed by CA
    california_taxable_income = max(0, california_agi - std_deduction_ca)

    # --- Step 10: Calculate California State Tax ---
    estimated_california_state_tax = get_california_state_tax(california_taxable_income, filing_status, tax_config)

    # --- Step 11: Calculate effective tax rates ---
    total_income = gross_income_before_ss_adjustment + ss_distribution
    total_tax = total_federal_tax + estimated_california_state_tax
    
    effective_federal_rate = (total_federal_tax / total_income * 100) if total_income > 0 else 0
    effective_california_rate = (estimated_california_state_tax / total_income * 100) if total_income > 0 else 0
    combined_effective_rate = (total_tax / total_income * 100) if total_income > 0 else 0

    return {
        "federal_taxable_income": round(federal_taxable_income, 2),
        "estimated_federal_income_tax": round(estimated_federal_income_tax, 2),
        "california_taxable_income": round(california_taxable_income, 2),
        "estimated_california_state_tax": round(estimated_california_state_tax, 2),
        "social_security_taxable_federal_portion": round(social_security_taxable_federal, 2),
        "medicare_tax": round(medicare_tax, 2),
        "net_investment_income_tax": round(niit_tax, 2),
        "total_federal_tax": round(total_federal_tax, 2),
        "total_tax": round(total_tax, 2),
        "effective_federal_rate": round(effective_federal_rate, 2),
        "effective_california_rate": round(effective_california_rate, 2),
        "combined_effective_rate": round(combined_effective_rate, 2),
        "total_income": round(total_income, 2)
    }


def print_tax_summary(income_details, filing_status, tax_estimates, tax_config=None):
    """
    Prints a comprehensive tax summary with all income sources and tax calculations.
    
    Args:
        income_details (dict): Income details dictionary
        filing_status (str): Filing status
        tax_estimates (dict): Tax calculation results
        tax_config (dict): Tax configuration dictionary (uses TAX_CONFIG if None)
    """
    if tax_config is None:
        tax_config = TAX_CONFIG
    
    print(f"\n{'='*60}")
    print(f"TAX ESTIMATION SUMMARY - {filing_status.replace('_', ' ').title()} - {tax_config['year']}")
    print(f"{'='*60}")
    
    print(f"\nINCOME BREAKDOWN:")
    print(f"{'Income Source':<25} {'Amount':<15}")
    print(f"{'-'*25} {'-'*15}")
    
    income_sources = {
        'Salary/Wages': income_details.get('salary', 0),
        'Rental Net Income': income_details.get('rental_net_income', 0),
        'Ordinary Dividends (Total)': income_details.get('ordinary_dividend', 0),
        '  - Qualified Dividends': income_details.get('qualified_dividend', 0),
        '  - Non-Qualified Dividends': income_details.get('ordinary_dividend', 0) - income_details.get('qualified_dividend', 0),
        'Short-term Capital Gains': income_details.get('short_term_capital_gain', 0),
        'Long-term Capital Gains': income_details.get('long_term_capital_gain', 0),
        '401K Distribution': income_details.get('401k_distribution', 0),
        'Social Security': income_details.get('social_security_distribution', 0),
        'NCQDP Distribution': income_details.get('ncqdp_distribution', 0)
    }
    
    for source, amount in income_sources.items():
        if amount > 0:
            print(f"{source:<25} ${amount:>14,.2f}")
    
    print(f"{'-'*25} {'-'*15}")
    print(f"{'TOTAL INCOME':<25} ${tax_estimates['total_income']:>14,.2f}")
    
    print(f"\nFEDERAL TAX BREAKDOWN:")
    print(f"{'Description':<35} {'Amount':<15}")
    print(f"{'-'*35} {'-'*15}")
    
    print(f"{'Federal Taxable Income':<35} ${tax_estimates['federal_taxable_income']:>14,.2f}")
    print(f"{'Federal Income Tax':<35} ${tax_estimates['estimated_federal_income_tax']:>14,.2f}")
    print(f"{'Additional Medicare Tax':<35} ${tax_estimates['medicare_tax']:>14,.2f}")
    print(f"{'Net Investment Income Tax':<35} ${tax_estimates['net_investment_income_tax']:>14,.2f}")
    print(f"{'-'*35} {'-'*15}")
    print(f"{'TOTAL FEDERAL TAX':<35} ${tax_estimates['total_federal_tax']:>14,.2f}")
    print(f"{'Federal Effective Rate':<35} {tax_estimates['effective_federal_rate']:>14.2f}%")
    
    print(f"\nCALIFORNIA STATE TAX:")
    print(f"{'California Taxable Income':<35} ${tax_estimates['california_taxable_income']:>14,.2f}")
    print(f"{'California State Tax':<35} ${tax_estimates['estimated_california_state_tax']:>14,.2f}")
    print(f"{'California Effective Rate':<35} {tax_estimates['effective_california_rate']:>14.2f}%")
    
    print(f"\nTOTAL TAX SUMMARY:")
    print(f"{'-'*35} {'-'*15}")
    print(f"{'TOTAL TAX (Federal + CA)':<35} ${tax_estimates['total_tax']:>14,.2f}")
    print(f"{'COMBINED EFFECTIVE RATE':<35} {tax_estimates['combined_effective_rate']:>14.2f}%")
    
    if income_details.get('social_security_distribution', 0) > 0:
        print(f"\nSOCIAL SECURITY TAXABILITY:")
        print(f"Total SS Benefits: ${income_details['social_security_distribution']:,.2f}")
        print(f"Taxable Portion (Federal): ${tax_estimates['social_security_taxable_federal_portion']:,.2f}")
        print(f"Taxable Percentage: {tax_estimates['social_security_taxable_federal_portion'] / income_details['social_security_distribution'] * 100:.1f}%")
    
    # Show high-income tax impact
    if tax_estimates['medicare_tax'] > 0 or tax_estimates['net_investment_income_tax'] > 0:
        print(f"\nHIGH-INCOME TAX IMPACT:")
        if tax_estimates['medicare_tax'] > 0:
            medicare_rate = tax_config["tax_rates"]["medicare_additional_rate"] * 100
            print(f"Additional Medicare Tax: ${tax_estimates['medicare_tax']:,.2f} ({medicare_rate}% on wages over threshold)")
        if tax_estimates['net_investment_income_tax'] > 0:
            niit_rate = tax_config["tax_rates"]["niit_rate"] * 100
            print(f"Net Investment Income Tax: ${tax_estimates['net_investment_income_tax']:,.2f} ({niit_rate}% on investment income)")
        total_high_income_tax = tax_estimates['medicare_tax'] + tax_estimates['net_investment_income_tax']
        print(f"Total High-Income Taxes: ${total_high_income_tax:,.2f}")


# --- Example Usage and Test Cases ---

if __name__ == "__main__":
    print("Available tax years:", get_available_tax_years())
    
    # Example 1: Your current scenario with 2023 tax year (default)
    print("\nEXAMPLE 1: Your Current Income Scenario (2023 - Default)")

 
    # my_income_scenario = {
    #     'salary': 901000, #1156486,
    #     'short_term_capital_gain': 0,
    #     'long_term_capital_gain': 119700,
    #     'rental_net_income': 0,
    #     'ordinary_dividend': 68817+1323,
    #     'qualified_dividend': 49969,
    #     '401k_distribution': 0,
    #     'social_security_distribution': 0,
    #     'ncqdp_distribution': 0
    # }

    my_income_scenario = {
        'salary': salary,
        'short_term_capital_gain': short_term_cg,
        'long_term_capital_gain': long_term_cg,
        'rental_net_income': 0,
        'ordinary_dividend': ordinary_dividend,
        'qualified_dividend': qualified_dividend,
        '401k_distribution': 0,
        'social_security_distribution': 0,
        'ncqdp_distribution': 0
    }

    my_filing_status = "married_jointly"
    tax_estimates_2023 = calculate_tax(my_income_scenario, my_filing_status)
    
    if tax_estimates_2023:
        print_tax_summary(my_income_scenario, my_filing_status, tax_estimates_2023)
    
    print("\nEXAMPLE 2: Year-over-Year Comparison (2023 vs 2024)")
    print("-" * 60)
    
    # Compare 2023 vs 2024
    tax_estimates_2023 = calculate_tax(my_income_scenario, "single", get_tax_config(2023))
    tax_estimates_2024 = calculate_tax(my_income_scenario, "single", get_tax_config(2024))
    
    if tax_estimates_2023 and tax_estimates_2024:
        print(f"{'Description':<25} {'2023':<15} {'2024':<15} {'Change':<15}")
        print(f"{'-'*25} {'-'*15} {'-'*15} {'-'*15}")
        
        print(f"{'Federal Taxable Income':<25} ${tax_estimates_2023['federal_taxable_income']:>14,.0f} ${tax_estimates_2024['federal_taxable_income']:>14,.0f} ${tax_estimates_2024['federal_taxable_income'] - tax_estimates_2023['federal_taxable_income']:>+14,.0f}")
        print(f"{'Federal Income Tax':<25} ${tax_estimates_2023['estimated_federal_income_tax']:>14,.0f} ${tax_estimates_2024['estimated_federal_income_tax']:>14,.0f} ${tax_estimates_2024['estimated_federal_income_tax'] - tax_estimates_2023['estimated_federal_income_tax']:>+14,.0f}")
        print(f"{'California State Tax':<25} ${tax_estimates_2023['estimated_california_state_tax']:>14,.0f} ${tax_estimates_2024['estimated_california_state_tax']:>14,.0f} ${tax_estimates_2024['estimated_california_state_tax'] - tax_estimates_2023['estimated_california_state_tax']:>+14,.0f}")
        print(f"{'Total Tax':<25} ${tax_estimates_2023['total_tax']:>14,.0f} ${tax_estimates_2024['total_tax']:>14,.0f} ${tax_estimates_2024['total_tax'] - tax_estimates_2023['total_tax']:>+14,.0f}")
        print(f"{'Effective Tax Rate':<25} {tax_estimates_2023['combined_effective_rate']:>14.2f}% {tax_estimates_2024['combined_effective_rate']:>14.2f}% {tax_estimates_2024['combined_effective_rate'] - tax_estimates_2023['combined_effective_rate']:>+14.2f}%")

    print("\nEXAMPLE 3: Different Filing Statuses (2024)")
    print("-" * 60)

    print("\nEXAMPLE 4: Future Year Tax Projections (Inflation-Adjusted)")
    print("-" * 60)
    
    # Example income scenario
    future_income = {
        'salary': 120000,
        'long_term_capital_gain': 25000,
        'ordinary_dividend': 6000,
        'short_term_capital_gain': 0,
        'rental_net_income': 0,
        '401k_distribution': 0,
        'social_security_distribution': 0,
        'other_income': 0
    }
    
    print("Income Scenario:")
    for key, value in future_income.items():
        if value > 0:
            print(f"  {key}: ${value:,}")
    
    # Compare different years (default inflation rate from tax_configs.py)
    years_to_project = [2024, 2025, 2030, 2035]
    print(f"\nTax Projections (Single Filer, default inflation rate):")
    print(f"{'Year':<6} {'Federal Tax':<15} {'State Tax':<15} {'Total Tax':<15} {'Effective Rate':<15}")
    print(f"{'-'*6} {'-'*15} {'-'*15} {'-'*15} {'-'*15}")
    
    for year in years_to_project:
        config = get_tax_config(year)
        tax_estimates = calculate_tax(future_income, "single", config)
        
        if tax_estimates:
            print(f"{year:<6} ${tax_estimates['estimated_federal_income_tax']:<14,.0f} "
                  f"${tax_estimates['estimated_california_state_tax']:<14,.0f} "
                  f"${tax_estimates['total_tax']:<14,.0f} "
                  f"{tax_estimates['combined_effective_rate']:<14.2f}%")
    
    print(f"\nKey Insights:")
    print(f"• Tax brackets and deductions are automatically adjusted for inflation")
    print(f"• Tax rates remain constant (not inflation-adjusted)")
    print(f"• Effective tax rates may change due to bracket creep or relief")
    print(f"• Useful for long-term financial planning and retirement projections")

    # EXAMPLE 5 removed: Custom inflation scenarios are not supported in this simplified version. 