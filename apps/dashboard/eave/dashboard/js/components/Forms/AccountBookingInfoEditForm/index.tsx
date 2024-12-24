import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { formatPhoneNumber } from "$eave-dashboard/js/util/phoneNumber";
import { styled } from "@mui/material";
import * as EmailValidator from "email-validator";
import React, { useCallback, useState } from "react";
import LoadingButton from "../../Buttons/LoadingButton";
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
  fontSize: rem(16),
  lineHeight: rem(30),
}));

const InputErrorContainer = styled("div")(() => ({
  fontSize: rem(12),
  lineHeight: rem(16),
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 24,
  padding: "0 16px",
}));

const PaddedPrimaryButton = styled(LoadingButton)(() => ({
  padding: "10px 14px",
  minWidth: rem(76),
}));

const PaddedSecondaryButton = styled(SecondaryButton)(() => ({
  padding: "10px 14px",
  minWidth: rem(76),
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
  onSubmit: ({
    firstName,
    lastName,
    phoneNumber,
    email,
  }: {
    firstName: string;
    lastName: string;
    phoneNumber: string;
    email: string;
  }) => void;
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
  // only prevent submit on internalError since that can be fixed w/o another submit
  const submitButtonDisabled = !!(isLoading || internalError);

  function checkInputs({
    first,
    last,
    emailAddr,
    phone,
  }: {
    first: string;
    last: string;
    emailAddr: string;
    phone: string;
  }) {
    if (first.length === 0) {
      setInternalError("First name required");
    } else if (last.length === 0) {
      setInternalError("Last name required");
    } else if (emailAddr.length === 0) {
      setInternalError("Email required");
    } else if (!EmailValidator.validate(emailAddr)) {
      setInternalError("Invalid email");
    } else if (phone.length === 0) {
      setInternalError("Phone number required");
    } else {
      // all good
      setInternalError(undefined);
    }
  }

  const handleEmailChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newEmail = e.target.value;
      setEmail(newEmail);
      checkInputs({ first: firstName, last: lastName, emailAddr: newEmail, phone: phoneNumber });
    },
    [firstName, lastName, email, phoneNumber],
  );
  const handleFirstNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newFirst = e.target.value;
      setFirstName(newFirst);
      checkInputs({ first: newFirst, last: lastName, emailAddr: email, phone: phoneNumber });
    },
    [firstName, lastName, email, phoneNumber],
  );
  const handleLastNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newLast = e.target.value;
      setLastName(newLast);
      checkInputs({ first: firstName, last: newLast, emailAddr: email, phone: phoneNumber });
    },
    [firstName, lastName, email, phoneNumber],
  );
  const handlePhoneNumberChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newPhone = e.target.value;
      setPhoneNumber(newPhone);
      checkInputs({ first: firstName, last: lastName, emailAddr: email, phone: newPhone });
    },
    [firstName, lastName, email, phoneNumber],
  );
  const handleSubmit = useCallback(() => {
    onSubmit({ firstName, lastName, phoneNumber, email });
  }, [firstName, lastName, email, phoneNumber]);

  return (
    <>
      <FieldsContainer>
        <NameInputContainer>
          <BoldInput placeholder="First name" value={firstName} onChange={handleFirstNameChange} />
          <BoldInput placeholder="Last name" value={lastName} onChange={handleLastNameChange} />
        </NameInputContainer>
        <BoldInput placeholder="Email" value={email} onChange={handleEmailChange} />
        <BoldInput
          placeholder="Phone #"
          value={phoneNumber}
          onKeyUp={formatPhoneNumber}
          onChange={handlePhoneNumberChange}
        />
      </FieldsContainer>

      {error && (
        <InputErrorContainer>
          <InputError>{error}</InputError>
        </InputErrorContainer>
      )}

      <SpreadButtonsContainer>
        <PaddedSecondaryButton onClick={onCancel}>Cancel</PaddedSecondaryButton>
        <PaddedPrimaryButton onClick={handleSubmit} loading={isLoading} disabled={submitButtonDisabled}>
          Save
        </PaddedPrimaryButton>
      </SpreadButtonsContainer>
    </>
  );
};

export default AccountBookingInfoEditForm;
