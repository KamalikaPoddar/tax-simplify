
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

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
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Investment Details</h2>
        <p className="text-gray-600">Please provide your investment related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="taxSavingInvestments">
            Tax Saving Investments (80C - PPF, ELSS, etc.)
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
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="npsContribution">NPS Contribution</Label>
          <Input
            id="npsContribution"
            type="text"
            value={formData.investmentDetails.npsContribution}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentDetails: {
                  ...prev.investmentDetails,
                  npsContribution: e.target.value,
                },
              }))
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="healthInsurance">Health Insurance Premium</Label>
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
          />
        </div>
      </div>

      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button type="submit">Next</Button>
      </div>
    </form>
  );
}
