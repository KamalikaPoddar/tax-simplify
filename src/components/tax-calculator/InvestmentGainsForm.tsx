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
    <form onSubmit={handleSubmit} className="space-y-6 bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg shadow-sm">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Investment Gains</h2>
        <p className="text-gray-600">Please provide your investment gains information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2 bg-white bg-opacity-50 p-4 rounded-md">
          <Label htmlFor="capitalGains" className="flex items-center gap-2">
            <Coins className="h-4 w-4 text-purple-600" />
            Have you received any capital gains from your investments?
          </Label>
          <Input
            id="capitalGains"
            type="number"
            value={formData.investmentGains.capitalGains}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentGains: {
                  ...prev.investmentGains,
                  capitalGains: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2 bg-white bg-opacity-50 p-4 rounded-md">
          <Label htmlFor="dividends" className="flex items-center gap-2">
            <Landmark className="h-4 w-4 text-purple-600" />
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

        <div className="space-y-2 bg-white bg-opacity-50 p-4 rounded-md">
          <Label htmlFor="digitalAssetsSale" className="flex items-center gap-2">
            <Bitcoin className="h-4 w-4 text-purple-600"/>
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
