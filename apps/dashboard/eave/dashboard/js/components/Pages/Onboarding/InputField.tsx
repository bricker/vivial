import { textStyles } from "$eave-dashboard/js/theme";
import classNames from "classnames";
import React, { useCallback, useEffect, useState } from "react";
import { StylesConfig } from "react-select";
import CreatableSelect from "react-select/creatable";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((_theme) => ({
  container: {
    flex: 1,
    height: "auto",
    display: "flex",
    flexDirection: "column",
  },
}));

interface QuestionOption {
  readonly value: string;
  readonly label: string;
  readonly isFixed?: boolean;
  readonly isDisabled?: boolean;
}

const colourStyles: StylesConfig<QuestionOption, true> = {
  // On hover, color options have a gray background
  option: (styles, { isFocused }) => {
    const backgroundColor = isFocused ? "#EEEEEE" : undefined;
    return {
      ...styles,
      backgroundColor,
    };
  },
  // Tag Color
  multiValue: (styles) => {
    return {
      ...styles,
      backgroundColor: "#E8F4FF",
    };
  },
  // Tag Text Color
  multiValueLabel: (styles) => ({
    ...styles,
    color: "#1980DF",
  }),
  // Removing Colors
  multiValueRemove: (styles) => ({
    ...styles,
    color: "#1980DF",
    ":hover": {
      backgroundColor: "#1980DF",
      color: "white",
    },
  }),
};

interface InputFieldProps {
  question: string;
  questionOptions: QuestionOption[];
  setValue: (value: readonly QuestionOption[]) => void;
}

const InputField: React.FC<InputFieldProps> = ({ question, questionOptions, setValue }) => {
  const { classes } = useStyles();
  const { classes: text } = textStyles();
  const [options, setOptions] = useState<readonly QuestionOption[]>(questionOptions);

  // Set the value displayed based on local storage
  const [displayValue, setValueState] = useState<readonly QuestionOption[]>(() => {
    const storedValue = localStorage.getItem(question);
    return storedValue ? JSON.parse(storedValue) : [];
  });

  // On mount update the value submitted if necessary
  useEffect(() => {
    const storedValue = localStorage.getItem(question);
    if (storedValue) {
      setValue(JSON.parse(storedValue));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(question, JSON.stringify(displayValue));
  }, [displayValue, question]);

  const handleCreate = useCallback(
    (inputValue: string) => {
      const newOption: QuestionOption = {
        value: inputValue,
        label: inputValue,
      };
      setOptions((prev) => [...prev, newOption]);
      setValueState((prev) => [...prev, newOption]);
      const newValue = [...displayValue, newOption];
      setValue(newValue);
    },
    [setOptions, setValueState, setValue, questionOptions],
  );

  const handleChange = (newValue: readonly QuestionOption[]) => {
    setValueState(newValue);
    setValue(newValue);
  };

  return (
    <div className={classes.container}>
      <p className={classNames(text.body, text.bold)}>
        {question}
        <span style={{ color: "red" }}> *</span>
      </p>
      <CreatableSelect
        closeMenuOnSelect={false}
        isMulti
        options={options}
        styles={colourStyles}
        onCreateOption={handleCreate}
        value={displayValue}
        onChange={handleChange}
        formatCreateLabel={(inputValue) => <div style={{ color: "#1980DF" }}>Create "{inputValue}"</div>}
      />
    </div>
  );
};

export default InputField;
