#!/usr/bin/env python3

from datetime import datetime, date
from decimal import Decimal
import json
import logging
import re
from http import HTTPStatus
import decimal
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union, Tuple
import os
from io import BytesIO

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pydantic import BaseModel, validator, ValidationError

app = Flask(__name__)
CORS(app)

class TaxInput(BaseModel):
    income: Decimal
    age: int
    gender: str
    city: str
    rent: Decimal
    has_hra: bool
    basic_salary: Decimal = Decimal("0.0")
    hra_received: Decimal = Decimal("0.0")
    property_self_occupied: bool = False
    home_loan_interest: Decimal = Decimal("0.0")
    home_loan_principal_80c: Decimal = Decimal("0.0")
    sec_80ee: bool = False
    sec_80eea: bool = False
    total_80c_investments: Decimal = Decimal("0.0")
    nps_80ccd_1b: Decimal = Decimal("0.0")
    health_insurance_self_parents: Decimal = Decimal("0.0")
    is_disabled_self: bool = False
    is_disabled_dependent: bool = False
    severe_disability_self: bool = False
    severe_disability_dep: bool = False
    critical_illness_bills: Decimal = Decimal("0.0")
    student_loan_interest: Decimal = Decimal("0.0")
    donations_80g: Decimal = Decimal("0.0")
    royalty_income_80rrb: Decimal = Decimal("0.0")
    is_startup_investments: bool = False
    startup_investments_80iac: Decimal = Decimal("0.0")
    cooperative_society_80p: Decimal = Decimal("0.0")
    number_of_new_employees_80jjaa: int = 0
    new_employees_wages: Decimal = Decimal("0.0")
    deduction_from_scientific_research: Decimal = Decimal("0.0")
    is_exempted_under_80gge: bool = False
    savings_interest_80tta: Decimal = Decimal("0.0")
    interest_income_80ttb: Decimal = Decimal("0.0")
    donation_100pct_no_limit: Decimal = Decimal("0.0")
    donation_50pct_no_limit: Decimal = Decimal("0.0")
    donation_100pct_with_limit: Decimal = Decimal("0.0")
    donation_50pct_with_limit: Decimal = Decimal("0.0")
    nps_80ccd1: Decimal = Decimal("0.0")
    employer_nps_80ccd2: Decimal = Decimal("0.0")
    rent_paid_80gg: Decimal = Decimal("0.0")
    medical_treatment_80ddb: Decimal = Decimal("0.0")
    tax_rate: Decimal = Decimal("0.30")
    assessment_year: str = "2023-24"
    first_time_home_buyer: bool = False

    @validator('income')
    def income_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Income must be non-negative')
        return v

    @validator('age')
    def age_must_be_valid(cls, v):
        if not 0 <= v <= 120:
            raise ValueError('Age must be within a reasonable range (0-120)')
        return v

    @validator('city')
    def city_must_be_valid(cls, v):
        tax_data = load_tax_slabs()
        if tax_data:
            allowed_cities = tax_data.get('city_classification', {}).get('metro', []) + tax_data.get('city_classification', {}).get('non-metro', [])
            if allowed_cities and v.lower() not in [city.lower() for city in allowed_cities]:
                raise ValueError(f'City must be one of: {", ".join(allowed_cities)}')
        return v

class TaxDataNotFoundError(Exception):
    """Custom exception for when tax data is not found."""
    pass

class InvalidTaxSlabsStructureError(Exception):
    """Custom exception for invalid tax slabs structure."""
    pass

def load_tax_slabs():
    """Loads tax slabs and configurations from tax_slabs.json."""
    try:
        with open('tax_slabs.json', 'r') as f:
            tax_data = json.load(f)
        return tax_data
    except FileNotFoundError:
        logger.error("Tax slabs file 'tax_slabs.json' not found.")
        raise TaxDataNotFoundError("Tax configuration file not found.")
    except json.JSONDecodeError:
        logger.error("Error decoding JSON from 'tax_slabs.json'.")
        raise InvalidTaxSlabsStructureError("Invalid JSON format in tax configuration file.")
    except Exception as e:
        logger.error(f"Unexpected error loading tax slabs: {e}")
        raise TaxDataNotFoundError(f"Failed to load tax configuration: {e}")

def get_tax_slabs(assessment_year: str, regime_type: str, age: Optional[int] = None):
    """Retrieves tax slabs based on assessment year, regime type, and age."""
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    regime_data = year_data.get(f"{regime_type}_regime", {})

    if regime_type == 'old':
        if age is not None:
            if age > 80:
                return regime_data.get('super_senior_citizen', [])
            elif age >= 60:
                return regime_data.get('senior_citizen', [])
        return regime_data.get('general', [])
    elif regime_type == 'new_regime':
        return regime_data.get('general', [])
    return []

def get_surcharge_rates(assessment_year: str):
    """Retrieves surcharge rates for a given assessment year."""
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    regime_data = year_data.get('old_regime', {})
    return regime_data.get('surcharge', {})

def get_rebate_87a(assessment_year: str):
    """Retrieves rebate 87A details for a given assessment year."""
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    return year_data.get('rebate_87A')

