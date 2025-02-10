
import { useTaxForm } from "@/context/TaxFormContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Mail, Calendar, Briefcase, Globe, Mars, Venus, Person, Calculator } from "lucide-react";

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
    <form onSubmit={handleSubmit} className="space-y-6 bg-gradient-to-br from-white to-purple-50">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Calculator className="h-8 w-8 text-purple-600" />
          Tax Savvy Calculator
        </h1>
        <p className="text-lg text-gray-600">
          Let's find out what should be your optimal tax liability
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className="flex items-center gap-2">
            <Mail className="h-4 w-4" />
            Where can I send your personalised report?
          </Label>
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
          <Label htmlFor="birthDate" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            What is your Birth date?
          </Label>
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
        </div>

        <div className="space-y-2">
          <Label className="flex items-center gap-2">Gender</Label>
          <div className="flex space-x-4">
            {[
              { value: "male", icon: Mars },
              { value: "female", icon: Venus },
              { value: "other", icon: Person },
            ].map(({ value, icon: Icon }) => (
              <div
                key={value}
                onClick={() =>
                  setFormData((prev) => ({
                    ...prev,
                    personalInfo: { ...prev.personalInfo, gender: value as "male" | "female" | "other" },
                  }))
                }
                className={`flex-1 cursor-pointer rounded-full border p-4 flex justify-center transition-all ${
                  formData.personalInfo.gender === value
                    ? "border-purple-500 bg-purple-50"
                    : "border-gray-200 hover:border-purple-200"
                }`}
              >
                <Icon
                  className={`h-6 w-6 ${
                    formData.personalInfo.gender === value ? "text-purple-500" : "text-gray-500"
                  }`}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="employmentType" className="flex items-center gap-2">
            <Briefcase className="h-4 w-4" />
            Please select your employment type
          </Label>
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
          <Label htmlFor="residencyCountry" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
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
        <Button type="submit" className="bg-purple-600 hover:bg-purple-700">
          Next
        </Button>
      </div>
    </form>
  );
}
