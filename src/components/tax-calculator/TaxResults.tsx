
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { useCallback, useState } from "react";
import { calculateTax } from "@/api/taxCalculator";
import { toast } from "sonner";

interface TaxResultsProps {
  onPrevious: () => void;
}

export function TaxResults({ onPrevious }: TaxResultsProps) {
  const { formData, result, setResult } = useTaxForm();
  const [isCalculating, setIsCalculating] = useState(false);

  const handleCalculate = useCallback(async () => {
    try {
      setIsCalculating(true);
      const calculationResult = await calculateTax({
        ...formData.personalInfo,
        ...formData.incomeDetails,
        ...formData.investmentDetails,
        ...formData.loanDetails,
        ...formData.investmentGains,
        ...formData.medicalDetails,
      });
      setResult(calculationResult);
      toast.success("Tax calculation completed successfully");
    } catch (error) {
      console.error("Tax calculation error:", error);
      toast.error("Failed to calculate tax. Please try again.");
    } finally {
      setIsCalculating(false);
    }
  }, [formData, setResult]);

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
              <p>Tax: ₹{result.old_regime.tax.toLocaleString()}</p>
              <p>Taxable Income: ₹{result.old_regime.taxable_income.toLocaleString()}</p>
            </div>
          </div>

          <div className="rounded-lg border p-4">
            <h3 className="text-lg font-semibold">New Regime</h3>
            <div className="mt-2">
              <p>Tax: ₹{result.new_regime.tax.toLocaleString()}</p>
              <p>Taxable Income: ₹{result.new_regime.taxable_income.toLocaleString()}</p>
            </div>
          </div>

          <div className="rounded-lg border p-4 bg-purple-50">
            <h3 className="text-lg font-semibold">Recommended Regime</h3>
            <p className="mt-2 font-medium text-purple-700">
              {result.optimal_regime}
            </p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center space-y-4">
          <p>Click calculate to get your tax assessment</p>
          <Button 
            onClick={handleCalculate} 
            disabled={isCalculating}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isCalculating ? "Calculating..." : "Calculate Tax"}
          </Button>
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