def get_standard_deduction(assessment_year: str):
    """Retrieves standard deduction for a given assessment year."""
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    return year_data.get('standard_deduction')

def get_80D_limits(assessment_year: str, age: int):
    """Retrieves 80D deduction limits for a given assessment year and age."""
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    limits_80d = year_data.get('section_80d_limits', {})

    if age >= 60:
        return limits_80d.get('senior_citizen')
    else:
        return limits_80d.get('general')

def calculate_section24b_deduction(home_loan_interest: Decimal, property_self_occupied: bool) -> Decimal:
    """Calculate deduction under Section 24b for home loan interest."""
    if not home_loan_interest:
        return Decimal("0")
    
    if property_self_occupied:
        return min(home_loan_interest, Decimal("200000"))
    return home_loan_interest

def calculate_80eea_deduction(first_time_home_buyer: bool, home_loan_interest: Decimal) -> Decimal:
    """Calculate deduction under Section 80EEA for first-time home buyers."""
    if not first_time_home_buyer or not home_loan_interest:
        return Decimal("0")
    
    return min(home_loan_interest, Decimal("150000"))

def calculate_old_regime_tax(
    income: Decimal,
    age: int,
    gender: str,
    city: str,
    rent: Decimal,
    has_hra: bool,
    basic_salary: Decimal = Decimal("0.0"),
    hra_received: Decimal = Decimal("0.0"),
    property_self_occupied: bool = False,
    home_loan_interest: Decimal = Decimal("0.0"),
    home_loan_principal_80c: Decimal = Decimal("0.0"),
    sec_80ee: bool = False,
    sec_80eea: bool = False,
    total_80c_investments: Decimal = Decimal("0.0"),
    nps_80ccd_1b: Decimal = Decimal("0.0"),
    health_insurance_self_parents: Decimal = Decimal("0.0"),
    is_disabled_self: bool = False,
    is_disabled_dependent: bool = False,
    severe_disability_self: bool = False,
    severe_disability_dep: bool = False,
    critical_illness_bills: Decimal = Decimal("0.0"),
    student_loan_interest: Decimal = Decimal("0.0"),
    donations_80g: Decimal = Decimal("0.0"),
    royalty_income_80rrb: Decimal = Decimal("0.0"),
    is_startup_investments: bool = False,
    startup_investments_80iac: Decimal = Decimal("0.0"),
    cooperative_society_80p: Decimal = Decimal("0.0"),
    number_of_new_employees_80jjaa: int = 0,
    new_employees_wages: Decimal = Decimal("0.0"),
    deduction_from_scientific_research: Decimal = Decimal("0.0"),
    is_exempted_under_80gge: bool = False,
    savings_interest_80tta: Decimal = Decimal("0.0"),
    interest_income_80ttb: Decimal = Decimal("0.0"),
    donation_100pct_no_limit: Decimal = Decimal("0.0"),
    donation_50pct_no_limit: Decimal = Decimal("0.0"),
    donation_100pct_with_limit: Decimal = Decimal("0.0"),
    donation_50pct_with_limit: Decimal = Decimal("0.0")
):
    """
    Returns:
      total_tax, taxable_income_after_deductions, breakdown_deductions (dict)
    where breakdown_deductions = {
      'HRA': { 'used': X, 'limit': Y, 'remaining': Y-X, 'tax_saved_est': ??? },
      '80C': { 'used': A, 'limit': 150000, 'remaining': ???, 'tax_saved_est': ??? },
      ... 
    }
    so we can display a detailed optimization report if old regime is better.
    """
    taxable_income = income
    breakdown = {}
    
    def record_ded(name, used_amount, limit=None):
        """
        Utility to record each deduction or exemption in a breakdown dictionary.
        'limit' = max limit if relevant
        """
        # We'll store how much is used and leftover if we have a known limit
        if limit is not None and limit >= 0:
            remaining = round(max(0, limit - used_amount), 2)
        else:
            remaining = 0.0
        # Approx tax saving = used_amount * marginal rate? Hard to do precisely. We'll do a placeholder
        # since final slab rates can vary. We'll assume a max 30% for high-level estimate
        # or do 20% if they're in that slab, etc. We'll just show 30% as an estimate for "max saving".
        estimated_tax_saving = round(used_amount * 0.30, 2)
        
        breakdown[name] = {
            'used': round(used_amount, 2),
            'limit': limit if limit else None,
            'remaining_capacity': remaining if limit else None,
            'estimated_tax_saving_if_fully_used': round(remaining * 0.30, 2) if limit else 0.0,
            'tax_saved_from_used_approx': estimated_tax_saving
        }
    
    total_deductions = 0.0
    
    # 1) HRA or 80GG
    hra_used = 0.0
    if has_hra and basic_salary > 0 and hra_received > 0 and rent > 0:
        is_metro = city.lower() in ("delhi","mumbai","kolkata","chennai","metro")
        limit_by_location = (0.5 if is_metro else 0.4) * basic_salary
        limit_rent_basic = rent - 0.1 * basic_salary
        if limit_rent_basic < 0: 
            limit_rent_basic = 0
        hra_exemption = min(hra_received, limit_by_location, limit_rent_basic)
        if hra_exemption < 0:
            hra_exemption = 0
        hra_used = hra_exemption
        taxable_income -= hra_used
        total_deductions += hra_used
        record_ded('HRA Exemption', hra_used, limit=hra_received)
    else:
        if is_exempted_under_80gge and rent > 0:
            # 80GG limit => min(60000, 25% of inc, rent -10% inc)
            val1 = 60000.0
            val2 = 0.25 * taxable_income
            val3 = rent - 0.1*taxable_income
            if val3 < 0: val3 = 0
            gg_ded = min(val1, val2, val3)
            if gg_ded<0: gg_ded=0
            taxable_income -= gg_ded
            total_deductions += gg_ded
            record_ded('80GG Rent Deduction', gg_ded, limit=60000)

    # 2) Home loan interest (Sec 24(b))
    home_loan_used = 0.0
    if property_self_occupied and home_loan_interest>0:
        hl_ded = min(home_loan_interest, 200000.0)
        home_loan_used = hl_ded
        taxable_income -= hl_ded
        total_deductions += hl_ded
        record_ded('Home Loan Interest (Self-Occ)', hl_ded, limit=200000.0)
    
    # 3) 80EE / 80EEA
    ee_used=0.0
    if sec_80ee and home_loan_interest>0:
        # up to 50k
        ee_d = min(home_loan_interest, 50000.0)
        ee_used+=ee_d
        taxable_income -= ee_d
        total_deductions += ee_d
    if sec_80eea and home_loan_interest>0:
        # up to 1.5L
        eea_d = min(home_loan_interest, 150000.0)
        ee_used+=eea_d
        taxable_income-=eea_d
        total_deductions+=eea_d
    
    if ee_used>0:
        record_ded('80EE/80EEA Additional Interest', ee_used, limit=200000.0) 
        # 2L is arbitrary or none. Actually 80EE => 50k, 80EEA =>1.5L. We combine them in one record, for demo.

    # 4) Chapter VI-A if taxable_income>0
    # a) 80C
    c_used = 0.0
    if taxable_income>0:
        c_limit = 150000.0
        c_amt = home_loan_principal_80c + total_80c_investments
        used_c = min(c_limit, c_amt)
        c_used = used_c
        taxable_income-= used_c
        total_deductions+= used_c
        record_ded('80C', used_c, limit=c_limit)
    # b) 80CCD(1B)
    nps_used=0.0
    if taxable_income>0 and nps_80ccd_1b>0:
        nps_l= min(50000.0, nps_80ccd_1b)
        nps_used= nps_l
        taxable_income-= nps_l
        total_deductions+= nps_l
        record_ded('80CCD(1B) - NPS Addl', nps_used, limit=50000.0)
    # c) 80D
    d_used=0.0
    if taxable_income>0:
        # simplified approach 
        if age>=60:
            limit_d=50000.0
        else:
            limit_d=25000.0
        d_applied= min(limit_d, health_insurance_self_parents)
        d_used= d_applied
        taxable_income-= d_used
        total_deductions+= d_used
        record_ded('80D - Health Insurance', d_used, limit=limit_d)

    # d) 80E - Ed Loan
    e_loan=0.0
    if taxable_income>0 and student_loan_interest>0:
        e_loan= student_loan_interest  # no upper limit
        taxable_income-= e_loan
        total_deductions+= e_loan
        record_ded('80E - Edu Loan Int', e_loan, limit=None)

    # e) Disability (80U / 80DD)
    dis_used=0.0
    if taxable_income>0 and is_disabled_self:
        if severe_disability_self:
            dis_amt=125000.0
        else:
            dis_amt=75000.0
        # no actual cap 
        amt= min(taxable_income, dis_amt)
        dis_used+=amt
        taxable_income-=amt
        total_deductions+=amt
    if taxable_income>0 and is_disabled_dependent:
        if severe_disability_dep:
            dep_amt=125000.0
        else:
            dep_amt=75000.0
        amt2= min(taxable_income, dep_amt)
        dis_used+= amt2
        taxable_income-=amt2
        total_deductions+= amt2
    if dis_used>0:
        record_ded('80U / 80DD - Disability', dis_used)

    # f) 80DDB
    ddb_used=0.0
    if taxable_income>0 and critical_illness_bills>0:
        if age>=60:
            cap_ill=100000.0
        else:
            cap_ill=40000.0
        use_ill= min(cap_ill, critical_illness_bills, taxable_income)
        taxable_income-=use_ill
        total_deductions+=use_ill
        ddb_used= use_ill
        record_ded('80DDB - Critical Illness', ddb_used, limit=cap_ill)
    
    # g) 80TTA / 80TTB
    tta_used=0.0
    if age<60:
        # TTA upto 10k
        use_tta= min(10000.0, savings_interest_80tta, taxable_income)
        tta_used=use_tta
        taxable_income-=use_tta
        total_deductions+=use_tta
        if use_tta>0:
            record_ded('80TTA - Savings Interest', use_tta, limit=10000.0)
    else:
        # TTB up to 50k
        use_ttb= min(50000.0, interest_income_80ttb, taxable_income)
        tta_used=use_ttb
        taxable_income-= use_ttb
        total_deductions+= use_ttb
        if use_ttb>0:
            record_ded('80TTB - Senior Interest', use_ttb, limit=50000.0)

    # h) 80RRB - Royalty (3L)
    rrb_used=0.0
    if taxable_income>0 and royalty_income_80rrb>0:
        r = min(300000.0, royalty_income_80rrb, taxable_income)
        taxable_income-=r
        total_deductions+=r
        rrb_used=r
        record_ded('80RRB - Patent Royalty', r, limit=300000.0)
    
    # i) 80IAC - startup
    iac_used=0.0
    if taxable_income>0 and is_startup_investments and startup_investments_80iac>0:
        i_ = min(startup_investments_80iac, taxable_income)
        taxable_income-= i_
        total_deductions+= i_
        iac_used= i_
        record_ded('80IAC - Startup Profit', i_)

    # j) 80P - Co-op
    coop_used=0.0
    if taxable_income>0 and cooperative_society_80p>0:
        cc= min(cooperative_society_80p, taxable_income)
        taxable_income-=cc
        total_deductions+=cc
        coop_used=cc
        record_ded('80P - Cooperative Income', cc)

    # k) 80JJAA - new employees
    jj_used=0.0
    if taxable_income>0 and number_of_new_employees_80jjaa>0 and new_employees_wages>0:
        ded_jj= 0.30* new_employees_wages
        if ded_jj> taxable_income:
            ded_jj=taxable_income
        taxable_income-=ded_jj
        total_deductions+= ded_jj
        jj_used= ded_jj
        record_ded('80JJAA - New Employees', jj_used)

    # l) 80GGA - Sci research
    gga_used=0.0
    if deduction_from_scientific_research>0 and taxable_income>0:
        sc= min(deduction_from_scientific_research, taxable_income)
        taxable_income-= sc
        total_deductions+= sc
        gga_used= sc
        record_ded('80GGA - Scientific Research', sc)

    # m) 80G - Donations (the advanced logic with with-limit/no-limit is not fully integrated)
    # For brevity, we do a simpler approach for now:
    if donations_80g>0 and taxable_income>0:
        # Suppose 50% deduction
        # Real logic is more nuanced, but we keep it simple
        used_g= min(donations_80g*0.5, taxable_income)
        taxable_income-= used_g
        total_deductions+= used_g
        record_ded('80G - Donations', used_g)

    # if after all that, negative => 0
    if taxable_income<0:
        taxable_income=0

    # Now compute tax by old slabs
    basic_tax=0.0
    if taxable_income<=250000:
        basic_tax=0.0
    elif taxable_income<=500000:
        basic_tax= (taxable_income-250000)*0.05
    elif taxable_income<=1000000:
        basic_tax=12500 + (taxable_income-500000)*0.20
    else:
        basic_tax=112500 + (taxable_income-1000000)*0.30

    # Rebate 87A
    rebate_87a=0.0
    if taxable_income<=500000:
        rebate_87a= min(basic_tax, 12500.0)
    basic_tax_after_rebate= basic_tax- rebate_87a
    if basic_tax_after_rebate<0:
        basic_tax_after_rebate=0.0

    # Surcharge (simple approach)
    surcharge_rate=0.0
    if income>50000000:
        surcharge_rate=0.37
    elif income>20000000:
        surcharge_rate=0.25
    elif income>10000000:
        surcharge_rate=0.15
    elif income>5000000:
        surcharge_rate=0.10
    tax_plus_surcharge= basic_tax_after_rebate*(1+surcharge_rate)

    # 4% cess
    cess= 0.04* tax_plus_surcharge
    total_tax= tax_plus_surcharge+ cess

    # Women-specific if any
    # Currently no extra

    total_tax_rounded= round(total_tax,2)
    taxable_income_rounded= round(taxable_income,2)

    return total_tax_rounded, taxable_income_rounded, breakdown


