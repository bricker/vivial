import { useDispatch, useSelector } from "react-redux";
import { usePlanOutingMutation } from "../store/slices/coreApiSlice";
import { getPreferenceInputs } from "../util/preferences";
import { useCallback, useEffect, useState } from "react";
import { AppRoute, routePath, type NavigationState } from "../routes";
import { useNavigate } from "react-router-dom";
import type { RootState } from "../store";
import { plannedOuting } from "../store/slices/outingSlice";
import { OutingBudget, type ItineraryFieldsFragment, type PlanOutingMutation } from "../graphql/generated/graphql";

export function useReroll({ outing }: { outing?: ItineraryFieldsFragment | null }): [() => Promise<void>, { isSuccess?: boolean, isLoading: boolean }] {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userPreferences = useSelector((state: RootState) => state.outing.preferences.user);
  const partnerPreferences = useSelector((state: RootState) => state.outing.preferences.partner);

  const [planOuting, { data: planOutingData, isLoading: planOutingIsLoading }] = usePlanOutingMutation();

  const [isSuccess, setIsSuccess] = useState<boolean | undefined>(undefined);

  const performReroll = useCallback(async () => {
    if (outing) {
      const groupPreferences = getPreferenceInputs(userPreferences, partnerPreferences);
      await planOuting({
        input: {
          startTime: new Date(outing.survey?.startTime || outing.startTime).toISOString(),
          searchAreaIds: (outing.survey?.searchRegions || outing.searchRegions).map((r) => r.id),
          budget: outing.survey?.budget || OutingBudget.Expensive,
          headcount: outing.survey?.headcount || outing.headcount,
          groupPreferences,
          isReroll: true,
        },
      });
    }
  }, [userPreferences, partnerPreferences, outing]);

  useEffect(() => {
    if (planOutingData) {
      switch (planOutingData.planOuting?.__typename) {
        case "PlanOutingSuccess": {
          setIsSuccess(true);
          const newOuting = planOutingData.planOuting.outing;
          dispatch(plannedOuting({ outing: newOuting }));
          break;
        }
        default: {
          setIsSuccess(false);
          break;
        }
      }
    }
  }, [planOutingData]);

  return [
    performReroll,
    { isSuccess, isLoading: planOutingIsLoading }
  ];
}
