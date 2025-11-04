# =============================================================================
# TAX CONFIGURATIONS FOR DIFFERENT YEARS
# =============================================================================
# This file contains tax parameters for different tax years
# To use a different year, simply import the appropriate config

import math

# Global constants
INFLATION_RATE = 0.03  # 3% annual inflation rate

# 2024 Tax Year Configuration (Base Year for Inflation Adjustments)
TAX_CONFIG_2024 = {
    "year": 2024,
    
    # Federal Standard Deductions
    "federal_standard_deduction": {
        "single": 14600,
        "married_jointly": 29200,
        "married_separately": 14600,
        "head_of_household": 21900
    },
    
    # California Standard Deductions
    "california_standard_deduction": {
        "single": 5540,
        "married_jointly": 11080,
        "married_separately": 5540,
        "head_of_household": 11080
    },
    
    # Federal Ordinary Income Tax Brackets
    "federal_ordinary_brackets": {
        "single": [
            (0, 11600, 0.10),
            (11601, 47150, 0.12),
            (47151, 100525, 0.22),
            (100526, 191950, 0.24),
            (191951, 243725, 0.32),
            (243726, 609350, 0.35),
            (609351, float('inf'), 0.37)
        ],
        "married_jointly": [
            (0, 23200, 0.10),
            (23201, 94300, 0.12),
            (94301, 201050, 0.22),
            (201051, 383900, 0.24),
            (383901, 487450, 0.32),
            (487451, 731200, 0.35),
            (731201, float('inf'), 0.37)
        ],
        "married_separately": [
            (0, 11600, 0.10),
            (11601, 47150, 0.12),
            (47151, 100525, 0.22),
            (100526, 191950, 0.24),
            (191951, 243725, 0.32),
            (243726, 365600, 0.35),
            (365601, float('inf'), 0.37)
        ],
        "head_of_household": [
            (0, 16550, 0.10),
            (16551, 63100, 0.12),
            (63101, 100500, 0.22),
            (100501, 191950, 0.24),
            (191951, 243700, 0.32),
            (243701, 609350, 0.35),
            (609351, float('inf'), 0.37)
        ]
    },
    
    # Federal Qualified Dividend / Long-Term Capital Gain Brackets
    "federal_qdi_ltcg_brackets": {
        "single": [
            (0, 47025, 0.00),
            (47026, 518900, 0.15),
            (518901, float('inf'), 0.20)
        ],
        "married_jointly": [
            (0, 94050, 0.00),
            (94051, 583750, 0.15),
            (583751, float('inf'), 0.20)
        ],
        "married_separately": [
            (0, 47025, 0.00),
            (47026, 291850, 0.15),
            (291851, float('inf'), 0.20)
        ],
        "head_of_household": [
            (0, 63100, 0.00),
            (63101, 551350, 0.15),
            (551351, float('inf'), 0.20)
        ]
    },
    
    # California State Tax Brackets
    "california_brackets": {
        "single": [
            (0, 10756, 0.01),
            (10757, 25499, 0.02),
            (25499, 40245, 0.04),
            (40245, 55866, 0.06),
            (55866, 70606, 0.08),
            (70606, 360659, 0.093),
            (360659, 432787, 0.103),
            (432787, 721314, 0.113),
            (721314, float('inf'), 0.123)
        ],
        "married_jointly": [
            (0, 21512, 0.01),
            (21513, 50998, 0.02),
            (50999, 80490, 0.04),
            (80491, 111732, 0.06),
            (111733, 141212, 0.08),
            (141213, 721318, 0.093),
            (721319, 865574, 0.103),
            (865575, 1442628, 0.113),
            (1442629, float('inf'), 0.123)
        ],
        "married_separately": [
            (0, 10756, 0.01),
            (10757, 25499, 0.02),
            (25499, 40245, 0.04),
            (40245, 55866, 0.06),
            (55866, 70606, 0.08),
            (70606, 360659, 0.093),
            (360659, 432787, 0.103),
            (432787, 721314, 0.113),
            (721314, float('inf'), 0.123)
        ],
        "head_of_household": [
            (0, 21512, 0.01),
            (21513, 50998, 0.02),
            (50999, 80490, 0.04),
            (80491, 111732, 0.06),
            (111733, 141212, 0.08),
            (141213, 721318, 0.093),
            (721319, 865574, 0.103),
            (865575, 1442628, 0.113),
            (1442629, float('inf'), 0.123)
        ]
    },
    
    # Additional Medicare Tax Thresholds
    "medicare_tax_thresholds": {
        "single": 200000,
        "married_jointly": 250000,
        "married_separately": 125000,
        "head_of_household": 200000
    },
    
    # Net Investment Income Tax Thresholds
    "niit_thresholds": {
        "single": 200000,
        "married_jointly": 250000,
        "married_separately": 125000,
        "head_of_household": 200000
    },
    
    # Social Security Taxability Thresholds
    "social_security_thresholds": {
        "married_jointly": {
            "first_threshold": 32000,
            "second_threshold": 44000
        },
        "single": {
            "first_threshold": 25000,
            "second_threshold": 34000
        },
        "head_of_household": {
            "first_threshold": 25000,
            "second_threshold": 34000
        },
        "married_separately": {
            "first_threshold": 25000,
            "second_threshold": 34000
        }
    },
    
    # Tax Rates
    "tax_rates": {
        "medicare_additional_rate": 0.009,  # 0.9%
        "niit_rate": 0.038,  # 3.8%
        "social_security_taxable_50_percent": 0.50,  # 50%
        "social_security_taxable_85_percent": 0.85   # 85%
    }
}