def calculate_new_regime_tax(
    income: Decimal,
    gender: str,
    basic_salary: Decimal = Decimal("0.0")
) -> tuple[float, float]:
    """
    Same logic as you provided. Returns (tax, taxable_income).
    """
    std_deduction= 75000.0 if basic_salary>0 else 0.0
    ti= income- std_deduction
    if ti<0: ti=0
    # slabs
    tax=0.0
    if ti<=400000:
        tax=0
    elif ti<=800000:
        tax= (ti-400000)*0.05
    elif ti<=1200000:
        tax= 20000+ (ti-800000)*0.10
    elif ti<=1600000:
        tax=60000+ (ti-1200000)*0.15
    elif ti<=2000000:
        tax=120000+ (ti-1600000)*0.20
    elif ti<=2400000:
        tax=200000+ (ti-2000000)*0.25
    else:
        tax=300000+ (ti-2400000)*0.30
    
    # rebate
    if ti<=1200000:
        rebate= tax
        tax-=rebate
        if tax<0: tax=0
    # surcharge
    sr=0.0
    if income>10000000:
        sr=0.15
    elif income>5000000:
        sr=0.10
    surchg= tax*sr
    tax_plus_surch= tax+ surchg
    cess= 0.04* tax_plus_surch
    total_tax= tax_plus_surch+ cess
    return round(total_tax,2), round(ti,2)


