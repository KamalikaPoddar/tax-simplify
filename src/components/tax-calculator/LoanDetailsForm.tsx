
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

interface LoanDetailsFormProps {
  onNext: () => void;
  onPrevious: () => void;
}

export function LoanDetailsForm({ onNext, onPrevious }: LoanDetailsFormProps) {
  const { formData, setFormData } = useTaxForm();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Loan Details</h2>
        <p className="text-gray-600">Please provide your loan related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="hasStudentLoan">Education Loan</Label>
            <Switch
              id="hasStudentLoan"
              checked={formData.loanDetails.hasStudentLoan}
              onCheckedChange={(checked) =>
                setFormData((prev) => ({
                  ...prev,
                  loanDetails: { ...prev.loanDetails, hasStudentLoan: checked },
                }))
              }
            />
          </div>
        </div>

        {formData.loanDetails.hasStudentLoan && (
          <div className="space-y-2">
            <Label htmlFor="studentLoanInterest">Education Loan Interest</Label>
            <Input
              id="studentLoanInterest"
              type="number"
              value={formData.loanDetails.studentLoanInterest}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  loanDetails: {
                    ...prev.loanDetails,
                    studentLoanInterest: Number(e.target.value),
                  },
                }))
              }
            />
          </div>
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="hasHousingLoan">Housing Loan</Label>
            <Switch
              id="hasHousingLoan"
              checked={formData.loanDetails.hasHousingLoan}
              onCheckedChange={(checked) =>
                setFormData((prev) => ({
                  ...prev,
                  loanDetails: { ...prev.loanDetails, hasHousingLoan: checked },
                }))
              }
            />
          </div>
        </div>

        {formData.loanDetails.hasHousingLoan && (
          <>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="isSelfOccupied">Self Occupied</Label>
                <Switch
                  id="isSelfOccupied"
                  checked={formData.loanDetails.isSelfOccupied}
                  onCheckedChange={(checked) =>
                    setFormData((prev) => ({
                      ...prev,
                      loanDetails: {
                        ...prev.loanDetails,
                        isSelfOccupied: checked,
                      },
                    }))
                  }
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="housingLoanInterest">Housing Loan Interest</Label>
              <Input
                id="housingLoanInterest"
                type="number"
                value={formData.loanDetails.housingLoanInterest}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    loanDetails: {
                      ...prev.loanDetails,
                      housingLoanInterest: Number(e.target.value),
                    },
                  }))
                }
              />
            </div>
          </>
        )}
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
