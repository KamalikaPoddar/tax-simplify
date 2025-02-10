
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
}

export interface InvestmentDetails {
  taxSavingInvestments: number;
  npsContribution: string;
  healthInsurance: number;
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
  oldRegime: {
    currentTaxLiability: number;
    potentialSavings: number;
    optimizedTaxPayable: number;
  };
  newRegime: {
    optimizedTaxPayable: number;
  };
}
