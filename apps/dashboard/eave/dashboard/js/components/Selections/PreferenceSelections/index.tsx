import { type Category } from "$eave-dashboard/js/types/category";
import { styled } from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";

import Typography from "@mui/material/Typography";
import DropdownButton from "../../Buttons/DropdownButton";
import PillButton from "../../Buttons/PillButton";
import PrimaryButton from "../../Buttons/PrimaryButton";
import Paper from "../../Paper";

import { getAccentColor, getCategoryMap } from "./helpers";

const RowContainer = styled(Paper)(() => ({
  position: "relative",
  display: "flex",
  flexDirection: "column",
  marginBottom: 16,
}));

const RowContentContainer = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  flex: 1,
}));

const Categories = styled("div")(() => ({
  marginTop: 16,
}));

const SubmitButton = styled(PrimaryButton)(() => ({
  minWidth: 76,
}));

const SubmitButtonContainer = styled("div")(() => ({
  marginTop: 7,
  display: "flex",
  justifyContent: "flex-end",
}));

const CollapseButton = styled(DropdownButton)(() => ({
  position: "absolute",
  right: 32,
  top: 18,
}));

interface PreferenceSelectionsProps {
  categoryGroupName: string;
  categories: Category[];
  defaultCategories: Category[];
  onSubmit: (selectedCategories: Category[], removedCategories?: Category[]) => void;
  onCollapse?: () => void;
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
  onCollapse,
  collapsable = false,
  collapsed = true,
  cta = "Save",
}: PreferenceSelectionsProps) => {
  const [selectedCategories, setSelectedCategories] = useState(defaultCategories);
  const [selectedCategoryMap, setSelectedCategoryMap] = useState(getCategoryMap(defaultCategories));
  const [removedCategories, setRemovedCategories] = useState<Category[]>([]);
  const [onCollapseEnabled, setOnCollapseEnabled] = useState(!!onCollapse);
  const [isCollapsed, setIsCollapsed] = useState(collapsed);
  const accentColor = getAccentColor(categoryGroupId);

  const handleSubmit = useCallback(() => {
    onSubmit(selectedCategories, removedCategories);
    setRemovedCategories([]);
    if (collapsable) {
      if (onCollapseEnabled && onCollapse) {
        onCollapse();
      } else {
        setIsCollapsed(false);
      }
    }
  }, [selectedCategories, removedCategories]);

  const handleForceCollapse = useCallback(() => {
    setIsCollapsed(!isCollapsed);
    setOnCollapseEnabled(false);
  }, [isCollapsed]);

  const handleSelect = useCallback(
    (category: Category) => {
      const mapClone = { ...selectedCategoryMap };
      if (category.id in mapClone) {
        delete mapClone[category.id];
        setRemovedCategories([...removedCategories, category]);
        setSelectedCategories(selectedCategories.filter((c) => c.id !== category.id));
      } else {
        mapClone[category.id] = category.name;
        setRemovedCategories(removedCategories.filter((c) => c.id !== category.id));
        setSelectedCategories([...selectedCategories, category]);
      }
      setSelectedCategoryMap(mapClone);
    },
    [selectedCategoryMap, removedCategories, selectedCategories],
  );

  const toggleSelectAll = useCallback(() => {
    if (selectedCategories.length === categories.length) {
      setSelectedCategories([]);
      setSelectedCategoryMap({});
    } else {
      setSelectedCategories(categories);
      setSelectedCategoryMap(getCategoryMap(categories));
    }
  }, [categories, selectedCategories]);

  useEffect(() => {
    setSelectedCategories(defaultCategories);
    setSelectedCategoryMap(getCategoryMap(defaultCategories));
  }, [defaultCategories]);

  useEffect(() => {
    setIsCollapsed(collapsed);
  }, [collapsed]);

  return (
    <RowContainer>
      {collapsable && <CollapseButton onClick={handleForceCollapse} open={isCollapsed} large />}
      <Typography variant="h5">{categoryGroupName}</Typography>
      {isCollapsed && (
        <RowContentContainer>
          <Categories>
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
          </Categories>
          <SubmitButtonContainer>
            <SubmitButton onClick={handleSubmit}>{cta}</SubmitButton>
          </SubmitButtonContainer>
        </RowContentContainer>
      )}
    </RowContainer>
  );
};

export default PreferenceSelections;