# 2023 Tax Year Configuration (for comparison)
TAX_CONFIG_2023 = {
    "year": 2023,
    
    # Federal Standard Deductions
    "federal_standard_deduction": {
        "single": 13850,
        "married_jointly": 27700,
        "married_separately": 13850,
        "head_of_household": 20800
    },
    
    # California Standard Deductions
    "california_standard_deduction": {
        "single": 5202,
        "married_jointly": 10404,
        "married_separately": 5202,
        "head_of_household": 10404
    },
    
    # Federal Ordinary Income Tax Brackets
    "federal_ordinary_brackets": {
        "single": [
            (0, 11000, 0.10),
            (11001, 44725, 0.12),
            (44726, 95375, 0.22),
            (95376, 182100, 0.24),
            (182101, 231250, 0.32),
            (231251, 578125, 0.35),
            (578126, float('inf'), 0.37)
        ],
        "married_jointly": [
            (0, 22000, 0.10),
            (22001, 89450, 0.12),
            (89451, 190750, 0.22),
            (190751, 364200, 0.24),
            (364201, 462500, 0.32),
            (462501, 693750, 0.35),
            (693751, float('inf'), 0.37)
        ],
        "married_separately": [
            (0, 11000, 0.10),
            (11001, 44725, 0.12),
            (44726, 95375, 0.22),
            (95376, 182100, 0.24),
            (182101, 231250, 0.32),
            (231251, 346875, 0.35),
            (346876, float('inf'), 0.37)
        ],
        "head_of_household": [
            (0, 15700, 0.10),
            (15701, 59850, 0.12),
            (59851, 95350, 0.22),
            (95351, 182100, 0.24),
            (182101, 231250, 0.32),
            (231251, 578100, 0.35),
            (578101, float('inf'), 0.37)
        ]
    },
    
    # Federal Qualified Dividend / Long-Term Capital Gain Brackets
    "federal_qdi_ltcg_brackets": {
        "single": [
            (0, 44625, 0.00),
            (44626, 492300, 0.15),
            (492301, float('inf'), 0.20)
        ],
        "married_jointly": [
            (0, 89250, 0.00),
            (89251, 553850, 0.15),
            (553851, float('inf'), 0.20)
        ],
        "married_separately": [
            (0, 44625, 0.00),
            (44626, 276900, 0.15),
            (276901, float('inf'), 0.20)
        ],
        "head_of_household": [
            (0, 59750, 0.00),
            (59751, 523050, 0.15),
            (523051, float('inf'), 0.20)
        ]
    },
    
    # California State Tax Brackets
    "california_brackets": {
        "single": [
            (0, 10099, 0.01),
            (10100, 23942, 0.02),
            (23943, 37788, 0.04),
            (37789, 52455, 0.06),
            (52456, 66295, 0.08),
            (66296, 338639, 0.093),
            (338640, 406364, 0.103),
            (406365, 677275, 0.113),
            (677276, float('inf'), 0.123)
        ],
        "married_jointly": [
            (0, 20198, 0.01),
            (20199, 47884, 0.02),
            (47885, 75576, 0.04),
            (75577, 104910, 0.06),
            (104911, 132590, 0.08),
            (132591, 677278, 0.093),
            (677279, 812728, 0.103),
            (812729, 1354550, 0.113),
            (1354551, float('inf'), 0.123)
        ],
        "married_separately": [
            (0, 10099, 0.01),
            (10100, 23942, 0.02),
            (23943, 37788, 0.04),
            (37789, 52455, 0.06),
            (52456, 66295, 0.08),
            (66296, 338639, 0.093),
            (338640, 406364, 0.103),
            (406365, 677275, 0.113),
            (677276, float('inf'), 0.123)
        ],
        "head_of_household": [
            (0, 20198, 0.01),
            (20199, 47884, 0.02),
            (47885, 75576, 0.04),
            (75577, 104910, 0.06),
            (104911, 132590, 0.08),
            (132591, 677278, 0.093),
            (677279, 812728, 0.103),
            (812729, 1354550, 0.113),
            (1354551, float('inf'), 0.123)
        ]
    },
    
    # Additional Medicare Tax Thresholds (same as 2024)
    "medicare_tax_thresholds": {
        "single": 200000,
        "married_jointly": 250000,
        "married_separately": 125000,
        "head_of_household": 200000
    },
    
    # Net Investment Income Tax Thresholds (same as 2024)
    "niit_thresholds": {
        "single": 200000,
        "married_jointly": 250000,
        "married_separately": 125000,
        "head_of_household": 200000
    },
    
    # Social Security Taxability Thresholds (same as 2024)
    "social_security_thresholds": {
        "married_jointly": {
            "first_threshold": 32000,
            "second_threshold": 44000
        },
        "single": {
            "first_threshold": 25000,
            "second_threshold": 34000
        },
        "head_of_household": {
            "first_threshold": 25000,
            "second_threshold": 34000
        },
        "married_separately": {
            "first_threshold": 25000,
            "second_threshold": 34000
        }
    },
    
    # Tax Rates (same as 2024)
    "tax_rates": {
        "medicare_additional_rate": 0.009,  # 0.9%
        "niit_rate": 0.038,  # 3.8%
        "social_security_taxable_50_percent": 0.50,  # 50%
        "social_security_taxable_85_percent": 0.85   # 85%
    }
}

