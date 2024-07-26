import { textStyles } from "$eave-dashboard/js/theme";
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
  instructions: {
    flex: 1,
    marginRight: theme.spacing(2),
    minHeight: theme.spacing(20),
  },
  codeBlock: {
    flex: 2,
    height: "100%",
    overflow: "hidden", // Ensure the code block doesn't overflow
  },
}));

interface Props {
  header: string;
  subHeader?: string;
  code: string;
  codeHeader: string;
}

export const SetupStep = ({ header, subHeader, code, codeHeader }: Props) => {
  const { classes: localClasses } = useStyles();
  const { classes: text } = textStyles();

  return (
    <div className={localClasses.container}>
      {/* Instructions */}
      <div className={localClasses.instructions}>
        {/* Step */}
        <h1 className={text.header}>{header}</h1>
        {/* SubStep */}
        {subHeader && <h2 className={text.subHeader}>{subHeader}</h2>}
      </div>
      {/* CodeBlock */}
      <div className={localClasses.codeBlock}>
        <CodeBlock codeString={code} codeHeader={codeHeader} />
      </div>
    </div>
  );
};
