"""
Tax Deductions Calculator Module

This module implements calculations for various tax deductions and exemptions
under the Indian Income Tax Act. It provides functions to calculate specific
deductions under different sections like 80C, 80D, HRA, etc.

Features:
- HRA exemption calculation
- Standard deduction for salaried employees
- Various Section 80 deductions:
  - 80C (Investments and payments)
  - 80D (Health insurance)
  - 80DD (Disabled dependent)
  - 80DDB (Medical treatment)
  - 80E (Education loan interest)
  - 80EEA (Housing loan interest)
  - 80G (Donations)
  - 80GG (Rent paid)
  - 80IAC (Startup investments)
  - 80TTA/TTB (Interest income)
- Professional tax deduction
- Home loan interest deduction (24b)
"""

from decimal import Decimal
from typing import Dict, Any, Union
from .tax_calculations import calculate_tax_for_income # Import calculate_tax_for_income to avoid circular import issues

def calculate_hra_exemption(city_type: str, basic_salary: Decimal, rent_paid: Decimal, hra_received: Decimal) -> Decimal:
    """
    Calculate HRA exemption as per Section 10(13A).
    
    The exemption is the minimum of:
    1. Actual HRA received
    2. Rent paid - 10% of basic salary
    3. 50% of basic salary (for metro cities) or 40% (for non-metro)
    
    Args:
        city_type (str): Type of city ('metro' or 'non-metro')
        basic_salary (Decimal): Basic salary component
        rent_paid (Decimal): Annual rent paid
        hra_received (Decimal): HRA received from employer
    
    Returns:
        Decimal: HRA exemption amount
    
    Example:
        >>> calculate_hra_exemption('metro', Decimal('50000'),
        ...                        Decimal('20000'), Decimal('25000'))
        Decimal('15000')  # min(25000, 20000-5000, 25000)
    """
    if hra_received == 0 or rent_paid == 0:
        return 0

    metro_cities = ['metro'] # Ideally, load metro cities from tax_slabs_data.json if it becomes configurable
    salary = basic_salary
    if city_type in metro_cities:
        limit_3 = 0.50 * salary
    else:
        limit_3 = 0.40 * salary

    hra_exemption = min(hra_received, rent_paid - (0.10 * salary), limit_3)
    return max(0, hra_exemption)

