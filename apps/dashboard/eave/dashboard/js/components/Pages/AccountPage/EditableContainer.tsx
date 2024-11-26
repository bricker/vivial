import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { Button, Typography, styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import AccountBookingInfoEditForm from "../../Forms/AccountBookingInfoEditForm";
import EditIcon from "../../Icons/EditIcon";

const FormContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRadius: 15,
  padding: "24px 40px",
}));

const TitleContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const LabeledInfoContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
}));

const LabelText = styled("p")(({ theme }) => ({
  color: theme.palette.text.secondary,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
  fontFamily: fontFamilies.inter,
  fontWeight: 400,
  margin: 0,
}));

const ValueText = styled("p")(({ theme }) => ({
  color: theme.palette.text.primary,
  fontSize: rem("16px"),
  lineHeight: rem("30px"),
  fontFamily: fontFamilies.inter,
  fontWeight: 400,
  margin: 0,
}));

const ShiftedButton = styled(Button)(() => ({
  position: "relative",
  right: -16,
}));

const InfoContainer = styled("div")(() => ({
  // margin: "24px 0",
  marginTop: 24,
}));

const InfoDisplay = ({ name, email, phoneNumber }: { name: string; email: string; phoneNumber: string }) => {
  const displayContent: Array<{ label: string; value: string }> = [
    { label: "Name", value: name },
    { label: "Email", value: email },
    { label: "Phone #", value: phoneNumber },
  ];

  return (
    <>
      {displayContent.map((text) => (
        <LabeledInfoContainer>
          <LabelText>{text.label}</LabelText>
          <ValueText>{text.value}</ValueText>
        </LabeledInfoContainer>
      ))}
    </>
  );
};

const EditableContainer = () => {
  const [isEditting, setIsEditting] = useState(false);

  // TODO: set from store
  const firstName = "Lana";
  const lastName = "Nguyen";
  const email = "lana@eave.fyi";
  const phoneNumber = "123 456-7890";

  // TODO: get account info from store
  const handleCancel = () => setIsEditting(false);
  const handleSubmit = useCallback(() => {
    // TODO: call account info update query
    // TODO: store updated account info

    // TODO: on success
    handleCancel();
  }, []);

  return (
    <FormContainer>
      <TitleContainer>
        <Typography variant="h2">Booking info</Typography>
        {!isEditting && (
          <ShiftedButton onClick={() => setIsEditting(true)}>
            <EditIcon />
          </ShiftedButton>
        )}
      </TitleContainer>

      <InfoContainer>
        {isEditting ? (
          <AccountBookingInfoEditForm
            initFirstName={firstName}
            initLastName={lastName}
            initEmail={email}
            initPhoneNumber={phoneNumber}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={false}
          />
        ) : (
          <InfoDisplay name={`${firstName} ${lastName}`} email={email} phoneNumber={phoneNumber} />
        )}
      </InfoContainer>
    </FormContainer>
  );
};

export default EditableContainer;
