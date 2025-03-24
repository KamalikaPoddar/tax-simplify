"""
Tax Optimization Module

This module provides tax optimization suggestions by analyzing the taxpayer's
current deductions and investments. It identifies opportunities for tax savings
and provides actionable recommendations.

Features:
- Analysis of current tax deductions utilization
- Personalized investment suggestions
- Tax saving calculations for each recommendation
- Support for various deduction sections:
  - Section 80C investments
  - NPS contributions under 80CCD(1B)
  - Health insurance under 80D
  - Education loan interest under 80E
  - Rent payment deductions
"""

from decimal import Decimal
from typing import List, Dict, Any
from .tax_calculations import calculate_tax_for_income

def generate_optimization_suggestions(
    input_data,  # Will be TaxInput type
    old_breakdown: Dict[str, Any],
    assessment_year: str,
    age: int,
    tax_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate personalized tax optimization suggestions.
    
    Analyzes the taxpayer's current deductions and investments to identify
    opportunities for additional tax savings. Provides specific recommendations
    with potential tax saving amounts.
    
    Args:
        input_data: TaxInput object containing taxpayer details
        old_breakdown (Dict[str, Any]): Current deduction utilization details
        assessment_year (str): Assessment year for tax calculation
        age (int): Age of the taxpayer
        tax_data (Dict[str, Any]): Tax configuration data
    
    Returns:
        List[Dict[str, Any]]: List of optimization suggestions
            Each suggestion contains:
            - deduction: Name of the deduction section
            - current_investment: Current amount invested
            - recommended_investment: Suggested investment amount
            - potential_tax_saving: Estimated tax saving
            - action: Detailed recommendation with rationale
    
    Example Suggestion:
        {
            "deduction": "80C",
            "current_investment": "50000",
            "recommended_investment": "150000",
            "potential_tax_saving": "30000",
            "action": "Invest an additional ₹100000 in ELSS/PPF/NSC..."
        }
    """
    suggestions: List[Dict[str, Any]] = []
    taxable_income = input_data.income
    student_loan_interest = input_data.student_loan_interest

    # Use tax bracket from config if available, otherwise default to 0.3
    default_tax_bracket = Decimal("0.3")
    tax_bracket = Decimal(str(tax_data.get('default_tax_bracket', default_tax_bracket))) if tax_data and 'default_tax_bracket' in tax_data else default_tax_bracket

    # 80C Suggestion
    if "80c" in old_breakdown and old_breakdown["80c"]["remaining_capacity"] != "Check with applicable limits" :
        remaining = Decimal(str(old_breakdown["80c"]["remaining_capacity"])) if  old_breakdown["80c"]["remaining_capacity"]!= None else Decimal("0")
        potential_tax_saving = Decimal(old_breakdown["80c"]["estimated_tax_saving_if_fully_used"]) if  old_breakdown["80c"]["estimated_tax_saving_if_fully_used"] != "Check applicable limits" else Decimal("0")

        suggestions.append({
            "deduction": "80C",
            "current_investment": str(input_data.total_80c_investments),
            "recommended_investment": str(input_data.total_80c_investments + remaining),
            "potential_tax_saving": str(potential_tax_saving.quantize(Decimal("0.00"))),
            "action": f"Invest an additional ₹{remaining} in ELSS/PPF/NSC. Consider a mix of ELSS (for growth) and PPF (for safety)."
        })

    # 80CCD(1B) Suggestion
    if "80ccd_1_nps" in old_breakdown:
        current = Decimal(old_breakdown["80ccd_1_nps"]["used"])
        potential_saving  =  Decimal(old_breakdown["80ccd_1_nps"]["estimated_tax_saving_if_fully_used"]) if  old_breakdown["80ccd_1_nps"]["estimated_tax_saving_if_fully_used"] != "Check applicable limits" else Decimal("0")
        limit = Decimal("50000")  # Additional NPS limit under 80CCD(1B)
        remaining = limit - current
        if remaining > 0:
            potential_tax_saving = remaining * tax_bracket
            suggestions.append({
                "deduction": "80CCD_1B_NPS",
                "current_investment": str(current),
                "recommended_investment": str(remaining),
                "potential_tax_saving": str(potential_tax_saving.quantize(Decimal("0.00"))),
                "action": f"Contribute an additional ₹{remaining} to NPS under section 80CCD(1B). NPS offers tax benefits and helps build a retirement corpus."
            })

    # 80D Suggestion
    if "80d_health_insurance" in old_breakdown and  old_breakdown["80d_health_insurance"]["remaining_capacity"] !="Check with applicable limits" :
        remaining = Decimal(old_breakdown["80d_health_insurance"]["remaining_capacity"])
        potential_tax_saving = Decimal(old_breakdown["80d_health_insurance"]["estimated_tax_saving_if_fully_used"]) if  old_breakdown["80d_health_insurance"]["estimated_tax_saving_if_fully_used"] != "Check applicable limits" else Decimal("0")

        suggestions.append({
            "deduction": "80D_Health_Insurance",
            "current_investment": str(Decimal(old_breakdown["80d_health_insurance"]["used"])),
            "recommended_investment": str(remaining),
            "potential_tax_saving": str(potential_tax_saving),
            "action": f"Purchase additional health insurance for yourself/family/parents to utilize the remaining 80D limit of ₹{remaining} and save up to ₹{potential_tax_saving} in taxes."
        })

    if input_data.student_loan_interest > 0:

        tax_before = calculate_tax_for_income(taxable_income, assessment_year, age)
        tax_after = calculate_tax_for_income(taxable_income - input_data.student_loan_interest, assessment_year, age)
        potential_tax_saving = tax_before - tax_after
        suggestions.append({
            "deduction": "80E Education Loan Interest",
            "totalInt": str(input_data.student_loan_interest),
            "potential_tax_saving": str(potential_tax_saving.quantize(Decimal("0.00"))),
            "action": "Total interest paid on education loan is taken as deduction"

        })
   #Rent Suggestion (If not used)
    if not input_data.has_hra and input_data.rent > 0 and not input_data.is_exempted_under_80gge:
        #Suggest 80GG if not getting HRA
        suggestions.append({
            "deduction": "80GG",
            "potential_tax_saving": "Check calculations and estimates based on the rent paid",
            "action": "Check if you can declare rent paid and claim the deductions as applicable"
        })

    return suggestions