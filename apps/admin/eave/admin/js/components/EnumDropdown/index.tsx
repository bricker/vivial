import { MenuItem, TextField } from "@mui/material";
import React, { useState } from "react";

function getEnumValues<T extends object>(enumObj: T): string[] {
  return Object.values(enumObj) as string[];
}

interface EnumDropdownProps<T extends object> {
  enumType: T; // The enum to create the dropdown values from
  label?: string; // Optional label for the dropdown
  initialValue?: keyof T | null;
  onChange?: (value: keyof T | "") => void;
  disabled?: boolean;
}

const EnumDropdown = <T extends object>({
  enumType,
  label = "Select an option",
  initialValue,
  onChange,
  disabled = false,
}: EnumDropdownProps<T>) => {
  // NOTE: makes assumption that this will only be used w/ string enums
  const fixedInitialValue = initialValue ? (enumType[initialValue] as string) : "";
  const [selectedOption, setSelectedOption] = useState<string>(fixedInitialValue);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    setSelectedOption(newValue);
    if (onChange) {
      onChange(newValue as keyof T | "");
    }
  };

  const enumValues = getEnumValues(enumType);

  return (
    <TextField select label={label} value={selectedOption} onChange={handleChange} disabled={disabled} fullWidth>
      <MenuItem value="">None</MenuItem>
      {enumValues.map((value) => (
        <MenuItem key={value} value={value}>
          {value}
        </MenuItem>
      ))}
    </TextField>
  );
};

export default EnumDropdown;
