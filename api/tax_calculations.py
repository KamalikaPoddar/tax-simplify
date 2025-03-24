"""
Tax Calculation Module

This module handles the core tax calculation logic for both old and new tax regimes
in India. It implements various tax calculation rules, deductions, and exemptions
as per the Indian Income Tax Act.

Key Functions:
- calculate_tax_from_slabs: Core function to calculate tax based on income slabs
- calculate_old_regime_tax: Calculates tax under the old regime with all applicable deductions
- calculate_new_regime_tax: Calculates tax under the new regime with simplified structure

The module works in conjunction with tax_slabs_data.py for tax slab information
and deductions.py for specific deduction calculations.
"""

import logging
from decimal import Decimal
from typing import List, Dict, Union, Optional, Any, Tuple
from .tax_slabs_data import get_tax_slabs, get_rebate_87a, get_surcharge_rates, get_standard_deduction # Import from tax_slabs_data
from .deductions import record_ded # Import from deductions

logger = logging.getLogger(__name__) # Get logger for this module

def calculate_tax_from_slabs(taxable_income: Decimal, tax_slabs: List[Dict[str, Union[Decimal, float, None]]]) -> Decimal:
    """
    Calculate tax amount based on income slabs.
    
    This function implements the progressive tax calculation logic where different
    tax rates apply to different portions of income as per the slab structure.
    
    Args:
        taxable_income (Decimal): Total taxable income after all deductions
        tax_slabs (List[Dict]): List of tax slabs with their limits and rates
            Each slab is a dict with keys:
            - 'limit': Upper limit of the slab (None for highest slab)
            - 'rate': Tax rate for this slab as decimal (e.g., 0.05 for 5%)
    
    Returns:
        Decimal: Calculated tax amount before cess and surcharge
    
    Example:
        >>> slabs = [
        ...     {'limit': 250000, 'rate': 0},
        ...     {'limit': 500000, 'rate': 0.05},
        ...     {'limit': None, 'rate': 0.20}
        ... ]
        >>> calculate_tax_from_slabs(Decimal('600000'), slabs)
        Decimal('32500.00')  # (250000 * 0) + (250000 * 0.05) + (100000 * 0.20)
    """
    tax_amount = Decimal('0.00')
    last_limit = Decimal('0.00')

    for slab in tax_slabs:
        limit = slab.get('limit')
        rate = Decimal(str(slab.get('rate', 0)))  # Ensure rate is Decimal

        if limit is None:  # Last slab with no upper limit
            taxable_amount_in_slab = max(0, taxable_income - last_limit)
        else:
            slab_limit = Decimal(str(limit))  # Ensure limit is Decimal
            taxable_amount_in_slab = max(0, min(taxable_income, slab_limit) - last_limit)
            last_limit = slab_limit

        tax_amount += taxable_amount_in_slab * rate

    return tax_amount