def calculate_80d_deduction(age, health_insurance_self, health_checkup_self,
                             age_parents, health_insurance_parents, health_checkup_parents):
    """
    Calculates the eligible deduction under Section 80D for health insurance and health checkups.

    Args:
        age (int): Age of the taxpayer.
        health_insurance_self (float): Premium paid for health insurance for self, spouse, and dependent children.
        health_checkup_self (float): Expenses on preventive health checkups for self, spouse, and dependent children.
        age_parents (int): Age of parents (enter 0 if no claim for parents is made).
        health_insurance_parents (float): Premium paid for health insurance for parents.
        health_checkup_parents (float): Expenses on preventive health checkups for parents.

    Returns:
        float: Total eligible deduction under Section 80D.
    """

    total_deduction = 0.0

    # Self, Spouse, and Dependent Children
    max_deduction_self = 25000.0 if age < 60 else 50000.0  # Limit for self, spouse and dependent children
    max_checkup_self = 5000.0  # Combined limit for health checkups (within the overall limit)
    
    eligible_health_insurance_self = min(health_insurance_self, max_deduction_self)
    
    # Health checkup limit applies to both insurance premium and checkup expenses together.
    # Ensure total checkup + insurance deduction doesn't exceed max limit and health checkup doesn't exceed checkup limit
    eligible_health_checkup_self = min(health_checkup_self, max_checkup_self) # Apply individual limit
    if eligible_health_insurance_self + eligible_health_checkup_self > max_deduction_self:
      eligible_health_checkup_self = max(0, max_deduction_self - eligible_health_insurance_self) # Adjust to comply with the max deduction


    total_deduction += eligible_health_insurance_self + eligible_health_checkup_self


    # Parents
    if age_parents > 0:  # Only consider if there's a claim for parents.
        max_deduction_parents = 25000.0 if age_parents < 60 else 50000.0  # Limit for parents

        max_checkup_parents = 5000.0  #Combined Limit for parents
        eligible_health_insurance_parents = min(health_insurance_parents, max_deduction_parents)
        
        eligible_health_checkup_parents = min(health_checkup_parents, max_checkup_parents) #Apply checkup limit
        if eligible_health_insurance_parents + eligible_health_checkup_parents > max_deduction_parents:
            eligible_health_checkup_parents = max(0, max_deduction_parents - eligible_health_insurance_parents)

        total_deduction += eligible_health_insurance_parents + eligible_health_checkup_parents

    return total_deduction


