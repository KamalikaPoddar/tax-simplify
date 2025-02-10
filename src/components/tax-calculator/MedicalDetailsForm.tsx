
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

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
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">Medical Details</h2>
        <p className="text-gray-600">Please provide your medical related information</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="disabilityStatus">Disability Status</Label>
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
              <SelectItem value="Partial">Partial</SelectItem>
              <SelectItem value="Full">Full</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="criticalIllnessExpenses">Critical Illness Expenses</Label>
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
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="hasDisabledDependents">Disabled Dependents</Label>
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
            <Label htmlFor="dependentMedicalExpenses">Dependent Medical Expenses</Label>
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
            />
          </div>
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
