import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React, { useState } from "react";
import PrimaryButton from "../../Buttons/PrimaryButton";
import SecondaryButton from "../../Buttons/SecondaryButton";
import Input from "../../Inputs/Input";
import InputError from "../../Inputs/InputError";

const SpreadButtonsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const FieldsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
  marginBottom: 24,
}));

const NameInputContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  gap: 8,
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
}));

const PaddedPrimaryButton = styled(PrimaryButton)(() => ({
  padding: "10px 14px",
  minWidth: rem("76px"),
}));

const PaddedSecondaryButton = styled(SecondaryButton)(() => ({
  padding: "10px 14px",
  minWidth: rem("76px"),
}));

const AccountBookingInfoEditForm = ({
  initFirstName,
  initLastName,
  initEmail,
  initPhoneNumber,
  onSubmit,
  onCancel,
  externalError,
  isLoading = false,
}: {
  initFirstName: string;
  initLastName: string;
  initEmail: string;
  initPhoneNumber: string;
  onSubmit: () => void;
  onCancel: () => void;
  externalError?: string;
  isLoading: boolean;
}) => {
  const [firstName, setFirstName] = useState(initFirstName);
  const [lastName, setLastName] = useState(initLastName);
  const [email, setEmail] = useState(initEmail);
  const [phoneNumber, setPhoneNumber] = useState(initPhoneNumber);
  const [internalError, setInternalError] = useState<string | undefined>(undefined);
  const error = internalError || externalError;

  function checkInputs({ first, last, email, phone }: { first: string; last: string; email: string; phone: string }) {
    if (first.length === 0) {
      setInternalError("First name required");
    } else if (last.length === 0) {
      setInternalError("Last name required");
    } else if (email.length === 0) {
      setInternalError("Email required");
    } else if (phone.length === 0) {
      setInternalError("Phone number required");
    } else {
      // all good
      setInternalError(undefined);
    }
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    checkInputs({ first: firstName, last: lastName, email: newEmail, phone: phoneNumber });
  };
  const handleFirstNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFirst = e.target.value;
    setFirstName(newFirst);
    checkInputs({ first: newFirst, last: lastName, email, phone: phoneNumber });
  };
  const handleLastNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newLast = e.target.value;
    setLastName(newLast);
    checkInputs({ first: firstName, last: newLast, email, phone: phoneNumber });
  };
  const handlePhoneNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPhone = e.target.value;
    setPhoneNumber(newPhone);
    checkInputs({ first: firstName, last: lastName, email, phone: newPhone });
  };

  return (
    <>
      <FieldsContainer>
        <NameInputContainer>
          <BoldInput placeholder="First name" value={firstName} onChange={handleFirstNameChange} />
          <BoldInput placeholder="Last name" value={lastName} onChange={handleLastNameChange} />
        </NameInputContainer>
        <BoldInput placeholder="Email" value={email} onChange={handleEmailChange} />
        <BoldInput placeholder="Phone #" value={phoneNumber} onChange={handlePhoneNumberChange} />
      </FieldsContainer>

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}

      <SpreadButtonsContainer>
        <PaddedSecondaryButton onClick={onCancel}>Cancel</PaddedSecondaryButton>
        <PaddedPrimaryButton onClick={onSubmit}>Save</PaddedPrimaryButton>
      </SpreadButtonsContainer>
    </>
  );
};

export default AccountBookingInfoEditForm;
