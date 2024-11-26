import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React, { useState } from "react";
import PrimaryButton from "../../Buttons/PrimaryButton";
import SecondaryButton from "../../Buttons/SecondaryButton";
import Input from "../../Inputs/Input";
import InputError from "../../Inputs/InputError";

const FormContent = styled("div")(() => ({
  padding: "0 40px",
}));

const SpreadButtonsContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const EmailInput = styled(Input)(() => ({
  marginBottom: 16,
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
  marginTop: 10,
  padding: "0 40px 0 56px",
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
    <FormContent>
      <NameInputContainer>
        <Input placeholder="First name" value={firstName} onChange={handleFirstNameChange} />
        <Input placeholder="Last name" value={lastName} onChange={handleLastNameChange} />
      </NameInputContainer>
      <EmailInput placeholder="Email" value={email} onChange={handleEmailChange} />
      <Input placeholder="Phone #" value={phoneNumber} onChange={handlePhoneNumberChange} />

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}

      <SpreadButtonsContainer>
        <SecondaryButton onClick={onCancel}>Cancel</SecondaryButton>
        <PrimaryButton onClick={onSubmit}>Submit</PrimaryButton>
      </SpreadButtonsContainer>
    </FormContent>
  );
};

export default AccountBookingInfoEditForm;
