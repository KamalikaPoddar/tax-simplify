
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

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
          <Label htmlFor="capitalGains">Capital Gains</Label>
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
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="gainsAmount">Gains Amount</Label>
          <Input
            id="gainsAmount"
            type="number"
            value={formData.investmentGains.gainsAmount}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                investmentGains: {
                  ...prev.investmentGains,
                  gainsAmount: Number(e.target.value),
                },
              }))
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="dividends">Dividends</Label>
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
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="investmentType">Investment Type</Label>
          <Select
            value={formData.investmentGains.investmentType}
            onValueChange={(value) =>
              setFormData((prev) => ({
                ...prev,
                investmentGains: { ...prev.investmentGains, investmentType: value },
              }))
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select investment type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="equity">Equity</SelectItem>
              <SelectItem value="debt">Debt</SelectItem>
              <SelectItem value="hybrid">Hybrid</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="digitalAssetsSale">Digital Assets Sale</Label>
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
