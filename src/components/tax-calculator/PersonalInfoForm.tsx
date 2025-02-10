
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Calendar } from "lucide-react";

interface PersonalInfoFormProps {
  onNext: () => void;
}

export function PersonalInfoForm({ onNext }: PersonalInfoFormProps) {
  const { formData, setFormData } = useTaxForm();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Tax Savvy Calculator</h1>
        <p className="text-lg text-gray-600">
          Let's find out what should be your optimal tax liability
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Where can I send your personalised report?</Label>
          <Input
            id="email"
            type="email"
            placeholder="john.doe@example.com"
            value={formData.personalInfo.email}
            onChange={(e) =>
              setFormData((prev) => ({
                ...prev,
                personalInfo: { ...prev.personalInfo, email: e.target.value },
              }))
            }
            required
            className="w-full"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="birthDate">What is your Birth date?</Label>
          <div className="relative">
            <Input
              id="birthDate"
              type="date"
              value={formData.personalInfo.birthDate}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  personalInfo: { ...prev.personalInfo, birthDate: e.target.value },
                }))
              }
              required
              className="w-full"
            />
            <Calendar className="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          </div>
        </div>

        <div className="space-y-2">
          <Label>Gender</Label>
          <div className="flex space-x-4">
            {["male", "female", "other"].map((gender) => (
              <div
                key={gender}
                className={`flex-1 cursor-pointer rounded-full border p-3 text-center transition-all ${
                  formData.personalInfo.gender === gender
                    ? "border-primary bg-primary/10"
                    : "border-gray-200 hover:border-primary/50"
                }`}
                onClick={() =>
                  setFormData((prev) => ({
                    ...prev,
                    personalInfo: { ...prev.personalInfo, gender: gender as "male" | "female" | "other" },
                  }))
                }
              >
                {gender.charAt(0).toUpperCase() + gender.slice(1)}
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="employmentType">Please select your employment type</Label>
          <Select
            value={formData.personalInfo.employmentType}
            onValueChange={(value) =>
              setFormData((prev) => ({
                ...prev,
                personalInfo: { ...prev.personalInfo, employmentType: value },
              }))
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select employment type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="salaried">Salaried</SelectItem>
              <SelectItem value="self-employed">Self Employed</SelectItem>
              <SelectItem value="business">Business</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="residencyCountry">
            Please select your residency country of last 12 months
          </Label>
          <Select
            value={formData.personalInfo.residencyCountry}
            onValueChange={(value) =>
              setFormData((prev) => ({
                ...prev,
                personalInfo: { ...prev.personalInfo, residencyCountry: value },
              }))
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select your country" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="india">India</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="dependentParents"
            checked={formData.personalInfo.hasDependentSeniorParents}
            onCheckedChange={(checked) =>
              setFormData((prev) => ({
                ...prev,
                personalInfo: {
                  ...prev.personalInfo,
                  hasDependentSeniorParents: checked as boolean,
                },
              }))
            }
          />
          <Label htmlFor="dependentParents">Do you have dependent senior parents?</Label>
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" className="bg-primary hover:bg-primary-hover">
          Next
        </Button>
      </div>
    </form>
  );
}
