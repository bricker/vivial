import { RootState } from "$eave-dashboard/js/store";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { CircularProgress, Typography, styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";
import Input from "../../Inputs/Input";
import InputError from "../../Inputs/InputError";

enum Corner {
  TOP_LEFT,
  TOP_RIGHT,
  BOTTOM_LEFT,
  BOTTOM_RIGHT,
}

const FieldsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  marginBottom: 24,
}));

const BoldRoundableInput = styled(Input)<{ rounded: Corner[] }>(({ theme, rounded }) => ({
  padding: "5px 16px",
  fontFamily: fontFamilies.inter,
  fontWeight: 600,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
  borderStyle: "solid",
  borderWidth: 1,
  borderColor: theme.palette.grey[800],
  borderTopLeftRadius: rounded.includes(Corner.TOP_LEFT) ? 20 : 0,
  borderTopRightRadius: rounded.includes(Corner.TOP_RIGHT) ? 20 : 0,
  borderBottomLeftRadius: rounded.includes(Corner.BOTTOM_LEFT) ? 20 : 0,
  borderBottomRightRadius: rounded.includes(Corner.BOTTOM_RIGHT) ? 20 : 0,
}));

const NameInputContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
}));

const InputErrorContainer = styled("div")(() => ({
  fontSize: rem("12px"),
  lineHeight: rem("16px"),
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 24,
  padding: "0 16px",
}));

const InputContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const CenteringContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "24px 40px",
}));

export interface ReserverFormFields {
  id: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
}

const ReservationDetailsForm = ({
  reserverDetails,
  error,
  onChange,
  isLoading,
}: {
  reserverDetails: ReserverFormFields;
  onChange: (key: keyof ReserverFormFields, value: string) => void;
  isLoading: boolean;
  error?: string;
}) => {
  const email = useSelector((state: RootState) => state.auth.account?.email);
  // if there's no id value on reserverDetails, that means there's no db entry yet server-side
  const shouldShowEmail = !!(email && reserverDetails.id);
  return (
    <InputContainer>
      <Typography variant="subtitle2">Your information</Typography>

      {isLoading ? (
        <CenteringContainer>
          <CircularProgress color="secondary" />
        </CenteringContainer>
      ) : (
        <FieldsContainer>
          <NameInputContainer>
            <BoldRoundableInput
              placeholder="First name"
              value={reserverDetails.firstName}
              onChange={(e) => onChange("firstName", e.target.value)}
              rounded={[Corner.TOP_LEFT]}
            />
            <BoldRoundableInput
              placeholder="Last name"
              value={reserverDetails.lastName}
              onChange={(e) => onChange("lastName", e.target.value)}
              rounded={[Corner.TOP_RIGHT]}
            />
          </NameInputContainer>
          <BoldRoundableInput
            placeholder="Phone #"
            value={reserverDetails.phoneNumber}
            onChange={(e) => onChange("phoneNumber", e.target.value)}
            rounded={shouldShowEmail ? [] : [Corner.BOTTOM_LEFT, Corner.BOTTOM_RIGHT]}
          />
          {shouldShowEmail && (
            <BoldRoundableInput
              value={email}
              contentEditable={false}
              disabled={true}
              rounded={[Corner.BOTTOM_LEFT, Corner.BOTTOM_RIGHT]}
            />
          )}
        </FieldsContainer>
      )}

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}
    </InputContainer>
  );
};

export default ReservationDetailsForm;
