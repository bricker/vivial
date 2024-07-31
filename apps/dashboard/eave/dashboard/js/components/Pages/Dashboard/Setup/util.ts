import { DashboardTeam } from "$eave-dashboard/js/types";

export function isSetupComplete(team?: DashboardTeam | null): boolean {
  return !!team?.clientCredentials?.last_used;
}
