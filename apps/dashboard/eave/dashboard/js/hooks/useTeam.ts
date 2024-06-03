import { AppContext } from "$eave-dashboard/js/context/Provider";
import {
  DashboardTeam,
  GetMyVirtualEventDetailsResponseBody,
  GetTeamResponseBody,
  ListMyVirtualEventsResponseBody,
  eaveWindow,
} from "$eave-dashboard/js/types";
import { isHTTPError, isUnauthorized, logUserOut } from "$eave-dashboard/js/util/http-util";
import { useContext } from "react";

export interface TeamHook {
  team: DashboardTeam | null;
  getTeam: () => void;
  listVirtualEvents: (query: string | null) => void;
  getVirtualEventDetails: (id: string) => void;
}

const useTeam = (): TeamHook => {
  const { teamCtx, dashboardNetworkStateCtx, glossaryNetworkStateCtx } = useContext(AppContext);
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
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/team/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": "eave_dashboard",
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
  function listVirtualEvents(query: string | null) {
    setGlossaryNetworkState((prev) => ({
      ...prev,
      virtualEventsAreLoading: true,
      virtualEventsAreErroring: false,
    }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/virtual-events/list`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": "eave_dashboard",
      },
      body: JSON.stringify({ query }),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }

        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: ListMyVirtualEventsResponseBody) => {
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

  function getVirtualEventDetails(id: string | null) {
    // setGlossaryNetworkState((prev) => ({
    //   ...prev,
    //   virtualEventsAreLoading: true,
    //   virtualEventsAreErroring: false,
    // }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/virtual-events/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": "eave_dashboard",
      },
      body: JSON.stringify({ id }),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }

        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: GetMyVirtualEventDetailsResponseBody) => {
          setTeam((prev) => ({
            ...prev,
            virtualEvents: data.virtual_events,
          }));

          // setGlossaryNetworkState((prev) => ({
          //   ...prev,
          //   virtualEventsAreErroring: false,
          //   virtualEventsAreLoading: false,
          // }));
        });
      })
      .catch(() => {
        // setGlossaryNetworkState((prev) => ({
        //   ...prev,
        //   virtualEventsAreErroring: true,
        //   virtualEventsAreLoading: false,
        // }));
      });
  }

  return {
    team,
    getTeam,
    listVirtualEvents,
    getVirtualEventDetails,
  };
};

export default useTeam;
