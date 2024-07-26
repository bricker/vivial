"use client";
import { textStyles } from "$eave-dashboard/js/theme";
import React, { useState } from "react";
import { StylesConfig } from "react-select";
import CreatableSelect from "react-select/creatable";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  question: {
    marginTop: theme.spacing(2),
  },
  errorContainer: {
    margin: 0,
    height: "20px",
    color: "red",
  },
}));

interface QuestionOption {
  readonly value: string;
  readonly label: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

const colourStyles: StylesConfig<QuestionOption, true> = {
  option: (styles, { data, isDisabled, isFocused, isSelected }) => {
    const backgroundColor = isDisabled ? undefined : isSelected ? "#1980DF" : isFocused ? "#EEEEEE" : undefined;
    const color = isDisabled ? "#ccc" : "#1980DF";
    return {
      ...styles,
      backgroundColor,
      color,
      cursor: isDisabled ? "not-allowed" : "default",
    };
  },
  multiValue: (styles) => {
    return {
      ...styles,
      backgroundColor: "#E8F4FF",
    };
  },
  multiValueLabel: (styles, { data }) => ({
    ...styles,
    color: "#1980DF",
  }),
  multiValueRemove: (styles, { data }) => ({
    ...styles,
    color: "#1980DF",
    ":hover": {
      backgroundColor: "#1980DF",
      color: "white",
    },
  }),
  menu: (base) => ({
    ...base,
    marginTop: -10,
  }),
  container: (styles) => ({
    ...styles,
    width: "100%",
    margin: 0,
    height: "50px",
  }),
};

interface InputFieldProps {
  question: string;
  questionOptions: QuestionOption[];
  error: boolean;
  setValue: (value: readonly QuestionOption[]) => void;
}

const InputField: React.FC<InputFieldProps> = ({ question, questionOptions, setValue, error }) => {
  const { classes } = useStyles();
  const { classes: text } = textStyles();
  const [options, setOptions] = useState<readonly QuestionOption[]>(questionOptions);
  const [value, setValueState] = useState<readonly QuestionOption[]>([]);

  const handleCreate = (inputValue: string) => {
    const newOption: QuestionOption = {
      value: inputValue,
      label: inputValue,
    };
    setOptions((prev) => [...prev, newOption]);
    setValueState((prev) => [...prev, newOption]);
    setValue([...value, newOption]);
  };

  const handleChange = (newValue: readonly QuestionOption[]) => {
    setValueState(newValue);
    setValue(newValue);
  };

  return (
    <div className={classes.question}>
      <p className={`${text.body} ${text.bold}`}>
        {question}
        <span style={{ color: "red" }}> *</span>
      </p>
      <CreatableSelect
        closeMenuOnSelect={false}
        isMulti
        options={options}
        styles={colourStyles}
        onCreateOption={handleCreate}
        value={value}
        onChange={(newValue) => handleChange(newValue as QuestionOption[])}
        formatCreateLabel={(inputValue) => <div style={{ color: "#1980DF" }}>Create "{inputValue}"</div>}
      />
      <div className={`${classes.errorContainer} ${text.body}`}>{error && <span>This field is required</span>}</div>
    </div>
  );
};

export default InputField;
