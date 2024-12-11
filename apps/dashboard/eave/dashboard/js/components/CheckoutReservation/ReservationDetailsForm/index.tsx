import { RootState } from "$eave-dashboard/js/store";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";
import Input from "../../Inputs/Input";
import InputError from "../../Inputs/InputError";

const FieldsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 16,
  marginBottom: 24,
}));

const BoldInput = styled(Input)(() => ({
  padding: "5px 16px",
  fontFamily: fontFamilies.inter,
  fontWeight: 600,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
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
  marginTop: 24,
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
}: {
  reserverDetails: ReserverFormFields;
  onChange: (key: keyof ReserverFormFields, value: string) => void;
  error?: string;
}) => {
  const email = useSelector((state: RootState) => state.auth.account?.email);
  // if there's not id value on reserverDetails, that means there's no db entry yet server-side
  const shouldShowEmail = !!(email && reserverDetails.id);
  return (
    <InputContainer>
      <FieldsContainer>
        <BoldInput
          placeholder="First name"
          value={reserverDetails.firstName}
          onChange={(e) => onChange("firstName", e.target.value)}
        />
        <BoldInput
          placeholder="Last name"
          value={reserverDetails.lastName}
          onChange={(e) => onChange("lastName", e.target.value)}
        />
        <BoldInput
          placeholder="Phone #"
          value={reserverDetails.phoneNumber}
          onChange={(e) => onChange("phoneNumber", e.target.value)}
        />
        {shouldShowEmail && <BoldInput value={"email"} contentEditable={false} />}
      </FieldsContainer>

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}
    </InputContainer>
  );
};

export default ReservationDetailsForm;
