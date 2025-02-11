
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Accessibility, HeartPulse, Users } from "lucide-react";

interface MedicalDetailsFormProps {
  onNext: () => void;
  onPrevious: () => void;
}

export function MedicalDetailsForm({ onNext, onPrevious }: MedicalDetailsFormProps) {
  const { formData, setFormData } = useTaxForm();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-gradient-to-br from-white to-purple-50 p-6 rounded-lg shadow-sm">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Medical Details</h2>
        <p className="text-gray-600">Please provide your medical related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="disabilityStatus" className="flex items-center gap-2">
            <Accessibility className="h-4 w-4" />
            Do you have any certified medical disabilities?
          </Label>
          <Select
            value={formData.medicalDetails.disabilityStatus}
            onValueChange={(value) =>
              setFormData((prev) => ({
                ...prev,
                medicalDetails: { ...prev.medicalDetails, disabilityStatus: value },
              }))
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select disability status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="None">None</SelectItem>
              <SelectItem value="Severe">Severe disability, 70-100%</SelectItem>
              <SelectItem value="Partial">Disability 40-70%</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="criticalIllnessExpenses" className="flex items-center gap-2">
            <HeartPulse className="h-4 w-4 text-purple-600" />
            How much have you paid for treatment of critical illness/disabilities?
          </Label>
          <Input
            id="criticalIllnessExpenses"
            type="number"
            value={formData.medicalDetails.criticalIllnessExpenses}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                medicalDetails: {
                  ...prev.medicalDetails,
                  criticalIllnessExpenses: Number(e.target.value),
                },
              }))
            }
            className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="hasDisabledDependents" className="flex items-center gap-2">
              <Users className="h-4 w-4 text-purple-600" />
              Disabled Dependents
            </Label>
            <Switch
              id="hasDisabledDependents"
              checked={formData.medicalDetails.hasDisabledDependents}
              onCheckedChange={(checked) =>
                setFormData((prev) => ({
                  ...prev,
                  medicalDetails: {
                    ...prev.medicalDetails,
                    hasDisabledDependents: checked,
                  },
                }))
              }
            />
          </div>
        </div>

        {formData.medicalDetails.hasDisabledDependents && (
          <div className="space-y-2">
            <Label htmlFor="dependentMedicalExpenses">
              How much have you paid for your dependent's critical illness/disability?
            </Label>
            <Input
              id="dependentMedicalExpenses"
              type="number"
              value={formData.medicalDetails.dependentMedicalExpenses}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  medicalDetails: {
                    ...prev.medicalDetails,
                    dependentMedicalExpenses: Number(e.target.value),
                  },
                }))
              }
              className="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
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
