import { Button } from "@mui/material";
import React from "react";
import CopyIcon from "../../Icons/CopyIcon";

const CopyableTextButton = ({ text }: { text: string }) => {
  return (
    <Button onClick={() => navigator.clipboard.writeText(text)} variant="outlined" endIcon={<CopyIcon />}>
      {text}
    </Button>
  );
};

export default CopyableTextButton;
