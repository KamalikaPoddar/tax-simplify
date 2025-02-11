#!/usr/bin/env python3

import math
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel
from typing import Optional

app = Flask(__name__)
CORS(app)

def calculate_old_regime_tax(
    income: float,
    age: int,
    gender: str,
    city: str,
    rent: float,
    has_hra: bool,
    basic_salary: float = 0.0,
    hra_received: float = 0.0,
    property_self_occupied: bool = False,
    home_loan_interest: float = 0.0,
    home_loan_principal_80c: float = 0.0,
    sec_80ee: bool = False,
    sec_80eea: bool = False,
    total_80c_investments: float = 0.0,
    nps_80ccd_1b: float = 0.0,
    health_insurance_self_parents: float = 0.0,
    is_disabled_self: bool = False,
    is_disabled_dependent: bool = False,
    severe_disability_self: bool = False,
    severe_disability_dep: bool = False,
    critical_illness_bills: float = 0.0,
    student_loan_interest: float = 0.0,
    donations_80g: float = 0.0,
    # placeholders
    royalty_income_80rrb: float = 0.0,
    is_startup_investments: bool = False,
    startup_investments_80iac: float = 0.0,
    cooperative_society_80p: float = 0.0,
    number_of_new_employees_80jjaa: int = 0,
    new_employees_wages_80jjaa: float = 0.0,
    deduction_from_scientific_research: float = 0.0,
    is_exempted_under_80gge: bool = False,
    savings_interest_80tta: float = 0.0,
    interest_income_80ttb: float = 0.0,
    donation_100pct_no_limit: float = 0.0,
    donation_50pct_no_limit: float = 0.0,
    donation_100pct_with_limit: float = 0.0,
    donation_50pct_with_limit: float = 0.0
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
    if taxable_income>0 and number_of_new_employees_80jjaa>0 and new_employees_wages_80jjaa>0:
        ded_jj= 0.30* new_employees_wages_80jjaa
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
    income: float,
    gender: str,
    basic_salary: float = 0.0
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
    elif new_tax < old_tax:
        print("\n**Conclusion**: New Regime is cheaper!")
        saved = round(old_tax - new_tax,2)
        print(f"You save about ₹{saved} compared to Old Regime.")
        print("\nNo further old-regime breakdown needed since new regime is chosen. No major personal deductions apply in new regime.")
    else:
        print("\nBoth regimes yield the **same** tax! Choose either for convenience.")
        print("\nNo further breakdown needed since they tie. If you prefer fewer compliance steps, new regime might be simpler.")
    
    print("\n--- End of Calculation ---")


@app.route('/api/calculateTax', methods=['POST'])
def calculate_tax():
    try:
        data = request.json
        print("Received data:", data)  # Debug print
        
        # Calculate deductions
        deductions = {
            '80C': min(data.get('total_80c_investments', 0), 150000),
            '80CCD(1B)': min(data.get('nps_80ccd_1b', 0), 50000),
            '80D': calculate_80d_deduction(
                age=data['age'],
                health_insurance_self=data.get('health_insurance_self', 0),
                health_checkup_self=data.get('health_checkup_self', 0),
                age_parents=data.get('age_parents', 0),
                health_insurance_parents=data.get('health_insurance_parents', 0),
                health_checkup_parents=data.get('health_checkup_parents', 0)
            ),
            'Home Loan Interest': data.get('home_loan_interest', 0),
            'Student Loan Interest': data.get('student_loan_interest', 0)
        }
        print("Calculated deductions:", deductions)  # Debug print
        
        # Calculate taxes under both regimes
        old_tax, old_ti, old_breakdown = calculate_old_regime_tax(
            income=data['income'],
            age=data['age'],
            gender=data['gender'],
            city=data['city'],
            rent=data['rent'],
            has_hra=data['has_hra'],
            basic_salary=data['basic_salary'],
            hra_received=data['hra_received'],
            property_self_occupied=data['property_self_occupied'],
            home_loan_interest=data['home_loan_interest'],
            home_loan_principal_80c=data['home_loan_principal_80c'],
            sec_80ee=data['sec_80ee'],
            sec_80eea=data['sec_80eea'],
            total_80c_investments=data['total_80c_investments'],
            nps_80ccd_1b=data['nps_80ccd_1b'],
            health_insurance_self_parents=data['health_insurance_self_parents'],
            is_disabled_self=data['is_disabled_self'],
            is_disabled_dependent=data['is_disabled_dependent'],
            severe_disability_self=data['severe_disability_self'],
            severe_disability_dep=data['severe_disability_dep'],
            critical_illness_bills=data['critical_illness_bills'],
            student_loan_interest=data['student_loan_interest'],
            donations_80g=data['donations_80g'],
            royalty_income_80rrb=data['royalty_income_80rrb'],
            deduction_from_scientific_research=data['deduction_from_scientific_research'],
            is_startup_investments=data['is_startup_investments'],
            startup_investments_80iac=data['startup_investments_80iac'],
            cooperative_society_80p=data['cooperative_society_80p'],
            number_of_new_employees_80jjaa=data['number_of_new_employees_80jjaa'],
            new_employees_wages_80jjaa=data['new_employees_wages_80jjaa'],
            is_exempted_under_80gge=data['is_exempted_under_80gge'],
            savings_interest_80tta=data['savings_interest_80tta'],
            interest_income_80ttb=data['interest_income_80ttb']
        )
        print("Calculated old regime tax:", old_tax, old_ti, old_breakdown)  # Debug print
        new_tax, new_ti = calculate_new_regime_tax(
            income=data['income'],
            gender=data['gender'],
            basic_salary=data['basic_salary']
        )
        print("Calculated new regime tax:", new_tax, new_ti)  # Debug print
        
        # Determine optimal regime
        optimal_regime = "Old Regime" if old_tax < new_tax else "New Regime"
        
        # Prepare response
        response = {
            'optimal_regime': optimal_regime,
            'old_regime': {
                'tax': old_tax,
                'taxable_income': old_ti,
                'deduction_breakdown': {
                    k: {
                        'used': v,
                        'limit': 150000 if k == '80C' else 50000 if k == '80CCD(1B)' else 75000 if k == '80D' else None,
                        'remaining_capacity': (150000 - v) if k == '80C' else (50000 - v) if k == '80CCD(1B)' else (75000 - v) if k == '80D' else None,
                        'estimated_tax_saving_if_fully_used': v * 0.3,
                        'tax_saved_from_used_approx': v * 0.3
                    } for k, v in deductions.items()
                }
            },
            'new_regime': {
                'tax': new_tax,
                'taxable_income': new_ti
            },
            'optimization_suggestions': {
                '80C': {
                    'current': deductions['80C'],
                    'proposed': 150000
                },
                '80CCD(1B)': {
                    'current': deductions['80CCD(1B)'],
                    'proposed': 50000
                },
                '80D - Health Insurance': {
                    'current': deductions['80D'],
                    'proposed': 75000
                }
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in calculate_tax: {str(e)}")  # Add debug logging
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
