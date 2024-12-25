import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";

import Typography from "@mui/material/Typography";
import BackButton from "../../Buttons/BackButton";
import ExternalLink from "../../Links/ExternalLink";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
  maxWidth: 600,
  margin: "0 auto",
}));

const CopyContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRadius: 15,
  padding: "32px 40px",
}));

const Subtitle = styled(Typography)(() => ({
  fontSize: rem(18),
  lineHeight: rem(22),
  marginTop: 16,
}));

const HelpPage = () => {
  return (
    <PageContainer>
      <BackButton />
      <CopyContainer>
        <Typography variant="h3">Help</Typography>
        <Subtitle>
          Have a question or need help with a booking? Reach out to us at{" "}
          <ExternalLink to="mailto:friends@vivialapp.com">friends@vivialapp.com</ExternalLink>.
        </Subtitle>
      </CopyContainer>
    </PageContainer>
  );
};

export default HelpPage;
