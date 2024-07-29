import { textStyles } from "$eave-dashboard/js/theme";
import classNames from "classnames";
import React from "react";
import { makeStyles } from "tss-react/mui";
import CodeBlock from "./CodeBlock";

const useStyles = makeStyles()((theme) => ({
  container: {
    display: "flex",
    width: "100%",
    justifyContent: "center",
    alignItems: "flex-start",
  },
  leftSideContainer: {
    flex: 1,
    display: "flex",
    gap: theme.spacing(1),
    marginRight: theme.spacing(2),
    minHeight: theme.spacing(20),
  },
  instructions: {
    flex: 1,
  },
  codeBlock: {
    flex: 2,
    height: "100%",
    overflow: "hidden", // Ensure the code block doesn't overflow
  },
  number: {
    margin: 0,
    border: "2px solid",
    width: "40px",
    height: "40px",
    display: "inline-block",
    borderRadius: "50%",
    textAlign: "center",
    lineHeight: "36px", // (height - border width * 2)
  },
}));

interface Props {
  header: string;
  subHeader?: string;
  code: string;
  codeHeader: string;
  codeLanguage: string;
  stepNumber: number;
}

export const SetupStep = ({ header, subHeader, code, codeHeader, stepNumber, codeLanguage }: Props) => {
  const { classes } = useStyles();
  const { classes: text } = textStyles();

  return (
    <div className={classes.container}>
      {/* Left Side */}
      <div className={classes.leftSideContainer}>
        {/* Instructions */}
        <h1 className={classNames(text.bold, classes.number, text.header)}>{stepNumber}</h1>
        <div className={classes.instructions}>
          {/* Step */}
          <h1 className={text.header}>{header}</h1>
          {/* SubStep */}
          {subHeader && <h2 className={text.subHeader}>{subHeader}</h2>}
        </div>
      </div>
      {/* CodeBlock */}
      <div className={classes.codeBlock}>
        <CodeBlock codeString={code} codeHeader={codeHeader} codeLanguage={codeLanguage} />
      </div>
    </div>
  );
};
