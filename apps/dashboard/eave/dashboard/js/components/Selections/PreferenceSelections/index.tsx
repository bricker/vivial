import { type Category } from "$eave-dashboard/js/types/category";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";

import Typography from "@mui/material/Typography";
import DropdownButton from "../../Buttons/DropdownButton";
import PillButton from "../../Buttons/PillButton";
import PrimaryButton from "../../Buttons/PrimaryButton";
import Paper from "../../Paper";

import { getAccentColor, getCategoryMap } from "./helpers";

const CategoryRow = styled(Paper)(() => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  marginTop: 16,
}));

const GroupName = styled(Typography)(() => ({
  marginBottom: 16,
}));

const SubmitButton = styled(PrimaryButton)(() => ({
  minWidth: 76,
}));

const SubmitButtonContainer = styled("div")(() => ({
  marginTop: 7,
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

  const handleSubmit = () => {
    onSubmit(selectedCategories);
  };

  const handleSelect = useCallback(
    (category: Category) => {
      const mapClone = { ...selectedCategoryMap };
      if (category.id in mapClone) {
        delete mapClone[category.id];
        setSelectedCategories(selectedCategories.filter((c) => c.id !== category.id));
      } else {
        mapClone[category.id] = category.name;
        setSelectedCategories([...selectedCategories, category]);
      }
      setSelectedCategoryMap(mapClone);
    },
    [selectedCategories, selectedCategoryMap],
  );

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
      {collapsable && <DropdownButton open={collapsed} />}
      <div>
        <GroupName variant="h5">{categoryGroupName}</GroupName>
        <PillButton
          onClick={toggleSelectAll}
          selected={selectedCategories.length === categories.length}
          accentColor={accentColor}
          outlined
        >
          All
        </PillButton>
        {categories.map((category) => (
          <PillButton
            onClick={() => handleSelect(category)}
            key={category.name}
            selected={category.id in selectedCategoryMap}
            accentColor={accentColor}
          >
            {category.name}
          </PillButton>
        ))}
      </div>
      <SubmitButtonContainer>
        <SubmitButton onClick={handleSubmit}>{cta}</SubmitButton>
      </SubmitButtonContainer>
    </CategoryRow>
  );
};

export default PreferenceSelections;