def calculate_80c_deduction(investments_80c: Decimal, nps_investment: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80C, 80CCC, and 80CCD(1).
    
    Combines all eligible investments and payments under section 80C
    up to the maximum limit of ₹1.5 lakhs.
    
    Args:
        investments_80c (Decimal): Total 80C eligible investments
        nps_investment (Decimal): NPS contribution under 80CCD(1)
    
    Returns:
        Decimal: Total allowed deduction under 80C
    """
    total_80c_investment = investments_80c + nps_investment
    max_80c_limit = 150000
    return min(total_80c_investment, max_80c_limit)

def calculate_80d_deduction(age: int, insurance_premium: Decimal, dependant_seniors: bool) -> Decimal:
    """
    Calculate deduction under Section 80D for medical insurance.
    
    The limits are:
    - Self & family: ₹25,000 (₹50,000 if senior citizen)
    - Parents: Additional ₹50,000 if senior citizens
    
    Args:
        age (int): Age of the taxpayer
        insurance_premium (Decimal): Total insurance premium paid
        dependant_seniors (bool): Whether dependents are senior citizens
    
    Returns:
        Decimal: Total allowed deduction under 80D
    """
    max_80d_limit_self = 25000 if age < 60 else 50000
    max_80d_limit_parents = 50000 if dependant_seniors else 0

    total_80d_deduction = min(insurance_premium, max_80d_limit_self + max_80d_limit_parents)
    return max(0, total_80d_deduction)

def calculate_80dd_deduction(disability: bool) -> Decimal:
    """
    Calculate deduction under Section 80DD for maintenance of disabled dependent.
    
    Args:
        disability (bool): Whether the dependent has a disability
    
    Returns:
        Decimal: Total allowed deduction under 80DD
    """
    if disability:
        return 75000
    return 0

def calculate_80ddb_deduction(age: int, medical_treatment_cost_80DDB: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80DDB for medical treatment of specified diseases.
    
    Args:
        age (int): Age of the taxpayer
        medical_treatment_cost_80DDB (Decimal): Medical treatment cost
    
    Returns:
        Decimal: Total allowed deduction under 80DDB
    """
    max_80ddb_limit = 40000 if age < 60 else 100000
    return min(medical_treatment_cost_80DDB, max_80ddb_limit)

def calculate_80e_deduction(student_loan_interest: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80E for interest on student loan.
    
    Args:
        student_loan_interest (Decimal): Interest paid on student loan
    
    Returns:
        Decimal: Total allowed deduction under 80E
    """
    return student_loan_interest

def calculate_80eea_deduction(first_time_home_buyer: bool, home_loan_interest: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80EEA for interest on housing loan for first-time home buyers.
    
    Args:
        first_time_home_buyer (bool): Whether the buyer is a first-time home buyer
        home_loan_interest (Decimal): Interest paid on home loan
    
    Returns:
        Decimal: Total allowed deduction under 80EEA
    """
    if first_time_home_buyer:
        max_80eea_limit = 150000
        return min(home_loan_interest, max_80eea_limit)
    return 0

def calculate_80g_deduction(donations_scientific_research: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80G for donations (assuming 100% deduction for scientific research).
    
    Args:
        donations_scientific_research (Decimal): Donations made for scientific research
    
    Returns:
        Decimal: Total allowed deduction under 80G
    """
    return donations_scientific_research

def calculate_80gg_deduction(income: Decimal, rent_paid_80gg: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80GG for rent paid.
    
    Args:
        income (Decimal): Total income
        rent_paid_80gg (Decimal): Rent paid
    
    Returns:
        Decimal: Total allowed deduction under 80GG
    """
    val1 = Decimal("60000.0")
    val2 = Decimal("0.25") * income
    val3 = rent_paid_80gg - Decimal("0.1") * income
    if val3 < 0:
        val3 = Decimal("0")
    return min(val1, val2, val3)

def calculate_80iac_deduction(startup_investment_80IAC: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80-IAC for investment in eligible startups.
    
    Args:
        startup_investment_80IAC (Decimal): Investment made in eligible startups
    
    Returns:
        Decimal: Total allowed deduction under 80-IAC
    """
    return startup_investment_80IAC

def calculate_section24b_deduction(home_loan_interest: Decimal, self_occupied_property: bool = True) -> Decimal:
    """
    Calculate deduction under Section 24b for interest on housing loan.
    
    Args:
        home_loan_interest (Decimal): Interest paid on home loan
        self_occupied_property (bool): Whether the property is self-occupied
    
    Returns:
        Decimal: Total allowed deduction under 24b
    """
    if self_occupied_property:
        max_24b_limit = 200000
        return min(home_loan_interest, max_24b_limit)
    return home_loan_interest

def calculate_standard_deduction(employment_type: str) -> Decimal:
    """
    Calculate standard deduction for salaried individuals.
    
    Args:
        employment_type (str): Type of employment
    
    Returns:
        Decimal: Standard deduction amount
    """
    if employment_type == 'salaried':
        return 50000
    return 0

def calculate_professional_tax_deduction(employment_type: str, city_type: str) -> Decimal:
    """
    Calculate professional tax deduction.
    
    Args:
        employment_type (str): Type of employment
        city_type (str): Type of city
    
    Returns:
        Decimal: Professional tax deduction amount
    """
    if employment_type == 'salaried' and city_type == 'metro':
        return 2500
    return 0

def calculate_80tta_deduction(age: int, interest_income: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80TTA for interest income.
    
    Args:
        age (int): Age of the taxpayer
        interest_income (Decimal): Interest income
    
    Returns:
        Decimal: Total allowed deduction under 80TTA
    """
    if age < 60:
        max_80tta_limit = 10000
        return min(interest_income, max_80tta_limit)
    return 0

def calculate_80ttb_deduction(age: int, interest_income: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80TTB for interest income.
    
    Args:
        age (int): Age of the taxpayer
        interest_income (Decimal): Interest income
    
    Returns:
        Decimal: Total allowed deduction under 80TTB
    """
    if age >= 60:
        max_80ttb_limit = 50000
        return min(interest_income, max_80ttb_limit)
    return 0

def calculate_80ccd1_deduction(nps_80ccd1: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80CCD(1) for employee NPS contribution.
    
    Args:
        nps_80ccd1 (Decimal): NPS contribution under 80CCD(1)
    
    Returns:
        Decimal: Total allowed deduction under 80CCD(1)
    """
    max_80ccd1_limit = 150000 # Subject to 80CCE limit
    return min(nps_80ccd1, max_80ccd1_limit)

def calculate_80ccd2_deduction(basic_salary: Decimal, employer_nps_80ccd2: Decimal) -> Decimal:
    """
    Calculate deduction under Section 80CCD(2) for employer NPS contribution.
    
    Args:
        basic_salary (Decimal): Basic salary component
        employer_nps_80ccd2 (Decimal): Employer NPS contribution under 80CCD(2)
    
    Returns:
        Decimal: Total allowed deduction under 80CCD(2)
    """
    max_80ccd2_limit = Decimal("0.10") * basic_salary if basic_salary > 0 else 0 # 10% of basic salary
    return min(employer_nps_80ccd2, max_80ccd2_limit)

def record_ded(
    name: str,
    amount: Decimal,
    limit: Union[str, Decimal],
    taxable_income: Decimal,
    assessment_year: str,
    age: int,
    tax_data: Dict[str, Any],
    tax_rate: Decimal = Decimal("0.30")
) -> Dict[str, Any]:
    """
    Record a deduction and calculate its tax impact.
    
    This function records the details of a deduction and calculates:
    1. Amount actually used
    2. Available limit
    3. Remaining capacity
    4. Potential tax saving if fully utilized
    5. Approximate tax saved from current usage
    
    Args:
        name (str): Name of the deduction
        amount (Decimal): Amount claimed under this deduction
        limit (Union[str, Decimal]): Maximum allowed limit
        taxable_income (Decimal): Current taxable income
        assessment_year (str): Assessment year
        age (int): Age of taxpayer
        tax_data (Dict[str, Any]): Tax configuration data
        tax_rate (Decimal): Applicable tax rate
    
    Returns:
        Dict[str, Any]: Dictionary containing deduction details and tax impact
    
    Example:
        >>> details = record_ded(
        ...     "80C", Decimal("100000"), Decimal("150000"),
        ...     Decimal("1000000"), "2023-24", 35,
        ...     tax_data, Decimal("0.30")
        ... )
        >>> details['used']
        '100000'
        >>> details['remaining_capacity']
        '50000'
    """
    used = Decimal(str(amount)).quantize(Decimal("0.01"))
    #tax_data = load_tax_slabs() # No longer loading tax_data here, passed as argument
    #tax_rate = Decimal(str(tax_data.get('default_tax_bracket', default_tax_bracket))) if tax_data and 'default_tax_bracket' in tax_data else default_tax_bracket # No longer using tax_data here, using tax_rate argument

    # Calculate tax saved
    initial_tax = calculate_tax_for_income(taxable_income, assessment_year, age)
    remaining_tax = calculate_tax_for_income(taxable_income - amount, assessment_year, age)
    estimated_tax_saving = initial_tax - remaining_tax

    if isinstance(limit, str):
        remaining = None
        limit_val = limit
    else:
        limit = Decimal(str(limit)).quantize(Decimal("0.01"))
        remaining = max(Decimal("0"), limit - used)
        limit_val = str(limit)

    potential_saving = None if remaining is None else (remaining * Decimal(str(tax_rate))).quantize(Decimal("0.01"))

    return {
        "used": str(used),
        "limit": limit_val,
        "remaining_capacity": str(remaining) if remaining is not None else "Check with applicable limits",
        "estimated_tax_saving_if_fully_used": str(potential_saving) if potential_saving is not None else "Check applicable limits",
        "tax_saved_from_used_approx": str(estimated_tax_saving)
    }