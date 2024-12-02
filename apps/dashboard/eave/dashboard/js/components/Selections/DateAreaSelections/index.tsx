import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";

import MaterialButton, { ButtonProps } from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import SubmitButton from "../../Buttons/PrimaryButton";

interface DateAreaSelectionsProps {
  cta: string;
  onSubmit: (selectedRegionIds: string[]) => void;
  regions?: SearchRegion[];
}

interface SelectButtonProps extends ButtonProps {
  selected?: boolean;
}

const Rows = styled("div")(() => ({
  marginBottom: 20,
}));

const Row = styled("div")(() => ({
  display: "flex",
  padding: "12px 24px",
  borderBottom: "1.111px solid #595959",
  "&:first-of-type": {
    paddingLeft: 0,
  },
  "&:last-of-type": {
    borderBottom: "none !important",
  },
}));

const SelectButton = styled(MaterialButton, {
  shouldForwardProp: (prop) => prop !== "selected",
})<SelectButtonProps>(({ selected, theme }) => ({
  padding: 0,
  minWidth: 0,
  marginRight: 12,
  height: 24,
  width: 24,
  borderRadius: "50%",
  border: `1.111px solid ${theme.palette.text.primary}`,
  ...(selected && {
    backgroundColor: theme.palette.accent[1],
    border: "none",
  }),
}));

const DateAreaSelections = ({ cta, regions, onSubmit }: DateAreaSelectionsProps) => {
  const [selectedRegionIds, setSelectedRegionIds] = useState(regions?.map((region) => region.id) || []);

  const selectRegion = useCallback(
    (id: string) => {
      if (selectedRegionIds.includes(id)) {
        setSelectedRegionIds(selectedRegionIds.filter((x) => x !== id));
      } else {
        setSelectedRegionIds(selectedRegionIds.concat([id]));
      }
    },
    [selectedRegionIds],
  );

  const toggleSelectAll = useCallback(() => {
    if (regions) {
      if (selectedRegionIds.length === regions.length) {
        setSelectedRegionIds([]);
      } else {
        setSelectedRegionIds(regions.map((region) => region.id));
      }
    }
  }, [regions, selectedRegionIds]);

  const handleSubmit = useCallback(() => {
    onSubmit(selectedRegionIds);
  }, [selectedRegionIds]);

  return (
    <>
      <Rows>
        <Row>
          <SelectButton onClick={toggleSelectAll} selected={regions?.length === selectedRegionIds.length} />
          <Typography>All Areas</Typography>
        </Row>
        {regions?.map((region) => (
          <Row key={region.id}>
            <SelectButton onClick={() => selectRegion(region.id)} selected={selectedRegionIds.includes(region.id)} />
            <Typography>{region.name}</Typography>
          </Row>
        ))}
      </Rows>
      <SubmitButton onClick={handleSubmit} bg={colors.lightOrangeAccent} fullWidth>
        {cta}
      </SubmitButton>
    </>
  );
};

export default DateAreaSelections;
