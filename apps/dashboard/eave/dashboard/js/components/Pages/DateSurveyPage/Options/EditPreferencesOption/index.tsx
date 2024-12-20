import { styled } from "@mui/material";
import Typography from "@mui/material/Typography";
import React from "react";
import EditButton from "../../../../Buttons/EditButton";

const OptionContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.field.primary,
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  borderRadius: "8px",
  width: "100%",
  padding: "4px 8px 4px 16px",
  marginTop: 8,
  height: 40,
}));

const FlexContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
}));

interface EditableIndicator extends React.HTMLAttributes<HTMLDivElement> {
  editable: boolean;
}

const EditableIndicator = styled("div", {
  shouldForwardProp: (prop) => prop !== "editable",
})<EditableIndicator>(({ editable, theme }) => ({
  marginRight: 10,
  height: 16,
  width: 16,
  borderRadius: "50%",
  backgroundColor: theme.palette.primary.main,
  ...(editable && {
    border: `1px solid ${theme.palette.text.primary}`,
    backgroundColor: "transparent",
  }),
}));

interface EditPreferencesOptionProps {
  label: string;
  editable: boolean;
  onClickEdit: () => void;
}

const EditPreferencesOption = ({ label, editable, onClickEdit }: EditPreferencesOptionProps) => {
  return (
    <OptionContainer>
      <FlexContainer>
        <EditableIndicator editable={editable} />
        <Typography variant="subtitle1">{label}</Typography>
      </FlexContainer>
      {editable && <EditButton onClick={onClickEdit} small />}
    </OptionContainer>
  );
};

export default EditPreferencesOption;
