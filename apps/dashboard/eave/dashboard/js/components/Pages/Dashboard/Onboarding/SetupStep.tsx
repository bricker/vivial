import React from "react";
import { makeStyles } from "tss-react/mui";
import CodeBlock from "./CodeBlock";

const useStyles = makeStyles()((theme) => ({
  container: {
    display: "flex",
    border: "2px solid",
    width: "100%",
    justifyContent: "center",
    alignItems: "center",
  },
  instructions: {
    width: 400,
    marginRight: "16px",
    border: "2px solid",
    height: 180,
  },
  codeBlock: {
    width: 800,
    height: "100%",
    border: "2px solid",
  },
  header: {
    fontSize: 24,
    fontWeight: "normal",
    lineHeight: 1.25,
  },
  subHeader: {
    fontSize: 20,
    fontWeight: "normal",
  },
}));

interface Props {
  header: string;
  subHeader?: string;
  code: string;
  codeHeader: string;
}

export const SetupStep = ({ header, subHeader, code, codeHeader }: Props) => {
  const { classes } = useStyles();

  return (
    <div className={classes.container}>
      {/* Instructions */}
      <div className={classes.instructions}>
        {/* Step */}
        <h1 className={classes.header}>{header}</h1>
        {/* SubStep */}
        {subHeader && <h2 className={classes.subHeader}>{subHeader}</h2>}
      </div>
      {/* CodeBlock */}
      <div className={classes.codeBlock}>
        <CodeBlock codeString={code} codeHeader={codeHeader} />
      </div>
    </div>
  );
};