def calculate_old_regime_tax(
    input_data, # Type hint will be model class name 'TaxInput' later in app.py
    tax_data: Dict[str, Any]
) -> Tuple[Decimal, Decimal, Dict[str, Any]]:
    """
    Calculate tax under the old regime with detailed deduction tracking.
    
    This function implements the comprehensive tax calculation logic for the old
    tax regime, including all applicable deductions and exemptions.
    
    Args:
        input_data: TaxInput object containing all taxpayer details and deductions
        tax_data (Dict[str, Any]): Tax configuration data including slab rates
    
    Returns:
        Tuple containing:
        - Decimal: Final tax amount after all deductions
        - Decimal: Taxable income after all deductions
        - Dict[str, Any]: Detailed breakdown of all applied deductions
            Each deduction entry contains:
            - 'used': Amount actually used
            - 'limit': Maximum allowed limit
            - 'remaining_capacity': Unused capacity
            - 'estimated_tax_saving_if_fully_used': Potential tax saving
            - 'tax_saved_from_used_approx': Actual tax saved
    
    The function processes deductions in the following order:
    1. Standard Deduction
    2. Section 80C deductions
    3. Home loan interest (Section 24b)
    4. Additional interest for first-time buyers (80EEA)
    5. Health insurance premium (80D)
    6. HRA exemption
    7. Other deductions (80CCD, 80G, etc.)
    """
    from .deductions import calculate_hra_exemption, calculate_section24b_deduction, calculate_80eea_deduction, calculate_80c_deduction # Import deduction functions here to avoid circular import issues
    deductions = {}
    total_deductions = Decimal("0")
    taxable_income = input_data.income

    # Standard Deduction
    standard_ded = Decimal(str(get_standard_deduction(input_data.assessment_year) or "0"))
    if input_data.basic_salary > 0:
        deductions["standard_deduction"] = record_ded("Standard Deduction", standard_ded, standard_ded, taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)
        taxable_income -= standard_ded if taxable_income > standard_ded else Decimal("0")
        total_deductions += standard_ded

    # Section 80C
    limit_80c = Decimal("150000")
    total_80c_eligible = input_data.total_80c_investments + input_data.home_loan_principal_80c # Combine all 80C components
    deductable_80c = min(limit_80c, total_80c_eligible, taxable_income)
    taxable_income -= deductable_80c
    deductions["80c"] = record_ded("80C (including Home Loan Principal)", deductable_80c, limit_80c, taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)
    total_deductions += deductable_80c

    # Section 24b - Home Loan Interest
    section24b_deduction = calculate_section24b_deduction(input_data.home_loan_interest, input_data.property_self_occupied)
    deductions["24b_home_loan_interest"] = record_ded("24b Home Loan Interest", section24b_deduction, "200000", taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate) # Using "200000" as string limit
    taxable_income -= section24b_deduction
    total_deductions += section24b_deduction

    # Section 80EEA - Additional Interest for First-Time Buyers
    section80eea_deduction = calculate_80eea_deduction(input_data.first_time_home_buyer, input_data.home_loan_interest)
    deductions["80eea_home_loan_interest"] = record_ded("80EEA Home Loan Interest", section80eea_deduction, "150000", taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate) # Using "150000" as string limit
    taxable_income -= section80eea_deduction
    total_deductions += section80eea_deduction

    # Section 80D (Health Insurance)
    from .tax_slabs_data import get_80D_limits # Import get_80D_limits here to avoid circular import issues
    if input_data.health_insurance_self_parents > 0:
        d80_limits = get_80D_limits(input_data.assessment_year, input_data.age)
        if d80_limits:
            d80_limit = Decimal(str(d80_limits['self']))
            d80_used = min(input_data.health_insurance_self_parents, d80_limit, taxable_income)
            taxable_income -= d80_used
            total_deductions += d80_used
            deductions["80d_health_insurance"] = record_ded("80D", d80_used, d80_limit, taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)
        else:
            deductions["80d_health_insurance"] = {
                "used": "0",
                "limit": "Check 80D Limits, check tax_slabs_data.json",
                "remaining_capacity": "Check 80D Limits, check tax_slabs_data.json",
                "estimated_tax_saving_if_fully_used": "Check 80D Limits, check tax_slabs_data.json",
                "tax_saved_from_used_approx": "Check 80D Limits, check tax_slabs_data.json"
            }

    # HRA Exemption
    if input_data.has_hra and input_data.basic_salary > 0 and input_data.hra_received > 0 and input_data.rent > 0:
        hra_limit = calculate_hra_exemption(input_data.city_type, input_data.basic_salary, input_data.rent, input_data.hra_received)
        hra_exemption = min(input_data.hra_received, hra_limit, taxable_income)

        taxable_income -= hra_exemption
        total_deductions += hra_exemption

        deductions["hra_exemption"] = record_ded("HRA", hra_exemption, input_data.hra_received,taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)
    else:
        deductions["hra_exemption"] = {
            "used": "0",
            "limit": "0",
            "remaining_capacity": "0",
            "estimated_tax_saving_if_fully_used": "0",
            "tax_saved_from_used_approx": "0"
        }

    # ... (rest of the deductions - 80E, 80G, 80GG, 80DDB, 80CCD(1), 80CCD(2), 80TTA/80TTB) ...
    from .deductions import calculate_80e_deduction, calculate_80g_deduction, calculate_80gg_deduction, calculate_80ddb_deduction, calculate_80ccd1_deduction, calculate_80ccd2_deduction, calculate_80tta_deduction, calculate_80ttb_deduction # Import remaining deduction functions here to avoid circular import issues
    # Section 80E - Education Loan Interest
    if input_data.student_loan_interest > 0:
        section80e_deduction = calculate_80e_deduction(input_data.student_loan_interest)
        deductions["80e_education_loan_interest"] = record_ded("80E", section80e_deduction, "No Limit", taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)
        taxable_income -= section80e_deduction
        total_deductions += section80e_deduction

    # Section 80G - Donations
    if input_data.donations_80g > 0:
        section80g_deduction = calculate_80g_deduction(input_data.donations_80g)
        #Basic implementation consider 50 % limit
        used_donations = min(section80g_deduction/Decimal("2.0"),taxable_income ) # Assuming 50% limit for simplicity
        taxable_income -= used_donations
        deductions["80g_donations"] = record_ded("80G", used_donations,  "50% Subject to AGI Limit", taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)
        total_deductions += used_donations

    #Section 80GG - Rent Paid
    if input_data.is_exempted_under_80gge and input_data.rent > 0 and not input_data.has_hra:
         section80gg_deduction = calculate_80gg_deduction(input_data.income, input_data.rent)
         gg_ded = min(section80gg_deduction, taxable_income)
         deductions["80gg_rent_paid"] = record_ded("80GG - Rent Paid", gg_ded, "60000", taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate) # Using "60000" as string limit
         taxable_income -= gg_ded
         total_deductions += gg_ded

     #Section 80DDB Section
    if input_data.medical_treatment_80ddb > 0:
        section80ddb_deduction = calculate_80ddb_deduction(input_data.age, input_data.medical_treatment_80ddb)
        cap_ill = Decimal("100000.0") if input_data.age >= 60 else Decimal("40000.0") # Redundant, calculate_80ddb_deduction already handles limit based on age
        use_ill = min(cap_ill, section80ddb_deduction, taxable_income) # Redundant, section80ddb_deduction already handles limit
        taxable_income -= use_ill
        total_deductions += use_ill
        deductions['80DDB - Critical Illness'] = record_ded('80DDB - Critical Illness', use_ill, cap_ill, taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)

    # Section 80CCD(1) Employee Contribution to NPS
    if input_data.nps_80ccd1 > 0:
         section80ccd1_deduction = calculate_80ccd1_deduction(input_data.nps_80ccd1)
         nps_1_l = min(Decimal("150000.0"), section80ccd1_deduction, taxable_income) # Redundant, calculate_80ccd1_deduction already handles limit
         taxable_income -= nps_1_l
         total_deductions += nps_1_l

         deductions['80CCD(1) - NPS'] = record_ded('80CCD(1) - NPS', input_data.nps_80ccd1, Decimal("150000.0"), taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)


     # Section  Employer Contribution to NPS
    if input_data.employer_nps_80ccd2 > 0:
       section80ccd2_deduction = calculate_80ccd2_deduction(input_data.basic_salary, input_data.employer_nps_80ccd2)
       nps_2_l = min( Decimal("0.10") * input_data.basic_salary if input_data.basic_salary > 0 else 0, section80ccd2_deduction, taxable_income) # Redundant, calculate_80ccd2_deduction already handles limit
       taxable_income -= nps_2_l
       total_deductions += nps_2_l

       deductions['80CCD(2) - Employer NPS'] = record_ded('80CCD(2) - Employer NPS', input_data.employer_nps_80ccd2, "10% of Basic Salary", taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)

     #80 TTA and TTB dependign on age, so 1 or the other
    if input_data.age < 60:
        section80tta_deduction = calculate_80tta_deduction(input_data.age, input_data.savings_interest_80tta)
        tta_limit = Decimal("10000.0") # Redundant, calculate_80tta_deduction already handles limit
        use_tta = min(tta_limit, section80tta_deduction, taxable_income) # Redundant, calculate_80tta_deduction already handles limit
        taxable_income -= use_tta
        total_deductions+= use_tta

        deductions['80TTA - Savings Interest'] = record_ded('80TTA - Savings Interest', input_data.savings_interest_80tta, tta_limit, taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)

    else:
        section80ttb_deduction = calculate_80ttb_deduction(input_data.age, input_data.interest_income_80ttb)
        ttb_limit = Decimal("50000.0") # Redundant, calculate_80ttb_deduction already handles limit
        use_ttb = min(ttb_limit, section80ttb_deduction, taxable_income) # Redundant, calculate_80ttb_deduction already handles limit
        taxable_income -= use_ttb
        total_deductions+= use_ttb

        deductions['80TTB - Senior Interest'] = record_ded('80TTB - Senior Interest', input_data.interest_income_80ttb, ttb_limit, taxable_income, input_data.assessment_year, input_data.age, tax_data, input_data.tax_rate)

    if taxable_income < 0:
         taxable_income = Decimal("0")

    tax = calculate_tax_for_income(taxable_income, input_data.assessment_year, input_data.age) #calculate tax now
    deduction_breakdown = deductions

    return tax.quantize(Decimal("0.01")), taxable_income.quantize(Decimal("0.01")), deduction_breakdown


