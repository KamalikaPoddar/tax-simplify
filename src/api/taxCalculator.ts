
interface TaxCalculationRequest {
  // Personal Info
  email: string;
  birthDate: string;
  gender: "male" | "female" | "other";
  employmentType: string;
  residencyCountry: string;
  hasDependentSeniorParents: boolean;
  
  // Income Details
  basicSalary: number;
  hraReceived: boolean;
  hraAmount: number;
  cityType: string;
  
  // Investment Details
  taxSavingInvestments: number;
  npsContribution: string;
  healthInsurance: number;
  
  // Loan Details
  hasStudentLoan: boolean;
  studentLoanInterest: number;
  hasHousingLoan: boolean;
  isSelfOccupied: boolean;
  housingLoanInterest: number;
  
  // Investment Gains
  capitalGains: number;
  gainsAmount: number;
  dividends: number;
  investmentType: string;
  digitalAssetsSale: number;
  
  // Medical Details
  disabilityStatus: string;
  criticalIllnessExpenses: number;
  hasDisabledDependents: boolean;
  dependentMedicalExpenses: number;
}

interface TaxCalculationResponse {
  oldRegime: {
    currentTaxLiability: number;
    potentialSavings: number;
    optimizedTaxPayable: number;
  };
  newRegime: {
    optimizedTaxPayable: number;
  };
}

export async function calculateTax(data: TaxCalculationRequest): Promise<TaxCalculationResponse> {
  try {
    // In a real application, this would make an API call to your backend
    // For now, we'll simulate the calculation with a mock response
    console.log('Tax calculation request data:', data);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock response - in reality, this would come from your backend
    return {
      oldRegime: {
        currentTaxLiability: data.basicSalary * 0.2,
        potentialSavings: data.taxSavingInvestments * 0.1,
        optimizedTaxPayable: (data.basicSalary * 0.2) - (data.taxSavingInvestments * 0.1)
      },
      newRegime: {
        optimizedTaxPayable: data.basicSalary * 0.15
      }
    };
  } catch (error) {
    console.error('Error calculating tax:', error);
    throw new Error('Failed to calculate tax');
  }
}
