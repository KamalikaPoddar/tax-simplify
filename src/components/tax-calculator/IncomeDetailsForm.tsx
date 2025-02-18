import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { IndianRupee, Building, Home } from "lucide-react";

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
    <form onSubmit={handleSubmit} className="space-y-6 bg-gradient-to-br from-white to-purple-50 p-6 rounded-lg shadow-sm">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Income Details</h2>
        <p className="text-gray-600">Please provide your income related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="basicSalary" className="flex items-center gap-2">
            <IndianRupee className="h-4 w-4 text-purple-600" />
            What is your AnnualBasic Salary?
          </Label>
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
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="cityType" className="flex items-center gap-2">
            <Home className="h-4 w-4 text-purple-600" />
            What is your City Type?
          </Label>
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

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="hraReceived" className="flex items-center gap-2">
              <Building className="h-4 w-4 text-purple-600"/>
              Do you receive Housing Rent Allowance?
            </Label>
            <Switch
              id="hraReceived"
              checked={formData.incomeDetails.hraReceived}
              onCheckedChange={(checked) =>
                setFormData((prev) => ({
                  ...prev,
                  incomeDetails: {
                    ...prev.incomeDetails,
                    hraReceived: checked,
                    ...(checked ? {} : { isOwnedHouse: false }),
                  },
                }))
              }
            />
          </div>
        </div>

        {formData.incomeDetails.hraReceived ? (
          <div className="space-y-2">
            <Label htmlFor="hraAmount">What is the annual HRA you receive?</Label>
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
              className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="isOwnedHouse" className="flex items-center gap-2">
                <Home className="h-4 w-4 text-purple-600"/>
                Are you residing in a owned, self-occupied property?
              </Label>
              <Switch
                id="isOwnedHouse"
                checked={formData.incomeDetails.isOwnedHouse}
                onCheckedChange={(checked) =>
                  setFormData((prev) => ({
                    ...prev,
                    incomeDetails: {
                      ...prev.incomeDetails,
                      isOwnedHouse: checked,
                    },
                  }))
                }
              />
            </div>
          </div>
        )}
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