def run_tax_calculator():
    """
    Prompts user, does calculations, 
    and if old regime is cheaper, prints a DETAILED breakdown from 'breakdown_deductions'.
    """
    print("=== Detailed Tax Calculator ===\n")
    gender= input("Gender (male/female): ").lower()
    try:
        income= float(input("Annual total income: "))
        age= int(input("Age: "))
    except ValueError:
        print("Invalid numeric input.")
        return

    city= input("City (metro/non-metro): ").lower()
    rent= float(input("Monthly Rent: ") or 0)
    hra_resp= input("Do you receive HRA? (yes/no): ").lower()
    has_hra= (hra_resp=='yes')
    basic_salary= float(input("Annual Basic Salary (if any): ") or 0)
    hra_received= float(input("Annual HRA received: ") or 0) if has_hra else 0
    prop_self= input("Is property self occupied? (yes/no): ").lower()
    prop_self_occ= (prop_self=='yes')
    hloan_int= float(input("Annual home loan interest: ") or 0)
    hloan_principal_80c= float(input("Home loan principal for 80C: ") or 0)
    sec80ee= (input("Qualify for 80EE? (yes/no): ").lower()=='yes')
    sec80eea= (input("Qualify for 80EEA (affordable)? (yes/no): ").lower()=='yes')

    # 80C
    total_80c= float(input("Total 80C investments (PPF,ELSS,etc): ") or 0)
    # 80CCD(1B)
    nps_1b= float(input("NPS 80CCD(1B): ") or 0)
    # 80D
    health_ins= float(input("Health Insure self+parents: ") or 0)
    # Disability
    self_dis= (input("Are you disabled? (yes/no): ").lower()=='yes')
    sev_self= False
    if self_dis:
        sev_self= (input("Severe disability? (yes/no): ").lower()=='yes')
    dep_dis= (input("Any disabled dependent? (yes/no): ").lower()=='yes')
    sev_dep= False
    if dep_dis:
        sev_dep= (input("Dependent severe disability? (yes/no): ").lower()=='yes')
    # 80DDB
    crit_ill= float(input("Critical illness bills (80DDB): ") or 0)
    # 80E
    stud_loan= float(input("Edu loan interest(80E): ") or 0)
    # 80G
    donat= float(input("Donations(80G) simplified: ") or 0)
    # plus
    roy_80rrb= float(input("Royalty income(80RRB): ") or 0)
    scires= float(input("Scientific research(80GGA): ") or 0)
    startup_inv= float(input("Startup profit/invest(80IAC): ") or 0)
    is_startup= (startup_inv>0)
    coop_amt= float(input("Coop societies(80P): ") or 0)
    newemp_count= int(input("Num new employees(80JJAA): ") or 0)
    newemp_wages= float(input("Wages for new employees(80JJAA): ") or 0)
    # 80GG
    e80gge= (input("Claim 80GG if no HRA? (yes/no): ").lower()=='yes')

    # TTA/TTB
    sav_int= float(input("Savings interest(80TTA/80TTB): ") or 0)
    fd_int= float(input("FD interest(senior for 80TTB else taxed): ") or 0)
    
    # Calculate OLD
    old_tax, old_ti, old_breakdown= calculate_old_regime_tax(
        income= income,
        age= age,
        gender= gender,
        city= city,
        rent= rent,
        has_hra= has_hra,
        basic_salary= basic_salary,
        hra_received= hra_received,
        property_self_occupied= prop_self_occ,
        home_loan_interest= hloan_int,
        home_loan_principal_80c= hloan_principal_80c,
        sec_80ee= sec80ee,
        sec_80eea= sec80eea,
        total_80c_investments= total_80c,
        nps_80ccd_1b= nps_1b,
        health_insurance_self_parents= health_ins,
        is_disabled_self= self_dis,
        is_disabled_dependent= dep_dis,
        severe_disability_self= sev_self,
        severe_disability_dep= sev_dep,
        critical_illness_bills= crit_ill,
        student_loan_interest= stud_loan,
        donations_80g= donat,
        royalty_income_80rrb= roy_80rrb,
        deduction_from_scientific_research= scires,
        is_startup_investments= is_startup,
        startup_investments_80iac= startup_inv,
        cooperative_society_80p= coop_amt,
        number_of_new_employees_80jjaa= newemp_count,
        new_employees_wages_80jjaa= newemp_wages,
        is_exempted_under_80gge= e80gge,
        savings_interest_80tta= sav_int if age<60 else 0.0,
        interest_income_80ttb= (sav_int+fd_int) if age>=60 else 0.0
    )

    # Calculate NEW
    new_tax, new_ti= calculate_new_regime_tax(
        income= income,
        gender= gender,
        basic_salary= basic_salary
    )

    # Show results
    print("\n--- Summary of Results ---")
    print(f"Old Regime => Taxable Income After Deductions: {old_ti}, Tax Payable: {old_tax}")
    print(f"New Regime => Taxable Income: {new_ti}, Tax Payable: {new_tax}")

    # Compare
    if old_tax < new_tax:
        print("\n**Conclusion**: Old Regime is cheaper!")
        saved = round(new_tax - old_tax,2)
        print(f"You save about ₹{saved} compared to New Regime.")
        
        # Provide DETAILED breakdown for the Old Regime
        print("\n===== Old Regime Detailed Deductions & Optimization =====")
        for key, val in old_breakdown.items():
            used= val['used']
            lim= val['limit']
            remain= val['remaining_capacity']
            est_saving= val['estimated_tax_saving_if_fully_used']
            tax_saved_from_used= val['tax_saved_from_used_approx']
            if lim:
                print(f" - {key}: Used ₹{used} of limit ₹{lim}. You can still invest/spend ₹{remain} more here, potentially saving ~₹{est_saving} additional tax.")
            else:
                print(f" - {key}: Used ₹{used} (no statutory limit). Approx tax saved so far ~₹{tax_saved_from_used}.")
        print("\n**If you have more capacity** to invest or spend in the above categories, you can further reduce your tax under the Old Regime.")

        total_potential_tax_saving = 0.0
        for key, val in old_breakdown.items():
            estimated_tax_saving = val['estimated_tax_saving_if_fully_used']
            total_potential_tax_saving += estimated_tax_saving

        optimal_old_tax = round(old_tax - total_potential_tax_saving, 2)

        print(f"\nPotential Tax Savings from Fully Utilizing Deductions: ₹{round(total_potential_tax_saving, 2)}")
        print(f"Optimal Old Regime Tax (If Fully Optimized): ₹{optimal_old_tax}")

        print("\n**Conclusion**: Old Regime is cheaper!")
        saved = round(new_tax - optimal_old_tax, 2)
        print(f"You save about ₹{saved} compared to New Regime.")

        # Provide DETAILED breakdown for the Old Regime
        print("\n===== Old Regime Detailed Deductions & Optimization =====")
        for key, val in old_breakdown.items():
            used = val['used']
            lim = val['limit']
            remain = val['remaining_capacity']
            est_saving = val['estimated_tax_saving_if_fully_used']
            tax_saved_from_used = val['tax_saved_from_used_approx']
            if lim:
                print(f" - {key}: Used ₹{used} of limit ₹{lim}. You can still invest/spend ₹{remain} more here, potentially saving ~₹{est_saving} additional tax.")
            else:
                print(f" - {key}: Used ₹{used} (no statutory limit). Approx tax saved so far ~₹{tax_saved_from_used}.")
        print("\n**If you have more capacity** to invest or spend in the above categories, you can further reduce your tax under the Old Regime.")
    elif new_tax < old_tax:
        print("\n**Conclusion**: New Regime is cheaper!")
        saved = round(old_tax - new_tax,2)
        print(f"You save about ₹{saved} compared to Old Regime.")
        print("\nNo further old-regime breakdown needed since new regime is chosen. No major personal deductions apply in new regime.")
    else:
        print("\nBoth regimes yield the **same** tax! Choose either for convenience.")
        print("\nNo further breakdown needed since they tie. If you prefer fewer compliance steps, new regime might be simpler.")
    
    print("\n--- End of Calculation ---")


