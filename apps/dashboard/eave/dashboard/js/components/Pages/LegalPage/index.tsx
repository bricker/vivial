import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";

import Typography from "@mui/material/Typography";
import BackButton from "../../Buttons/BackButton";

const PageContainer = styled("div")(() => ({
  padding: "24px 16px",
}));

const CopyContainer = styled("div")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  borderRadius: 15,
  padding: "32px 24px",
}));

const Title = styled(Typography)(() => ({
  fontWeight: 700,
  marginBottom: 16,
}));

const Body = styled(Typography)(() => ({
  fontSize: rem(18),
  lineHeight: rem(22),
}));

interface LegalPageProps {
  title: string;
  children: React.ReactNode;
}

const LegalPage = ({ title, children }: LegalPageProps) => {
  return (
    <PageContainer>
      <BackButton />
      <CopyContainer>
        <Title variant="h2">{title}</Title>
        <Body>{children}</Body>
      </CopyContainer>
    </PageContainer>
  );
};

export default LegalPage;
