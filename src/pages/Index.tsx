
import { TaxFormProvider } from "@/context/TaxFormContext";
import { PersonalInfoForm } from "@/components/tax-calculator/PersonalInfoForm";
import { IncomeDetailsForm } from "@/components/tax-calculator/IncomeDetailsForm";
import { InvestmentDetailsForm } from "@/components/tax-calculator/InvestmentDetailsForm";
import { LoanDetailsForm } from "@/components/tax-calculator/LoanDetailsForm";
import { InvestmentGainsForm } from "@/components/tax-calculator/InvestmentGainsForm";
import { MedicalDetailsForm } from "@/components/tax-calculator/MedicalDetailsForm";
import { TaxResults } from "@/components/tax-calculator/TaxResults";
import { useState } from "react";

const Index = () => {
  const [currentStep, setCurrentStep] = useState(1);

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <PersonalInfoForm onNext={() => setCurrentStep(2)} />;
      case 2:
        return (
          <IncomeDetailsForm
            onNext={() => setCurrentStep(3)}
            onPrevious={() => setCurrentStep(1)}
          />
        );
      case 3:
        return (
          <InvestmentDetailsForm
            onNext={() => setCurrentStep(4)}
            onPrevious={() => setCurrentStep(2)}
          />
        );
      case 4:
        return (
          <LoanDetailsForm
            onNext={() => setCurrentStep(5)}
            onPrevious={() => setCurrentStep(3)}
          />
        );
      case 5:
        return (
          <InvestmentGainsForm
            onNext={() => setCurrentStep(6)}
            onPrevious={() => setCurrentStep(4)}
          />
        );
      case 6:
        return (
          <MedicalDetailsForm
            onNext={() => setCurrentStep(7)}
            onPrevious={() => setCurrentStep(5)}
          />
        );
      case 7:
        return <TaxResults onPrevious={() => setCurrentStep(6)} />;
      default:
        return <PersonalInfoForm onNext={() => setCurrentStep(2)} />;
    }
  };

  return (
    <TaxFormProvider>
      <div className="min-h-screen bg-gradient-to-b from-white to-secondary/30 p-4 md:p-8">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-2xl bg-white p-6 shadow-lg transition-all duration-300 animate-fade-in">
            {renderStep()}
          </div>
        </div>
      </div>
    </TaxFormProvider>
  );
};

export default Index;
