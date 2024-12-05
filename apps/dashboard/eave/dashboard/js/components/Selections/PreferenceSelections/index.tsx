import React, { useState, useCallback } from "react";
import { styled } from "@mui/material";
import { type Category } from "$eave-dashboard/js/types/category";

import Typography from "@mui/material/Typography";
import PrimaryButton from "../../Buttons/PrimaryButton";
import DropdownButton from "../../Buttons/DropdownButton";
import PillButton from "../../Buttons/PillButton";
import Paper from "../../Paper";

import { getCategoryMap, getAccentColor } from "./helpers";

const CategoryRow = styled(Paper)(() => ({
  marginTop: 16,
}));

const SubmitButton = styled(PrimaryButton)(() => ({
  minWidth: 76,
}));

const SubmitButtonContainer = styled("div")(() => ({
  marginTop: 16,
  display: "flex",
  justifyContent: "flex-end",
}));

interface PreferenceSelectionsProps {
  categoryGroupName: string;
  categories: Category[] | [];
  defaultCategories: Category[] | [];
  onSubmit: (selectedCategories: Category[]) => void;
  categoryGroupId?: string;
  collapsable?: boolean;
  collapsed?: boolean;
  cta?: string;
}

const PreferenceSelections = ({
  categoryGroupName,
  categoryGroupId,
  categories,
  defaultCategories,
  onSubmit,
  collapsable = false,
  collapsed = false,
  cta = "Save",
}: PreferenceSelectionsProps) => {
  const [selectedCategories, setSelectedCategories] = useState(defaultCategories);
  const [selectedCategoryMap, setSelectedCategoryMap] = useState(getCategoryMap(defaultCategories));
  const accentColor = getAccentColor(categoryGroupId);

  const handleSubmit = useCallback(() => {
    onSubmit(selectedCategories);
  }, [selectedCategories]);

  const handleSelect = useCallback((category: Category) => {
    const mapClone = { ...selectedCategoryMap }
    if (category.id in mapClone) {
      delete mapClone[category.id];
      setSelectedCategories(selectedCategories.filter(c => c.id !== category.id))
    } else {
      mapClone[category.id] = category.name;
      setSelectedCategories([...selectedCategories, category]);
    }
    setSelectedCategoryMap(mapClone);
  }, [selectedCategories, selectedCategoryMap]);

  const toggleSelectAll = useCallback(() => {
    if (selectedCategories.length === categories.length) {
      setSelectedCategories([]);
      setSelectedCategoryMap({});
    } else {
      setSelectedCategories(categories);
      setSelectedCategoryMap(getCategoryMap(categories));
    }
  }, [selectedCategories]);

  return (
    <CategoryRow>
      {collapsable && (
        <DropdownButton open={collapsed} />
      )}
      <Typography>{categoryGroupName}</Typography>
      <PillButton onClick={toggleSelectAll} selected={selectedCategories.length === categories.length} accentColor={accentColor} outlined>
        All
      </PillButton>
      {categories.map((category) => (
        <PillButton onClick={() => handleSelect(category)} key={category.name} selected={category.id in selectedCategoryMap}  accentColor={accentColor}>
          {category.name}
        </PillButton>
      ))}
      <SubmitButtonContainer>
        <SubmitButton onClick={handleSubmit}>
          {cta}
        </SubmitButton>
      </SubmitButtonContainer>
    </CategoryRow>
  );
}

export default PreferenceSelections;
