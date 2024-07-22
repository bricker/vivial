"use client";
import React, { useState } from "react";
import { StylesConfig } from "react-select";
import CreatableSelect from "react-select/creatable";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  questionText: {
    fontSize: 18,
    fontWeight: "bold",
    margin: 0,
  },

  question: {
    marginTop: 32,
  },
}));

interface ColourOption {
  readonly value: string;
  readonly label: string;
  readonly color: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

const colourStyles: StylesConfig<ColourOption, true> = {
  control: (styles) => ({ ...styles, backgroundColor: "white" }),
  option: (styles, { data, isDisabled, isFocused, isSelected }) => {
    const backgroundColor = isDisabled ? undefined : isSelected ? "#1980DF" : isFocused ? "#EEEEEE" : undefined;
    const color = isDisabled ? "#ccc" : isSelected ? "#fff" : "#1980DF";

    return {
      ...styles,
      backgroundColor,
      color,
      cursor: isDisabled ? "not-allowed" : "default",
      ":active": {
        ...styles[":active"],
        backgroundColor: !isDisabled ? (isSelected ? "#1980DF" : "#EEEEEE") : undefined,
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
    color: "#1980DF",
    // fontSize: 36,
  }),
  multiValueRemove: (styles, { data }) => ({
    ...styles,
    color: "#1980DF",
    ":hover": {
      backgroundColor: "#1980DF",
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

interface InputFieldProps {
  question: string;
  questionOptions: ColourOption[];
}

const InputField: React.FC<InputFieldProps> = ({ question, questionOptions }) => {
  const { classes } = useStyles();
  const [options, setOptions] = useState<readonly ColourOption[]>(questionOptions);
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
    <div className={classes.question}>
      <p className={classes.questionText}> {question} </p>
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
};

export default InputField;
