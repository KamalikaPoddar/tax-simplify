import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PiggyBank, Building2, HeartPulse } from "lucide-react";

interface InvestmentDetailsFormProps {
  onNext: () => void;
  onPrevious: () => void;
}

export function InvestmentDetailsForm({ onNext, onPrevious }: InvestmentDetailsFormProps) {
  const { formData, setFormData } = useTaxForm();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-gradient-to-br from-white to-purple-50 p-6 rounded-lg shadow-sm">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Investment Details</h2>
        <p className="text-gray-600">Please provide your investment related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="taxSavingInvestments" className="flex items-center gap-2">
            <PiggyBank className="h-4 w-4 text-purple-600"/>
            How much have you invested in tax saving schemes?
          </Label>
          <Input
            id="taxSavingInvestments"
            type="number"
            value={formData.investmentDetails.taxSavingInvestments}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentDetails: {
                  ...prev.investmentDetails,
                  taxSavingInvestments: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="npsContribution" className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-purple-600" />
            How much have you saved in National Pension Scheme (NPS)?
          </Label>
          <Input
            id="npsContribution"
            type="number"
            value={formData.investmentDetails.npsContribution}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentDetails: {
                  ...prev.investmentDetails,
                  npsContribution: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="healthInsurance" className="flex items-center gap-2">
            <HeartPulse className="h-4 w-4 text-purple-600" />
            What is the total medical insurance you pay for yourself and your dependents?
          </Label>
          <Input
            id="healthInsurance"
            type="number"
            value={formData.investmentDetails.healthInsurance}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentDetails: {
                  ...prev.investmentDetails,
                  healthInsurance: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>
      </div>

      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button type="submit" className="bg-purple-600 hover:bg-purple-700">
          Next
        </Button>
      </div>
    </form>
  );
}
