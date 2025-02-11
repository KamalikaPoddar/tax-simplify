interface TaxCalculationRequest {
  // Income and Basic Info
  income: number;
  age: number;
  gender: "male" | "female" | "other";
  city: string;
  rent: number;
  has_hra: boolean;
  basic_salary: number;
  hra_received: number;

  // Property Details
  property_self_occupied: boolean;
  home_loan_interest: number;
  home_loan_principal_80c: number;
  sec_80ee: boolean;
  sec_80eea: boolean;

  // Investments and Insurance
  total_80c_investments: number;
  nps_80ccd_1b: number;
  health_insurance_self_parents: number;

  // Disability and Medical
  is_disabled_self: boolean;
  is_disabled_dependent: boolean;
  severe_disability_self: boolean;
  severe_disability_dep: boolean;
  critical_illness_bills: number;

  // Loans and Other Deductions
  student_loan_interest: number;
  donations_80g: number;
  royalty_income_80rrb: number;
  is_startup_investments: boolean;
  startup_investments_80iac: number;
  cooperative_society_80p: number;
  number_of_new_employees_80jjaa: number;
  new_employees_wages_80jjaa: number;
  deduction_from_scientific_research: number;
  is_exempted_under_80gge: boolean;
  savings_interest_80tta: number;
  interest_income_80ttb: number;
  donation_100pct_no_limit: number;
  donation_50pct_no_limit: number;
  donation_100pct_with_limit: number;
  donation_50pct_with_limit: number;
}

interface DeductionBreakdown {
  used: number;
  limit: number | null;
  remaining_capacity: number | null;
  estimated_tax_saving_if_fully_used: number;
  tax_saved_from_used_approx: number;
}

interface OptimizationSuggestion {
  current: number;
  proposed: number;
}

interface TaxCalculationResponse {
  optimal_regime: "Old Regime" | "New Regime";
  old_regime: {
    tax: number;
    taxable_income: number;
    deduction_breakdown: Record<string, DeductionBreakdown>;
  };
  new_regime: {
    tax: number;
    taxable_income: number;
  };
  optimization_suggestions: {
    "80C": OptimizationSuggestion;
    "80CCD(1B)": OptimizationSuggestion;
    "80D - Health Insurance": OptimizationSuggestion;
    recalculated_old_regime?: {
      taxable_income: number;
      tax: number;
    };
  };
}

function mapFormDataToRequest(formData: any): TaxCalculationRequest {
  const birthDate = new Date(formData.personalInfo.birthDate);
  const currentDate = new Date();
  const age = currentDate.getFullYear() - birthDate.getFullYear();

  return {
    income: formData.incomeDetails.basicSalary,
    age,
    gender: formData.personalInfo.gender,
    city: formData.incomeDetails.cityType,
    rent: 0, // Add this to your form if needed
    has_hra: formData.incomeDetails.hraReceived,
    basic_salary: formData.incomeDetails.basicSalary,
    hra_received: formData.incomeDetails.hraAmount,
    property_self_occupied: formData.loanDetails.isSelfOccupied,
    home_loan_interest: formData.loanDetails.housingLoanInterest,
    home_loan_principal_80c: 0, // Add this to your form if needed
    sec_80ee: false, // Add this to your form if needed
    sec_80eea: false, // Add this to your form if needed
    total_80c_investments: formData.investmentDetails.taxSavingInvestments,
    nps_80ccd_1b: formData.investmentDetails.npsContribution || 0,
    health_insurance_self_parents: formData.investmentDetails.healthInsurance,
    is_disabled_self: formData.medicalDetails.disabilityStatus !== "None",
    is_disabled_dependent: formData.medicalDetails.hasDisabledDependents,
    severe_disability_self: formData.medicalDetails.disabilityStatus === "Severe",
    severe_disability_dep: false, // Add this to your form if needed
    critical_illness_bills: formData.medicalDetails.criticalIllnessExpenses,
    student_loan_interest: formData.loanDetails.studentLoanInterest,
    donations_80g: 0, // Add this to your form if needed
    royalty_income_80rrb: 0,
    is_startup_investments: false,
    startup_investments_80iac: 0,
    cooperative_society_80p: 0,
    number_of_new_employees_80jjaa: 0,
    new_employees_wages_80jjaa: 0,
    deduction_from_scientific_research: 0,
    is_exempted_under_80gge: false,
    savings_interest_80tta: 0,
    interest_income_80ttb: 0,
    donation_100pct_no_limit: 0,
    donation_50pct_no_limit: 0,
    donation_100pct_with_limit: 0,
    donation_50pct_with_limit: 0,
  };
}

export async function calculateTax(formData: any): Promise<TaxCalculationResponse> {
  try {
    const requestData = mapFormDataToRequest(formData);
    console.log('Tax calculation request data:', requestData);

    // Make the API call to your Python backend
    const response = await fetch('http://localhost:5000/api/calculateTax', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error('Failed to calculate tax');
    }

    const data = await response.json();
    console.log('Tax calculation response:', data);
    return data;
  } catch (error) {
    console.error('Error calculating tax:', error);
    throw error;
  }
}
