import { type SearchRegion } from "$eave-dashboard/js/graphql/generated/graphql";
import { colors } from "$eave-dashboard/js/theme/colors";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";

import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import SubmitButton from "../../Buttons/PrimaryButton";

const Rows = styled("div")(() => ({
  marginBottom: 20,
}));

const Row = styled("div")(() => ({
  display: "flex",
  padding: "6px 24px",
  borderBottom: "1.111px solid #595959",
  "&:first-of-type": {
    paddingLeft: 0,
  },
  "&:last-of-type": {
    borderBottom: "none !important",
  },
}));

interface SelectedIndicatorProps extends React.HTMLAttributes<HTMLDivElement> {
  selected: boolean;
}

const SelectedIndicator = styled("div", {
  shouldForwardProp: (prop) => prop !== "selected",
})<SelectedIndicatorProps>(({ selected, theme }) => ({
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

const SelectButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  "&:hover": {
    backgroundColor: "transparent",
  },
}));

interface DateAreaSelectionsProps {
  cta: string;
  onSubmit: (selectedRegionIds: string[]) => void;
  regions?: SearchRegion[];
}

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
          <SelectButton onClick={toggleSelectAll} disableRipple>
            <SelectedIndicator selected={regions?.length === selectedRegionIds.length} />
            <Typography>All Areas</Typography>
          </SelectButton>
        </Row>
        {regions?.map((region) => (
          <Row key={region.id}>
            <SelectButton onClick={() => selectRegion(region.id)} disableRipple>
              <SelectedIndicator selected={selectedRegionIds.includes(region.id)} />
              <Typography noWrap>{region.name}</Typography>
            </SelectButton>
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
