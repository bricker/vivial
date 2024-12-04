import React, { useState, useCallback } from "react";
import { styled } from "@mui/material";
import {
  type ActivityCategory,
  type RestaurantCategory
} from "$eave-dashboard/js/graphql/generated/graphql"

import Typography from "@mui/material/Typography";
import DropdownButton from "../../Buttons/DropdownButton";
import PillButton from "../../Buttons/PillButton";
import Paper from "../../Paper";

import { getSelectedCategoryIds, getCategoryMap } from "./helpers";

interface CategorySelectionProps {
  categoryGroupName: string;
  accentColor: string;
  collapsable?: boolean;
  collapsed?: boolean;
  cta?: string;
}

interface RestaurantCategorySelectionsProps extends CategorySelectionProps {
  allCategories: RestaurantCategory[];
  selectedCategories: RestaurantCategory[];
  onSubmit: (selectedCategories: RestaurantCategory[]) => void;
}

interface ActivityCategorySelectionsProps extends CategorySelectionProps {
  allCategories: ActivityCategory[];
  selectedCategories: ActivityCategory[];
  onSubmit: (selectedCategories: ActivityCategory[]) => void;
}

const Row = styled(Paper)(() => ({
  marginTop: 16,
}));

const RestaurantCategorySelections = (props: RestaurantCategorySelectionsProps) => {
  const [selectedCategoryIds, setSelectedCategoryIds] = useState(
    getSelectedCategoryIds(allCategories, selectedCategories)
  );
  const selectedCategoryMap = getCategoryMap(selectedCategories);
  return (
    <Row>
      {collapsable && (
        <DropdownButton open={collapsed} />
      )}
      <Typography>{categoryGroupName}</Typography>
      <PillButton onClick={() => {}} selected={false} accentColor={accentColor} outlined>
        All
      </PillButton>
      {allCategories.map((category) => (
        <PillButton onClick={() => {}} key={category.name} selected={category.id in selectedCategoryMap}  accentColor={accentColor}>
          {category.name}
        </PillButton>
      ))}
    </Row>
  );
}

const ActivityCategorySelections = () => {
  return null;
}

export { RestaurantCategorySelections, ActivityCategorySelections }
