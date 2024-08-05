import CheckmarkIcon from "$eave-dashboard/js/components/Icons/CheckmarkIcon";
import CopyIcon from "$eave-dashboard/js/components/Icons/CopyIcon";
import React, { useState } from "react";
import SyntaxHighlighter from "react-syntax-highlighter";
import { github } from "react-syntax-highlighter/dist/esm/styles/hljs";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  container: {
    border: "0.5px solid",
    borderColor: "#7D7D7D",
    borderRadius: "10px",
    overflow: "hidden",
    "& pre": {
      margin: 0,
    },
  },
  textContainer: {
    backgroundColor: "#EEEEEE",
    display: "flex",
    justifyContent: "space-between",
    paddingLeft: 10,
    paddingRight: 10,
    alignItems: "center",
  },
  codeBlock: {
    overflow: "auto",
    maxHeight: "400px",
  },
  button: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "transparent",
    border: "0px",
    cursor: "pointer",
    aspectRatio: 1,
    borderRadius: "20%", // Makes the button rounded
    "&:hover": {
      backgroundColor: "#E4E4E4",
    },
  },
}));

export default function CodeBlock({
  codeString,
  codeHeader,
  codeLanguage,
}: {
  codeString: string;
  codeHeader: string;
  codeLanguage: string;
}) {
  const [isCopied, setIsCopied] = useState(false);
  const { classes } = useStyles();

  return (
    <div className={classes.container}>
      <div className={classes.textContainer}>
        <p>{codeHeader}</p>
        <button
          className={classes.button}
          onClick={() => {
            navigator.clipboard
              .writeText(codeString)
              .then(() => {
                setIsCopied(true);
                setTimeout(() => {
                  setIsCopied(false);
                }, 1500);
              })
              .catch(() => {
                setIsCopied(false);
              });
          }}
        >
          {isCopied ? <CheckmarkIcon width="24px" height="24px" /> : <CopyIcon width="24px" height="24px" />}
        </button>
      </div>
      <div className={classes.codeBlock}>
        <SyntaxHighlighter
          language={codeLanguage}
          style={github}
          customStyle={{
            padding: "25px",
            lineHeight: 2,
          }}
        >
          {codeString}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
