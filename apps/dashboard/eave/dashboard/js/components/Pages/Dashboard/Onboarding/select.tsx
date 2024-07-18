"use client";
import React, { useState } from "react";
import { StylesConfig } from "react-select";
import CreatableSelect from "react-select/creatable";

interface ColourOption {
  readonly value: string;
  readonly label: string;
  readonly color: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

const colourOptions: ColourOption[] = [
  { value: "ocean", label: "Ocean", color: "#1980DF", isFixed: true },
  { value: "blue", label: "Blue", color: "#1980DF", isDisabled: true },
  { value: "purple", label: "Purple", color: "#1980DF" },
  { value: "red", label: "Red", color: "#1980DF", isFixed: true },
  { value: "orange", label: "Orange", color: "#1980DF" },
  { value: "yellow", label: "Yellow", color: "#1980DF" },
  { value: "green", label: "Green", color: "#1980DF" },
  { value: "forest", label: "Forest", color: "#1980DF" },
  { value: "slate", label: "Slate", color: "#1980DF" },
  { value: "silver", label: "Silver", color: "#1980DF" },
];

const colourStyles: StylesConfig<ColourOption, true> = {
  control: (styles) => ({ ...styles, backgroundColor: "white" }),
  option: (styles, { data, isDisabled, isFocused, isSelected }) => {
    const backgroundColor = isDisabled ? undefined : isSelected ? data.color : isFocused ? "#EEEEEE" : undefined;
    const color = isDisabled ? "#ccc" : isSelected ? "#fff" : data.color;

    return {
      ...styles,
      backgroundColor,
      color,
      cursor: isDisabled ? "not-allowed" : "default",
      ":active": {
        ...styles[":active"],
        backgroundColor: !isDisabled ? (isSelected ? data.color : "#EEEEEE") : undefined,
      },
    };
  },
  multiValue: (styles, { data }) => {
    return {
      ...styles,
      backgroundColor: "#E8F4FF",
    };
  },
  multiValueLabel: (styles, { data }) => ({
    ...styles,
    color: data.color,
    // fontSize: 36,
  }),
  multiValueRemove: (styles, { data }) => ({
    ...styles,
    color: data.color,
    ":hover": {
      backgroundColor: data.color,
      color: "white",
    },
  }),

  placeholder: (styles) => ({
    ...styles,
  }),
  menu: (base) => ({
    ...base,
    marginTop: -10,
  }),
  menuList: (provided, state) => ({
    ...provided,
    paddingTop: 0,
    paddingBottom: 0,
  }),
  container: (styles) => ({
    ...styles,
    width: "600px", // set a fixed width
    height: "50px", // set a fixed height
  }),
};

export default function Select() {
  const [options, setOptions] = useState<readonly ColourOption[]>(colourOptions);
  const [value, setValue] = useState<readonly ColourOption[]>([]);

  const handleCreate = (inputValue: string) => {
    const newOption: ColourOption = {
      value: inputValue,
      label: inputValue,
      color: "#1980DF",
    };
    setOptions((prev) => [...prev, newOption]);
    setValue((prev) => [...prev, newOption]);
  };

  return (
    <div>
      <CreatableSelect
        closeMenuOnSelect={false}
        isMulti
        options={options}
        styles={colourStyles}
        onCreateOption={handleCreate}
        value={value}
        onChange={(newValue) => setValue(newValue as ColourOption[])}
        formatCreateLabel={(inputValue) => <div style={{ color: "#1980DF" }}>Create "{inputValue}"</div>}
      />
    </div>
  );
}
