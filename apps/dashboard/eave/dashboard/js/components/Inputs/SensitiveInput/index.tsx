import { styled } from "@mui/material";
import { InputProps } from "@mui/material/Input";
import React, { useCallback, useState } from "react";

import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";

import HiddenIcon from "../../Icons/HiddenIcon";
import VisibleIcon from "../../Icons/VisibleIcon";
import Input from "../Input";

const VisibilityButton = styled(IconButton)(() => ({
  padding: 0,
}));

const SensitiveInput = (props: InputProps) => {
  const [showInput, setShowInput] = useState(false);
  const type = showInput ? "text" : "password";
  const ariaLabel = showInput ? "Hide the input." : "Display the input.";

  const handleShowInput = useCallback(() => {
    setShowInput(!showInput);
  }, [showInput]);

  return (
    <Input
      type={type}
      endAdornment={
        <InputAdornment position="end">
          <VisibilityButton onClick={handleShowInput} aria-label={ariaLabel}>
            {showInput ? <VisibleIcon /> : <HiddenIcon />}
          </VisibilityButton>
        </InputAdornment>
      }
      {...props}
    />
  );
};

export default SensitiveInput;
