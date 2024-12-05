import React, { useState, useCallback } from "react";
import { styled } from "@mui/material";
import {
  type ActivityCategory,
  type RestaurantCategory,
} from "$eave-dashboard/js/graphql/generated/graphql"

import Typography from "@mui/material/Typography";
import DropdownButton from "../../Buttons/DropdownButton";
import PillButton from "../../Buttons/PillButton";
import Paper from "../../Paper";

import { getCategoryMap } from "./helpers";

/**
 * SHARED STYLES
 */
const CategoryRow = styled(Paper)(() => ({
  marginTop: 16,
}));

/**
 * SHARED INTERFACES
 */
interface PreferenceSelectionsProps {
  categoryGroupName: string;
  accentColor: string;
  collapsable?: boolean;
  collapsed?: boolean;
  cta?: string;
}

interface RestaurantPreferenceSelectionsProps extends PreferenceSelectionsProps {
  categories: RestaurantCategory[] | [];
  defaultCategories: RestaurantCategory[] | [];
  onSubmit: (selectedCategories: RestaurantCategory[]) => void;
}

/**
 * SHARED COMPONENTS
 */
const RestaurantPreferenceSelections = ({
  categories,
  defaultCategories,
  onSubmit,
  categoryGroupName,
  accentColor,
  collapsable = false,
  collapsed = false,
  cta = "Save",
}: RestaurantPreferenceSelectionsProps) => {
  const [selectedCategories, setSelectedCategories] = useState(defaultCategories);
  const [selectedCategoryMap, setSelectedCategoryMap] = useState(getCategoryMap(defaultCategories));

  const handleSubmit = useCallback(() => {
    onSubmit(selectedCategories);
  }, [selectedCategories]);

  const handleSelect = useCallback((category: RestaurantCategory) => {
    if (category.id in selectedCategoryMap) {
      const newMap = {...selectedCategoryMap}
      delete newMap[category.id];
      setSelectedCategoryMap(newMap);
      setSelectedCategories(selectedCategories.filter(c => c.id !== category.id))
    } else {
      const newMap = {...selectedCategoryMap}
      newMap[category.id] = category.name;
      setSelectedCategoryMap(newMap);
      setSelectedCategories([...selectedCategories, category]);
    }
  }, [selectedCategories, selectedCategoryMap]);

  const toggleSelectAll = useCallback(() => {

  }, []);

  return (
    <CategoryRow>
      {collapsable && (
        <DropdownButton open={collapsed} />
      )}
      <Typography>{categoryGroupName}</Typography>
      <PillButton onClick={toggleSelectAll} selected={false} accentColor={accentColor} outlined>
        All
      </PillButton>
      {categories.map((category) => (
        <PillButton onClick={() => handleSelect(category)} key={category.name} selected={category.id in selectedCategoryMap}  accentColor={accentColor}>
          {category.name}
        </PillButton>
      ))}
      <button onClick={handleSubmit}>
        {cta}
      </button>
    </CategoryRow>
  );
}

const ActivityPreferenceSelections = () => {
  return (
    null
  )
}

export { RestaurantPreferenceSelections, ActivityPreferenceSelections };
