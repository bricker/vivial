import { colors } from "$eave-dashboard/js/theme/colors";

import {
  ARTS_GROUP_ID,
  FITNESS_GROUP_ID,
  FOOD_GROUP_ID,
  HOBBIES_GROUP_ID,
  MEDIA_GROUP_ID,
  MUSIC_GROUP_ID,
  SEASONAL_GROUP_ID,
} from "$eave-dashboard/js/util/category/constant";

export const CATEGORY_ACCENT_COLOR_MAP: { [key: string]: string } = {
  [SEASONAL_GROUP_ID]: colors.mediumPurpleAccent,
  [FOOD_GROUP_ID]: colors.lightOrangeAccent,
  [MEDIA_GROUP_ID]: colors.mediumPurpleAccent,
  [MUSIC_GROUP_ID]: colors.lightPurpleAccent,
  [ARTS_GROUP_ID]: colors.lightPinkAccent,
  [HOBBIES_GROUP_ID]: colors.lightPurpleAccent,
  [FITNESS_GROUP_ID]: colors.lightPinkAccent,
};