def calculate_new_regime_tax(
    income: Decimal,
    gender: str,
    basic_salary: Decimal = Decimal("0.0"),
    assessment_year: str = "2023-24"
) -> tuple[Decimal, Decimal]:
    """
    Calculates income tax under the new regime.
    
    This function implements the simplified tax calculation logic for the new
    tax regime, with reduced tax rates and exemptions.
    
    Args:
        income (Decimal): Total income
        gender (str): Taxpayer's gender
        basic_salary (Decimal, optional): Basic salary for standard deduction. Defaults to Decimal("0.0").
        assessment_year (str, optional): Assessment year. Defaults to "2023-24".
    
    Returns:
        tuple[Decimal, Decimal]: Tax amount and taxable income
    """
    try:
        # Get standard deduction if applicable
        standard_deduction = Decimal(str(get_standard_deduction(assessment_year) or "50000.0"))
        taxable_income = income - (standard_deduction if basic_salary > 0 else Decimal("0"))
        taxable_income = max(Decimal("0"), taxable_income)

        # Get tax slabs for new regime
        slabs = get_tax_slabs(assessment_year, "new_regime")
        if not slabs:
            logger.warning("No tax slabs found for new regime, using default slabs")
            slabs = [
                {"limit": Decimal("300000"), "rate": 0.0},
                {"limit": Decimal("600000"), "rate": 0.05},
                {"limit": Decimal("900000"), "rate": 0.10},
                {"limit": Decimal("1200000"), "rate": 0.15},
                {"limit": Decimal("1500000"), "rate": 0.20},
                {"limit": None, "rate": 0.30}
            ]

        # Calculate basic tax
        basic_tax = calculate_tax_from_slabs(taxable_income, slabs)

        # Apply surcharge if applicable
        surcharge_rates = get_surcharge_rates(assessment_year)
        surcharge_rate = Decimal("0.0")
        if surcharge_rates:
            for income_limit_str in sorted(surcharge_rates, reverse=True, key=int):
                income_limit = int(income_limit_str)
                if income > income_limit:
                    surcharge_rate = Decimal(str(surcharge_rates[income_limit_str]))
                    break

        tax_plus_surcharge = basic_tax * (1 + surcharge_rate)

        # Add health and education cess (4%)
        cess = Decimal("0.04") * tax_plus_surcharge
        total_tax = tax_plus_surcharge + cess

        return total_tax.quantize(Decimal("0.01")), taxable_income.quantize(Decimal("0.01"))