def adjust_amount_for_inflation(amount, years_from_base=0, inflation_rate=None):
    """
    Adjust a dollar amount for inflation over multiple years.
    Args:
        amount (float): Original dollar amount
        years_from_base (int): Number of years from base year (2024)
        inflation_rate (float or None): Custom annual inflation rate (if provided)
    Returns:
        int: Inflation-adjusted amount, rounded to nearest dollar
    """
    if years_from_base <= 0:
        return int(amount)
    rate = inflation_rate if inflation_rate is not None else INFLATION_RATE
    cumulative_inflation = (1 + rate) ** years_from_base
    adjusted_amount = amount * cumulative_inflation
    return int(round(adjusted_amount))

def adjust_brackets_for_inflation(brackets, years_from_base=0, inflation_rate=None):
    """
    Adjust tax brackets for inflation.
    Args:
        brackets (list): List of tax brackets as tuples (min, max, rate)
        years_from_base (int): Number of years from base year
        inflation_rate (float or None): Custom annual inflation rate (if provided)
    Returns:
        list: Inflation-adjusted brackets
    """
    adjusted_brackets = []
    for bracket in brackets:
        min_income, max_income, rate = bracket
        adjusted_min = adjust_amount_for_inflation(min_income, years_from_base, inflation_rate)
        if max_income == float('inf'):
            adjusted_max = float('inf')
        else:
            adjusted_max = adjust_amount_for_inflation(max_income, years_from_base, inflation_rate)
        adjusted_brackets.append((adjusted_min, adjusted_max, rate))
    return adjusted_brackets

def adjust_deductions_for_inflation(deductions_dict, years_from_base=0, inflation_rate=None):
    """
    Adjust standard deductions for inflation.
    Args:
        deductions_dict (dict): Dictionary of deductions by filing status
        years_from_base (int): Number of years from base year
        inflation_rate (float or None): Custom annual inflation rate (if provided)
    Returns:
        dict: Inflation-adjusted deductions
    """
    adjusted_deductions = {}
    for filing_status, amount in deductions_dict.items():
        adjusted_deductions[filing_status] = adjust_amount_for_inflation(
            amount, years_from_base, inflation_rate
        )
    return adjusted_deductions

def adjust_thresholds_for_inflation(thresholds_dict, years_from_base=0, inflation_rate=None):
    """
    Adjust tax thresholds for inflation.
    Args:
        thresholds_dict (dict): Dictionary of thresholds
        years_from_base (int): Number of years from base year
        inflation_rate (float or None): Custom annual inflation rate (if provided)
    Returns:
        dict: Inflation-adjusted thresholds
    """
    adjusted_thresholds = {}
    for key, value in thresholds_dict.items():
        if isinstance(value, dict):
            adjusted_thresholds[key] = adjust_thresholds_for_inflation(
                value, years_from_base, inflation_rate
            )
        else:
            adjusted_thresholds[key] = adjust_amount_for_inflation(
                value, years_from_base, inflation_rate
            )
    return adjusted_thresholds

