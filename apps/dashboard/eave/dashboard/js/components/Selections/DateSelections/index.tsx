import { OutingBudget } from "$eave-dashboard/js/graphql/generated/graphql";
import { colors } from "$eave-dashboard/js/theme/colors";
import { rem } from "$eave-dashboard/js/theme/helpers/rem";
import { styled } from "@mui/material";
import React from "react";

import HighlightButton from "../../Buttons/HighlightButton";
import LoadingButton from "../../Buttons/LoadingButton";

const Row = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  marginBottom: 16,
}));

const RowTitle = styled("div")(({ theme }) => ({
  color: theme.palette.grey[400],
  fontSize: rem("16px"),
  lineHeight: rem("19px"),
  fontWeight: 500,
  minWidth: 60,
}));

const RowButtons = styled("div")(() => ({
  display: "flex",
}));

const SelectButton = styled(HighlightButton)(() => ({
  marginRight: 8,
  "&:last-of-type": {
    marginRight: 0,
  },
}));

const SubmitButton = styled(LoadingButton)(() => ({
  marginTop: 8,
}));

interface DateSelectionsProps {
  cta: string;
  headcount: number;
  startTime: string;
  searchArea: string;
  budget: OutingBudget;
  onSubmit: () => void;
  onSelectHeadcount: (value: number) => void;
  onSelectBudget: (value: OutingBudget) => void;
  onSelectStartTime: () => void;
  onSelectSearchArea: () => void;
}

const DateSelections = ({
  cta,
  headcount,
  startTime,
  searchArea,
  budget,
  onSubmit,
  onSelectHeadcount,
  onSelectBudget,
  onSelectStartTime,
  onSelectSearchArea,
}: DateSelectionsProps) => {
  return (
    <>
      <Row>
        <RowTitle>Who:</RowTitle>
        <RowButtons>
          <SelectButton
            onClick={() => onSelectHeadcount(2)}
            highlighted={headcount === 2}
            highlightColor={colors.lightPinkAccent}
          >
            👥 For 2
          </SelectButton>
          <SelectButton
            onClick={() => onSelectHeadcount(1)}
            highlighted={headcount === 1}
            highlightColor={colors.lightPinkAccent}
          >
            👤 Solo
          </SelectButton>
        </RowButtons>
      </Row>
      <Row>
        <RowTitle>When:</RowTitle>
        <RowButtons>
          <SelectButton onClick={onSelectStartTime} highlightColor={colors.lightPurpleAccent} highlighted>
            🕑 {startTime}
          </SelectButton>
        </RowButtons>
      </Row>
      <Row>
        <RowTitle>Where:</RowTitle>
        <RowButtons>
          <SelectButton onClick={onSelectSearchArea} highlightColor={colors.lightOrangeAccent} highlighted>
            📍 {searchArea}
          </SelectButton>
        </RowButtons>
      </Row>
      <Row>
        <RowTitle>Price:</RowTitle>
        <RowButtons>
          <SelectButton
            onClick={() => onSelectBudget(OutingBudget.Inexpensive)}
            highlighted={budget === OutingBudget.Inexpensive}
            highlightColor={colors.mediumPurpleAccent}
          >
            $
          </SelectButton>
          <SelectButton
            onClick={() => onSelectBudget(OutingBudget.Moderate)}
            highlighted={budget === OutingBudget.Moderate}
            highlightColor={colors.mediumPurpleAccent}
          >
            $$
          </SelectButton>
          <SelectButton
            onClick={() => onSelectBudget(OutingBudget.Expensive)}
            highlighted={budget === OutingBudget.Expensive}
            highlightColor={colors.mediumPurpleAccent}
          >
            $$$
          </SelectButton>
          <SelectButton
            onClick={() => onSelectBudget(OutingBudget.VeryExpensive)}
            highlighted={budget === OutingBudget.VeryExpensive}
            highlightColor={colors.mediumPurpleAccent}
          >
            $$$$
          </SelectButton>
        </RowButtons>
      </Row>
      <SubmitButton onClick={onSubmit} loading={false} fullWidth>
        {cta}
      </SubmitButton>
    </>
  );
};

export default DateSelections;
