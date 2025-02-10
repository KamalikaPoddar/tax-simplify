
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { useCallback } from "react";

interface TaxResultsProps {
  onPrevious: () => void;
}

export function TaxResults({ onPrevious }: TaxResultsProps) {
  const { formData, result } = useTaxForm();

  const handleCalculate = useCallback(async () => {
    // TODO: Implement API call to calculate tax
    console.log("Form data to be sent to API:", formData);
  }, [formData]);

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Tax Calculation Results</h2>
        <p className="text-gray-600">
          Review your tax calculation under both old and new regimes
        </p>
      </div>

      {result ? (
        <div className="space-y-6">
          <div className="rounded-lg border p-4">
            <h3 className="text-lg font-semibold">Old Regime</h3>
            <div className="mt-2 space-y-2">
              <p>Current Tax Liability: ₹{result.oldRegime.currentTaxLiability}</p>
              <p>Potential Savings: ₹{result.oldRegime.potentialSavings}</p>
              <p>Optimized Tax Payable: ₹{result.oldRegime.optimizedTaxPayable}</p>
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <h3 className="text-lg font-semibold">New Regime</h3>
            <div className="mt-2">
              <p>Optimized Tax Payable: ₹{result.newRegime.optimizedTaxPayable}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center space-y-4">
          <p>Click calculate to get your tax assessment</p>
          <Button onClick={handleCalculate}>Calculate Tax</Button>
        </div>
      )}

      <div className="flex justify-start">
        <Button type="button" variant="outline" onClick={onPrevious}>
          Previous
        </Button>
      </div>
    </div>
  );
}