def generate_future_tax_config(target_year, inflation_rate=None, base_year=2024):
    """
    Generate tax configuration for a future year based on inflation adjustments.
    Args:
        target_year (int): Target tax year
        inflation_rate (float or None): Custom annual inflation rate (if provided)
        base_year (int): Base year for calculations (default: 2024)
    Returns:
        dict: Tax configuration for the target year
    """
    if target_year <= base_year:
        return get_tax_config(target_year)
    years_from_base = target_year - base_year
    base_config = TAX_CONFIG_2024.copy()
    rate = inflation_rate if inflation_rate is not None else INFLATION_RATE
    future_config = {
        "year": target_year,
        "inflation_rate_used": rate,
        "base_year": base_year
    }
    future_config["federal_standard_deduction"] = adjust_deductions_for_inflation(
        base_config["federal_standard_deduction"], years_from_base, rate
    )
    future_config["california_standard_deduction"] = adjust_deductions_for_inflation(
        base_config["california_standard_deduction"], years_from_base, rate
    )
    future_config["federal_ordinary_brackets"] = {}
    for filing_status, brackets in base_config["federal_ordinary_brackets"].items():
        future_config["federal_ordinary_brackets"][filing_status] = adjust_brackets_for_inflation(
            brackets, years_from_base, rate
        )
    future_config["federal_qdi_ltcg_brackets"] = {}
    for filing_status, brackets in base_config["federal_qdi_ltcg_brackets"].items():
        future_config["federal_qdi_ltcg_brackets"][filing_status] = adjust_brackets_for_inflation(
            brackets, years_from_base, rate
        )
    future_config["california_brackets"] = {}
    for filing_status, brackets in base_config["california_brackets"].items():
        future_config["california_brackets"][filing_status] = adjust_brackets_for_inflation(
            brackets, years_from_base, rate
        )
    future_config["medicare_tax_thresholds"] = adjust_thresholds_for_inflation(
        base_config["medicare_tax_thresholds"], years_from_base, rate
    )
    future_config["niit_thresholds"] = adjust_thresholds_for_inflation(
        base_config["niit_thresholds"], years_from_base, rate
    )
    future_config["social_security_thresholds"] = adjust_thresholds_for_inflation(
        base_config["social_security_thresholds"], years_from_base, rate
    )
    future_config["tax_rates"] = base_config["tax_rates"].copy()
    return future_config

def get_tax_config(year, inflation_rate=None):
    """
    Returns the tax configuration for the specified year.
    For future years, generates inflation-adjusted configurations.
    Args:
        year (int): Tax year (e.g., 2023, 2024, 2025, 2030, etc.)
        inflation_rate (float or None): Custom annual inflation rate (if provided)
    Returns:
        dict: Tax configuration for the specified year
    """
    known_configs = {
        2023: TAX_CONFIG_2023,
        2024: TAX_CONFIG_2024
    }
    if year in known_configs and inflation_rate is None:
        return known_configs[year]
    elif year > 2024:
        return generate_future_tax_config(year, inflation_rate=inflation_rate)
    elif year in known_configs and inflation_rate is not None:
        # Allow inflation override for base years
        return generate_future_tax_config(year, inflation_rate=inflation_rate, base_year=year)
    else:
        print(f"Warning: Tax configuration for year {year} not found. Using 2024 configuration.")
        return TAX_CONFIG_2024

def get_available_tax_years():
    """
    Returns a list of available tax years with configurations.
    
    Returns:
        list: List of available tax years
    """
    return [2023, 2024]

def print_inflation_adjustment_example():
    """
    Print an example of how inflation adjustments work.
    """
    print("INFLATION ADJUSTMENT EXAMPLE")
    print("="*50)
    
    # Example: 2025 with 3% inflation
    config_2025 = get_tax_config(2025)
    
    print(f"2025 Tax Configuration (3% annual inflation from 2024):")
    print(f"Federal Standard Deduction (Single): ${config_2025['federal_standard_deduction']['single']:,}")
    print(f"Federal Standard Deduction (Married): ${config_2025['federal_standard_deduction']['married_jointly']:,}")
    
    print(f"\nFederal Tax Brackets (Single) - 2025:")
    for min_income, max_income, rate in config_2025['federal_ordinary_brackets']['single']:
        if max_income == float('inf'):
            print(f"  ${min_income:,} and up: {rate*100:.0f}%")
        else:
            print(f"  ${min_income:,} - ${max_income:,}: {rate*100:.0f}%")
    
    print(f"\nCapital Gains Brackets (Single) - 2025:")
    for min_income, max_income, rate in config_2025['federal_qdi_ltcg_brackets']['single']:
        if max_income == float('inf'):
            print(f"  ${min_income:,} and up: {rate*100:.0f}%")
        else:
            print(f"  ${min_income:,} - ${max_income:,}: {rate*100:.0f}%")

# Default configuration (currently 2024)
TAX_CONFIG = TAX_CONFIG_2024

if __name__ == "__main__":
    print_inflation_adjustment_example() 