import { AppContext } from "$eave-dashboard/js/context/Provider";
import { DashboardTeam, GetTeamResponseBody, GetVirtualEventsResponseBody, VirtualEventQueryInput } from "$eave-dashboard/js/types";
import {
  isHTTPError,
  isUnauthorized,
  logUserOut,
} from "$eave-dashboard/js/util/http-util";
import { useContext } from "react";

export interface TeamHook {
  team: DashboardTeam | null;
  getTeam: () => void;
  getTeamVirtualEvents: (input: VirtualEventQueryInput | null) => void;
}

const useTeam = (): TeamHook => {
  const { teamCtx, dashboardNetworkStateCtx, glossaryNetworkStateCtx } =
    useContext(AppContext);
  const [team, setTeam] = teamCtx!;
  const [, setDashboardNetworkState] = dashboardNetworkStateCtx!;
  const [, setGlossaryNetworkState] = glossaryNetworkStateCtx!;

  /**
   * Asynchronously fetches team data from the "/api/team" endpoint using a POST request.
   * If the response is unauthorized, it logs the user out.
   * If there is an HTTP error, it throws the response.
   * On successful fetch, it updates the team state with the received data, including team ID, name, and integrations.
   * If the fetch fails, it updates the team state to indicate an error.
   * Regardless of success or failure, sets 'teamIsLoading' state to false upon completion.
   */
  function getTeam() {
    setDashboardNetworkState((prev) => ({
      ...prev,
      teamIsLoading: true,
      teamIsErroring: false,
    }));
    fetch("/api/team", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: GetTeamResponseBody) => {
          setTeam((prev) => ({
            ...prev,
            id: data.team?.id,
            name: data.team?.name,
          }));

          setDashboardNetworkState((prev) => ({
            ...prev,
            teamIsLoading: false,
            teamRequestHasSucceededAtLeastOnce: true, // continue to show the table even if a subsequent request failed.
          }));
        });
      })
      .catch(() => {
        setDashboardNetworkState((prev) => ({
          ...prev,
          teamIsLoading: false,
          teamIsErroring: true,
        }));
      });
  }

  /**
   * Asynchronously fetches the team's list of virtual events for the glossary
   * from the core API.
   * Handles all network state for EventGlossary.jsx and sets the resulting
   * virtual events into the team hook.
   * The `input` parameter is passed along for event filtering on the backend.
   * If null is provided, no filtering is expected to be done.
   */
  function getTeamVirtualEvents(input: VirtualEventQueryInput | null) {
    setGlossaryNetworkState((prev) => ({
      ...prev,
      virtualEventsAreLoading: true,
      virtualEventsAreErroring: false,
    }));
    fetch("/api/team/virtual-events", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: input }),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }

        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: GetVirtualEventsResponseBody) => {
          setTeam((prev) => ({
            ...prev,
            virtualEvents: data.virtual_events,
          }));

          setGlossaryNetworkState((prev) => ({
            ...prev,
            virtualEventsAreErroring: false,
            virtualEventsAreLoading: false,
          }));
        });
      })
      .catch(() => {
        setGlossaryNetworkState((prev) => ({
          ...prev,
          virtualEventsAreErroring: true,
          virtualEventsAreLoading: false,
        }));
      });
  }

  return {
    team,
    getTeam,
    getTeamVirtualEvents,
  };
};

export default useTeam;