def calculate_tax_from_slabs(taxable_income: Decimal, tax_slabs: List[Dict[str, Union[Decimal, float, None]]]) -> Decimal:
    """Calculates tax from income and tax slabs."""
    tax_amount = Decimal('0.00')
    last_limit = Decimal('0.00')

    for slab in tax_slabs:
        limit = slab.get('limit')
        rate = Decimal(str(slab.get('rate', 0)))

        if limit is None:  # Last slab with no upper limit
            taxable_amount_in_slab = max(0, taxable_income - last_limit)
        else:
            slab_limit = Decimal(str(limit))
            taxable_amount_in_slab = max(0, min(taxable_income, slab_limit) - last_limit)
            last_limit = slab_limit

        tax_amount += taxable_amount_in_slab * rate

    return tax_amount

def calculate_tax_for_income(taxable_income: Decimal, assessment_year: str, age: Optional[int] = None):
    try:
        slabs = get_tax_slabs(assessment_year, 'old', age)
        if not slabs:
            logger.warning("No tax slabs found, using default slabs")
            slabs = [
                {"limit": Decimal("250000"), "rate": 0},
                {"limit": Decimal("500000"), "rate": 0.05},
                {"limit": Decimal("1000000"), "rate": 0.20},
                {"limit": None, "rate": 0.30}
            ]

        tax = calculate_tax_from_slabs(taxable_income, slabs)

        rebate_87a = get_rebate_87a(assessment_year)
        if rebate_87a:
            rebate_limit = Decimal(str(rebate_87a['limit']))
            income_threshold = Decimal(str(rebate_87a['income_threshold']))
            if taxable_income <= income_threshold:
                tax = max(Decimal("0"), tax - rebate_limit)

        return tax.quantize(Decimal("0.01"))
    except Exception as e:
        logger.error("Error calculating tax for income: %s", str(e))
        return Decimal("0")

