
import { TaxFormData, TaxCalculationResult } from "@/types/tax-calculator";

// Get the API URL from environment or default to the deployed backend URL
const API_URL = import.meta.env.VITE_API_URL || 'https://tax-calculator-api.herokuapp.com';

export async function calculateTax(formData: TaxFormData): Promise<TaxCalculationResult> {
  try {
    // Map the form data to the structure expected by the backend
    const requestData = {
      income: formData.incomeDetails.basicSalary,
      age: calculateAge(formData.personalInfo.birthDate),
      gender: formData.personalInfo.gender,
      city: formData.incomeDetails.cityType.toLowerCase(),
      rent: 0, // Add if needed
      has_hra: formData.incomeDetails.hraReceived,
      basic_salary: formData.incomeDetails.basicSalary,
      hra_received: formData.incomeDetails.hraAmount,
      property_self_occupied: formData.loanDetails.isSelfOccupied,
      home_loan_interest: formData.loanDetails.housingLoanInterest,
      home_loan_principal_80c: 0, // Add if needed
      sec_80ee: false,
      sec_80eea: false,
      total_80c_investments: formData.investmentDetails.taxSavingInvestments,
      nps_80ccd_1b: formData.investmentDetails.npsContribution,
      health_insurance_self_parents: formData.investmentDetails.healthInsurance,
      is_disabled_self: formData.medicalDetails.disabilityStatus !== "None",
      is_disabled_dependent: formData.medicalDetails.hasDisabledDependents,
      severe_disability_self: formData.medicalDetails.disabilityStatus === "Severe",
      severe_disability_dep: false,
      critical_illness_bills: formData.medicalDetails.criticalIllnessExpenses,
      student_loan_interest: formData.loanDetails.studentLoanInterest,
      donations_80g: 0,
      royalty_income_80rrb: 0,
      is_startup_investments: formData.investmentDetails.startup_investments_80iac > 0,
      startup_investments_80iac: formData.investmentDetails.startup_investments_80iac,
      cooperative_society_80p: 0,
      number_of_new_employees_80jjaa: 0,
      new_employees_wages_80jjaa: 0,
      deduction_from_scientific_research: formData.investmentDetails.deduction_from_scientific_research,
      is_exempted_under_80gge: false,
      savings_interest_80tta: 0,
      interest_income_80ttb: 0,
      donation_100pct_no_limit: 0,
      donation_50pct_no_limit: 0,
      donation_100pct_with_limit: 0,
      donation_50pct_with_limit: 0,
      email: formData.personalInfo.email
    };

    console.log("Raw form data:", formData);
    console.log("Mapped request data:", requestData);

    const response = await fetch(`${API_URL}/api/calculateTax`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Tax calculation response:", data);

    if (data.status === 'error') {
      throw new Error(data.message || 'Failed to calculate tax');
    }

    return data;
  } catch (error) {
    console.error("Error calculating tax:", error);
    throw error;
  }
}

function calculateAge(birthDate: string): number {
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  
  return age;
}
