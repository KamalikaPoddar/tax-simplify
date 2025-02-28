
export interface PersonalInfo {
  email: string;
  birthDate: string;
  gender: "male" | "female" | "other";
  employmentType: string;
  residencyCountry: string;
  hasDependentSeniorParents: boolean;
}

export interface IncomeDetails {
  basicSalary: number;
  hraReceived: boolean;
  hraAmount: number;
  cityType: string;
  isOwnedHouse: boolean;
}

export interface InvestmentDetails {
  taxSavingInvestments: number;
  npsContribution: number;
  healthInsurance: number;
  startup_investments_80iac: number;
  deduction_from_scientific_research: number;
}

export interface LoanDetails {
  hasStudentLoan: boolean;
  studentLoanInterest: number;
  hasHousingLoan: boolean;
  isSelfOccupied: boolean;
  housingLoanInterest: number;
}

export interface InvestmentGains {
  capitalGains: number;
  gainsAmount: number;
  dividends: number;
  investmentType: string;
  digitalAssetsSale: number;
}

export interface MedicalDetails {
  disabilityStatus: string;
  criticalIllnessExpenses: number;
  hasDisabledDependents: boolean;
  dependentMedicalExpenses: number;
}

export interface TaxFormData {
  step: number;
  personalInfo: PersonalInfo;
  incomeDetails: IncomeDetails;
  investmentDetails: InvestmentDetails;
  loanDetails: LoanDetails;
  investmentGains: InvestmentGains;
  medicalDetails: MedicalDetails;
}

export interface TaxCalculationResult {
  optimal_regime: "Old Regime" | "New Regime";
  old_regime: {
    tax: number;
    taxable_income: number;
    deduction_breakdown: Record<string, {
      used: number;
      limit: number | null;
      remaining_capacity: number | null;
      estimated_tax_saving_if_fully_used: number;
      tax_saved_from_used_approx: number;
    }>;
  };
  new_regime: {
    tax: number;
    taxable_income: number;
  };
  optimization_suggestions: {
    "80C": { current: number; proposed: number; };
    "80CCD(1B)": { current: number; proposed: number; };
    "80D - Health Insurance": { current: number; proposed: number; };
    recalculated_old_regime?: {
      taxable_income: number;
      tax: number;
    };
  };
}