def generate_optimization_suggestions(input_data: TaxInput, old_breakdown: Dict[str, Any], assessment_year: str, age: int, tax_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates more personalized optimization suggestions."""
    suggestions: List[Dict[str, Any]] = []
    taxable_income = input_data.income

    default_tax_bracket = Decimal("0.3")
    tax_bracket = Decimal(str(tax_data.get('default_tax_bracket', default_tax_bracket))) if tax_data and 'default_tax_bracket' in tax_data else default_tax_bracket

    # 80C Suggestion
    if "80c" in old_breakdown and old_breakdown["80c"]["remaining_capacity"] != "Check with applicable limits":
        remaining = Decimal(str(old_breakdown["80c"]["remaining_capacity"])) if old_breakdown["80c"]["remaining_capacity"] is not None else Decimal("0")
        potential_tax_saving = Decimal(old_breakdown["80c"]["estimated_tax_saving_if_fully_used"]) if old_breakdown["80c"]["estimated_tax_saving_if_fully_used"] != "Check applicable limits" else Decimal("0")

        suggestions.append({
            "deduction": "80C",
            "current_investment": str(input_data.total_80c_investments),
            "recommended_investment": str(input_data.total_80c_investments + remaining),
            "potential_tax_saving": str(potential_tax_saving.quantize(Decimal("0.00"))),
            "action": f"Invest an additional ₹{remaining} in ELSS/PPF/NSC. Consider a mix of ELSS (for growth) and PPF (for safety)."
        })

    # 80D Suggestion
    if "80d_health_insurance" in old_breakdown and old_breakdown["80d_health_insurance"]["remaining_capacity"] != "Check with applicable limits":
        remaining = Decimal(old_breakdown["80d_health_insurance"]["remaining_capacity"])
        potential_tax_saving = Decimal(old_breakdown["80d_health_insurance"]["estimated_tax_saving_if_fully_used"]) if old_breakdown["80d_health_insurance"]["estimated_tax_saving_if_fully_used"] != "Check applicable limits" else Decimal("0")

        suggestions.append({
            "deduction": "80D_Health_Insurance",
            "current_investment": str(Decimal(old_breakdown["80d_health_insurance"]["used"])),
            "recommended_investment": str(remaining),
            "potential_tax_saving": str(potential_tax_saving),
            "action": f"Purchase additional health insurance for yourself/family/parents to utilize the remaining 80D limit of ₹{remaining} and save up to ₹{potential_tax_saving} in taxes."
        })

    # Home Loan Suggestions
    if input_data.home_loan_interest > 0:
        if input_data.first_time_home_buyer:
            suggestions.append({
                "deduction": "80EEA",
                "current_investment": str(input_data.home_loan_interest),
                "potential_tax_saving": "Up to ₹150,000 additional deduction",
                "action": "As a first-time home buyer, you can claim up to ₹150,000 additional deduction under Section 80EEA"
            })
        else:
            suggestions.append({
                "deduction": "24b_Home_Loan",
                "current_investment": str(input_data.home_loan_interest),
                "potential_tax_saving": "Up to ₹200,000 for self-occupied property",
                "action": "You can claim up to ₹200,000 deduction on home loan interest under Section 24b for self-occupied property"
            })

    return suggestions

@app.route('/api/calculateTax', methods=['POST'])
def calculate_tax():
    """Calculate tax for both old and new regimes."""
    try:
        data = request.get_json()
        logger.info("Received tax calculation request with data: %s", data)
        input_data = TaxInput(**data)

        tax_data = load_tax_slabs()
        if not tax_data:
            return jsonify({'status': 'error', 'message': 'Tax data not found'}), HTTPStatus.INTERNAL_SERVER_ERROR

        default_tax_bracket = Decimal("0.3")
        tax_bracket = Decimal(str(tax_data.get('default_tax_bracket', default_tax_bracket))) if tax_data and 'default_tax_bracket' in tax_data else default_tax_bracket

        # Old Regime Calculations
        old_tax, old_ti, old_breakdown = calculate_old_regime_tax(
            input_data=input_data,
            tax_data=tax_data
        )

        # New Regime Calculations
        new_tax, new_ti = calculate_new_regime_tax(
            income=input_data.income,
            gender=input_data.gender,
            basic_salary=input_data.basic_salary,
            assessment_year=input_data.assessment_year
        )

        total_potential_tax_saving = Decimal("0.0")
        for key, val in old_breakdown.items():
            if 'estimated_tax_saving_if_fully_used' in val:
                estimated_tax_saving = Decimal(val['estimated_tax_saving_if_fully_used']) if val['estimated_tax_saving_if_fully_used'] != "Check applicable limits" else Decimal("0")
                if isinstance(estimated_tax_saving, (int, float, str)):
                    estimated_tax_saving = Decimal(str(estimated_tax_saving))
                total_potential_tax_saving += estimated_tax_saving

        optimal_old_tax = (old_tax - total_potential_tax_saving).quantize(Decimal("0.01"))
        optimal_regime = "old_regime" if optimal_old_tax < new_tax else "new_regime"

        def to_snake_case(text):
            return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

        optimization_suggestions = generate_optimization_suggestions(input_data, old_breakdown, input_data.assessment_year, input_data.age, tax_data)

        response = {
            'status': 'success',
            'optimal_regime': optimal_regime,
            'old_regime': {
                'tax': "{:.2f}".format(float(old_tax)),
                'taxable_income': "{:.2f}".format(float(old_ti)),
                'optimal_tax': "{:.2f}".format(float(optimal_old_tax)),
                'total_potential_tax_saving': str(int(total_potential_tax_saving)),
                'deduction_breakdown': {
                    to_snake_case(k): {
                        'used': "{:.2f}".format(float(v['used'])),
                        'limit': str(v['limit']) if v['limit'] is not None else None,
                        'remaining_capacity': str(int(v['remaining_capacity'])) if v['remaining_capacity'] is not None else None,
                        'estimated_tax_saving_if_fully_used': "{:.2f}".format(float(v['estimated_tax_saving_if_fully_used'])),
                        'tax_saved_from_used_approx': "{:.2f}".format(float(v['tax_saved_from_used_approx']))
                    } for k, v in old_breakdown.items()
                }
            },
            'new_regime': {
                'tax': "{:.2f}".format(float(new_tax)),
                'taxable_income': "{:.2f}".format(float(new_ti)),
                'standard_deduction': "{:.1f}".format(float(get_standard_deduction(input_data.assessment_year) or 50000.0))
            },
            'optimization_suggestions': optimization_suggestions,
            'assessment_year': input_data.assessment_year
        }

        logger.info("Successfully calculated tax for both regimes")
        return jsonify(response), HTTPStatus.OK

    except ValidationError as e:
        logger.error("Validation error in tax calculation request: %s", e.errors())
        return jsonify({
            'status': 'error',
            'error_type': 'validation_error',
            'message': 'Invalid input data',
            'details': e.errors()
        }), HTTPStatus.BAD_REQUEST

    except TaxDataNotFoundError as e:
        logger.error("Tax data not found: %s", str(e))
        return jsonify({
            'status': 'error',
            'error_type': 'tax_data_error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    except InvalidTaxSlabsStructureError as e:
        logger.error("Invalid tax slabs structure: %s", str(e))
        return jsonify({
            'status': 'error',
            'error_type': 'tax_slabs_error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    except decimal.InvalidOperation as e:
        logger.error("Invalid decimal operation: %s", str(e))
        return jsonify({
            'status': 'error',
            'error_type': 'calculation_error',
            'message': f"Invalid numeric value in calculation: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        logger.error("Unexpected error in tax calculation: %s", str(e), exc_info=True)
        return jsonify({
            'status': 'error',
            'error_type': 'unexpected_error',
            'message': f"An unexpected error occurred: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run(port=5000, debug=True)
