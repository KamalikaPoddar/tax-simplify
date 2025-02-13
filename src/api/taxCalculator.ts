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
  startup_investments_80iac: number;
  deduction_from_scientific_research: number;

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

  // Ensure numeric values
  const income = Number(formData.incomeDetails.basicSalary) || 0;
  const basic_salary = Number(formData.incomeDetails.basicSalary) || 0;
  const hra_amount = Number(formData.incomeDetails.hraAmount) || 0;
  const taxSavingInvestments = Number(formData.investmentDetails.taxSavingInvestments) || 0;
  const npsContribution = Number(formData.investmentDetails.npsContribution) || 0;
  const healthInsurance = Number(formData.investmentDetails.healthInsurance) || 0;
  const housingLoanInterest = Number(formData.loanDetails.housingLoanInterest) || 0;
  const studentLoanInterest = Number(formData.loanDetails.studentLoanInterest) || 0;
  const criticalIllnessExpenses = Number(formData.medicalDetails.criticalIllnessExpenses) || 0;

  return {
    income,
    age,
    gender: formData.personalInfo.gender,
    city: formData.incomeDetails.cityType,
    rent: 0,
    has_hra: formData.incomeDetails.hraReceived,
    basic_salary,
    hra_received: hra_amount,
    property_self_occupied: formData.loanDetails.isSelfOccupied,
    home_loan_interest: housingLoanInterest,
    home_loan_principal_80c: 0,
    sec_80ee: false,
    sec_80eea: false,
    total_80c_investments: taxSavingInvestments,
    nps_80ccd_1b: npsContribution,
    health_insurance_self_parents: healthInsurance,
    is_disabled_self: formData.medicalDetails.disabilityStatus !== "None",
    is_disabled_dependent: formData.medicalDetails.hasDisabledDependents,
    severe_disability_self: formData.medicalDetails.disabilityStatus === "Severe",
    severe_disability_dep: false,
    critical_illness_bills: criticalIllnessExpenses,
    student_loan_interest: studentLoanInterest,
    donations_80g: 0,
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
    console.log('Raw form data:', formData);
    console.log('Mapped request data:', requestData);

    // Make the API call to your Python backend
    const response = await fetch('http://localhost:5000/api/calculateTax', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Server error response:', errorText);
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
