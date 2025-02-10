
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Coins, Landmark, Bitcoin } from "lucide-react";

interface InvestmentGainsFormProps {
  onNext: () => void;
  onPrevious: () => void;
}

export function InvestmentGainsForm({ onNext, onPrevious }: InvestmentGainsFormProps) {
  const { formData, setFormData } = useTaxForm();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Investment Gains</h2>
        <p className="text-gray-600">Please provide your investment gains information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="savingsInterest" className="flex items-center gap-2">
            <Coins className="h-4 w-4" />
            Have you received any interest from your savings investments?
          </Label>
          <Input
            id="savingsInterest"
            type="number"
            value={formData.investmentGains.savingsInterest}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentGains: {
                  ...prev.investmentGains,
                  savingsInterest: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="dividends" className="flex items-center gap-2">
            <Landmark className="h-4 w-4" />
            Have you received any dividend payouts from your capital market investments?
          </Label>
          <Input
            id="dividends"
            type="number"
            value={formData.investmentGains.dividends}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentGains: {
                  ...prev.investmentGains,
                  dividends: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="digitalAssetsSale" className="flex items-center gap-2">
            <Bitcoin className="h-4 w-4" />
            Have you recorded any sale of digital assets?
          </Label>
          <Input
            id="digitalAssetsSale"
            type="number"
            value={formData.investmentGains.digitalAssetsSale}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentGains: {
                  ...prev.investmentGains,
                  digitalAssetsSale: Number(e.target.value),
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
