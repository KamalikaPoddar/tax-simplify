
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

interface IncomeDetailsFormProps {
  onNext: () => void;
  onPrevious: () => void;
}

export function IncomeDetailsForm({ onNext, onPrevious }: IncomeDetailsFormProps) {
  const { formData, setFormData } = useTaxForm();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Income Details</h2>
        <p className="text-gray-600">Please provide your income related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="basicSalary">Basic Salary (Annual)</Label>
          <Input
            id="basicSalary"
            type="number"
            value={formData.incomeDetails.basicSalary}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                incomeDetails: {
                  ...prev.incomeDetails,
                  basicSalary: Number(e.target.value),
                },
              }))
            }
            required
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="hraReceived">HRA Received</Label>
            <Switch
              id="hraReceived"
              checked={formData.incomeDetails.hraReceived}
              onCheckedChange={(checked) =>
                setFormData((prev) => ({
                  ...prev,
                  incomeDetails: {
                    ...prev.incomeDetails,
                    hraReceived: checked,
                  },
                }))
              }
            />
          </div>
        </div>

        {formData.incomeDetails.hraReceived && (
          <>
            <div className="space-y-2">
              <Label htmlFor="hraAmount">HRA Amount</Label>
              <Input
                id="hraAmount"
                type="number"
                value={formData.incomeDetails.hraAmount}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    incomeDetails: {
                      ...prev.incomeDetails,
                      hraAmount: Number(e.target.value),
                    },
                  }))
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="cityType">City Type</Label>
              <Select
                value={formData.incomeDetails.cityType}
                onValueChange={(value) =>
                  setFormData((prev) => ({
                    ...prev,
                    incomeDetails: { ...prev.incomeDetails, cityType: value },
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select city type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="metro">Metro (Delhi, Mumbai, Kolkata, Chennai)</SelectItem>
                  <SelectItem value="non-metro">Non-Metro</SelectItem>
                </SelectContent>
              </Select>
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
