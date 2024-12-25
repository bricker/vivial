import { RootState } from "$eave-dashboard/js/store";
import { fontFamilies } from "$eave-dashboard/js/theme/fonts";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { imageUrl } from "$eave-dashboard/js/util/asset";
import { formatPhoneNumber } from "$eave-dashboard/js/util/phoneNumber";
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
}));

const RoundableInput = styled(Input)<{ rounded: Corner[] }>(({ theme, rounded }) => ({
  padding: "5px 16px",
  fontFamily: fontFamilies.inter,
  fontSize: rem(16),
  lineHeight: rem(30),
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
  fontSize: rem(12),
  lineHeight: rem(16),
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  marginBottom: 8,
  padding: "0 16px",
}));

const InputContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: 8,
}));

const HeaderContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "flex-end",
}));

const CenteringContainer = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "24px 40px",
}));

const StripeImg = styled("img")(() => ({
  height: rem(24),
  maxHeight: 32,
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
  showStripeBadge,
}: {
  reserverDetails: ReserverFormFields;
  onChange: (key: keyof ReserverFormFields, value: string) => void;
  isLoading: boolean;
  error?: string;
  showStripeBadge?: boolean;
}) => {
  const email = useSelector((state: RootState) => state.auth.account?.email);
  // if there's no id value on reserverDetails, that means there's no db entry yet server-side
  const shouldShowEmail = !!(email && reserverDetails.id);
  return (
    <InputContainer>
      <HeaderContainer>
        <Typography variant="subtitle2">Your information</Typography>

        {showStripeBadge && <StripeImg src={imageUrl("powered-by-stripe.png")} alt="powered by stripe" />}
      </HeaderContainer>

      {isLoading ? (
        <CenteringContainer>
          <CircularProgress color="secondary" />
        </CenteringContainer>
      ) : (
        <FieldsContainer>
          <NameInputContainer>
            <RoundableInput
              placeholder="First name"
              value={reserverDetails.firstName}
              onChange={(e) => onChange("firstName", e.target.value)}
              rounded={[Corner.TOP_LEFT]}
              required
            />
            <RoundableInput
              placeholder="Last name"
              value={reserverDetails.lastName}
              onChange={(e) => onChange("lastName", e.target.value)}
              rounded={[Corner.TOP_RIGHT]}
              required
            />
          </NameInputContainer>
          <RoundableInput
            placeholder="Phone #"
            value={reserverDetails.phoneNumber}
            onChange={(e) => onChange("phoneNumber", e.target.value)}
            onKeyUp={formatPhoneNumber}
            rounded={shouldShowEmail ? [] : [Corner.BOTTOM_LEFT, Corner.BOTTOM_RIGHT]}
            required
            type="tel"
          />
          {shouldShowEmail && (
            <RoundableInput
              value={email}
              contentEditable={false}
              disabled={true}
              rounded={[Corner.BOTTOM_LEFT, Corner.BOTTOM_RIGHT]}
              required
              type="email"
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
