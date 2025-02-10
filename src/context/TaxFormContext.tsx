
import React, { createContext, useContext, useState } from "react";
import { TaxFormData, TaxCalculationResult } from "@/types/tax-calculator";

interface TaxFormContextType {
  formData: TaxFormData;
  setFormData: React.Dispatch<React.SetStateAction<TaxFormData>>;
  result: TaxCalculationResult | null;
  setResult: React.Dispatch<React.SetStateAction<TaxCalculationResult | null>>;
}

const defaultFormData: TaxFormData = {
  step: 1,
  personalInfo: {
    email: "",
    birthDate: "",
    gender: "male",
    employmentType: "",
    residencyCountry: "",
    hasDependentSeniorParents: false,
  },
  incomeDetails: {
    basicSalary: 0,
    hraReceived: false,
    hraAmount: 0,
    cityType: "",
  },
  investmentDetails: {
    taxSavingInvestments: 0,
    npsContribution: "",
    healthInsurance: 0,
  },
  loanDetails: {
    hasStudentLoan: false,
    studentLoanInterest: 0,
    hasHousingLoan: false,
    isSelfOccupied: false,
    housingLoanInterest: 0,
  },
  investmentGains: {
    capitalGains: 0,
    gainsAmount: 0,
    dividends: 0,
    investmentType: "",
    digitalAssetsSale: 0,
  },
  medicalDetails: {
    disabilityStatus: "None",
    criticalIllnessExpenses: 0,
    hasDisabledDependents: false,
    dependentMedicalExpenses: 0,
  },
};

const TaxFormContext = createContext<TaxFormContextType | undefined>(undefined);

export function TaxFormProvider({ children }: { children: React.ReactNode }) {
  const [formData, setFormData] = useState<TaxFormData>(defaultFormData);
  const [result, setResult] = useState<TaxCalculationResult | null>(null);

  return (
    <TaxFormContext.Provider value={{ formData, setFormData, result, setResult }}>
      {children}
    </TaxFormContext.Provider>
  );
}

export function useTaxForm() {
  const context = useContext(TaxFormContext);
  if (context === undefined) {
    throw new Error("useTaxForm must be used within a TaxFormProvider");
  }
  return context;
}
