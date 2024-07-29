import { buttonStyles } from "$eave-dashboard/js/theme";
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
}));

const COPY_BUTTON_TEXT = "Copy Code";
const COPIED_BUTTON_TEXT = "Copied";

export default function CodeBlock({ codeString, codeHeader }: { codeString: string; codeHeader: string }) {
  const [copy, setCopy] = useState(COPY_BUTTON_TEXT);
  const { classes } = useStyles();
  const { classes: button } = buttonStyles();

  return (
    <div className={classes.container}>
      <div className={classes.textContainer}>
        <p>{codeHeader}</p>
        <button
          className={button.invisible}
          onClick={() => {
            navigator.clipboard
              .writeText(codeString)
              .then(() => {
                setCopy(COPIED_BUTTON_TEXT);
                setTimeout(() => {
                  setCopy(COPY_BUTTON_TEXT);
                }, 3000);
              })
              .catch(() => {
                setCopy(COPY_BUTTON_TEXT);
              });
          }}
        >
          {copy}
        </button>
      </div>
      <div className={classes.codeBlock}>
        <SyntaxHighlighter
          language="javascript"
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
