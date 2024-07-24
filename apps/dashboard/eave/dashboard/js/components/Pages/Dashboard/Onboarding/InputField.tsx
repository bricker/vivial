"use client";
import React, { useState } from "react";
import { StylesConfig } from "react-select";
import CreatableSelect from "react-select/creatable";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  questionText: {
    fontSize: 18,
    fontWeight: "bold",
    margin: 0,
  },
  question: {
    // border: "2px solid",
    marginTop: theme.spacing(2),
  },
  errorContainer: {
    margin: 0,
    height: "20px",
    color: "red",
  },
}));

interface ColourOption {
  readonly value: string;
  readonly label: string;
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
    margin: 0,
    height: "50px", // set a fixed height
  }),
};

interface InputFieldProps {
  question: string;
  questionOptions: ColourOption[];
  error: boolean;
  setValue: (value: readonly ColourOption[]) => void;
}

const InputField: React.FC<InputFieldProps> = ({ question, questionOptions, setValue, error }) => {
  const { classes } = useStyles();
  const [options, setOptions] = useState<readonly ColourOption[]>(questionOptions);
  const [value, setValueState] = useState<readonly ColourOption[]>([]);

  const handleCreate = (inputValue: string) => {
    const newOption: ColourOption = {
      value: inputValue,
      label: inputValue,
    };
    setOptions((prev) => [...prev, newOption]);
    setValueState((prev) => [...prev, newOption]);
    setValue([...value, newOption]);
  };

  const handleChange = (newValue: readonly ColourOption[]) => {
    setValueState(newValue);
    setValue(newValue);
  };

  return (
    <div className={classes.question}>
      <p className={classes.questionText}>
        {" "}
        {question}
        <span style={{ color: "red" }}> *</span>{" "}
      </p>
      <CreatableSelect
        closeMenuOnSelect={false}
        isMulti
        options={options}
        styles={colourStyles}
        onCreateOption={handleCreate}
        value={value}
        onChange={(newValue) => handleChange(newValue as ColourOption[])}
        formatCreateLabel={(inputValue) => <div style={{ color: "#1980DF" }}>Create "{inputValue}"</div>}
      />
      <div className={classes.errorContainer}>{error && <span>This field is required</span>}</div>
    </div>
  );
};

export default InputField;
