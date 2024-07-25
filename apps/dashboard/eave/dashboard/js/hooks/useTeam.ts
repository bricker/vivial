import { AppContext } from "$eave-dashboard/js/context/Provider";
import {
  CreateMyOnboardingSubmissionRequestBody,
  CreateMyOnboardingSubmissionResponseBody,
  DashboardTeam,
  GetMyClientCredentialsResponseBody,
  GetMyOnboardingSubmissionResponseBody,
  GetMyVirtualEventDetailsResponseBody,
  GetTeamResponseBody,
  ListMyVirtualEventsResponseBody,
  VirtualEventDetails,
  eaveOrigin,
  eaveWindow,
} from "$eave-dashboard/js/types";
import { isHTTPError, isUnauthorized, logUserOut } from "$eave-dashboard/js/util/http-util";
import { useContext } from "react";

export interface TeamHook {
  team: DashboardTeam | null;
  getTeam: () => void;
  listVirtualEvents: (args?: { query?: string | null }) => void;
  getVirtualEventDetails: (id: string) => void;
  getOnboardingFormSubmission: () => void;
  createOnboardingFormSubmission: (requestBody: CreateMyOnboardingSubmissionRequestBody) => void;
  getClientCredentials: () => void;
}

const useTeam = (): TeamHook => {
  const {
    teamCtx,
    dashboardNetworkStateCtx,
    glossaryNetworkStateCtx,
    onboardingFormNetworkStateCtx,
    clientCredentialsNetworkStateCtx,
  } = useContext(AppContext);
  const [team, setTeam] = teamCtx!;
  const [, setDashboardNetworkState] = dashboardNetworkStateCtx!;
  const [, setGlossaryNetworkState] = glossaryNetworkStateCtx!;
  const [, setOnboardingFormNetworkState] = onboardingFormNetworkStateCtx!;
  const [, setClientCredentialsNetworkState] = clientCredentialsNetworkStateCtx!;

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
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
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
      .catch((e) => {
        console.error(e);
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
  function listVirtualEvents({ query }: { query?: string | null } = {}) {
    setGlossaryNetworkState((prev) => ({
      ...prev,
      virtualEventsAreLoading: true,
      virtualEventsAreErroring: false,
    }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/virtual-events/list`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
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
          setTeam((prev) => {
            const prevVirtualEvents = prev?.virtualEvents;
            if (!prevVirtualEvents) {
              return {
                ...prev,
                virtualEvents: data.virtual_events,
              };
            }

            const newVirtualEvents: VirtualEventDetails[] = [];

            for (const incoming of data.virtual_events) {
              const existing = prevVirtualEvents.find((current) => current.id === incoming.id);
              // If the virtual event hasn't been loaded, append it to the list.
              // Otherwise, leave it without overwriting, because it might have fields already populated.
              if (existing) {
                newVirtualEvents.push(existing);
              } else {
                newVirtualEvents.push(incoming);
              }
            }

            return {
              ...prev,
              virtualEvents: newVirtualEvents,
            };
          });

          setGlossaryNetworkState((prev) => ({
            ...prev,
            virtualEventsAreErroring: false,
            virtualEventsAreLoading: false,
          }));
        });
      })
      .catch((e) => {
        console.error(e);
        setGlossaryNetworkState((prev) => ({
          ...prev,
          virtualEventsAreErroring: true,
          virtualEventsAreLoading: false,
        }));
      });
  }

  function getVirtualEventDetails(id: string | null) {
    const existingVirtualEvent = team?.virtualEvents?.find((ve) => ve.id === id);
    if (existingVirtualEvent && existingVirtualEvent.fields) {
      // The virtual event already has its fields loaded.
      return;
    }

    setGlossaryNetworkState((prev) => ({
      ...prev,
      virtualEventsAreLoading: true,
      virtualEventsAreErroring: false,
    }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/virtual-events/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
      body: JSON.stringify({ virtual_event: { id } }),
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
          // update the virt event list data entry with the fetched details
          setTeam((prev) => {
            const virtualEvents = prev?.virtualEvents;
            if (!virtualEvents) {
              // No virtual events were previously loaded. Set the array to the virtual event from the response.
              return {
                ...prev,
                virtualEvents: [data.virtual_event],
              };
            }

            const idx = virtualEvents.findIndex((ve) => ve.id === id);
            if (idx > -1) {
              // update the virtual event with the extra data from the response.
              virtualEvents[idx] = data.virtual_event;
            } else {
              // The virtual event was not in the list. Append it to the list.
              virtualEvents.push(data.virtual_event);
            }

            return {
              ...prev,
              virtualEvents,
            };
          });

          setGlossaryNetworkState((prev) => ({
            ...prev,
            virtualEventsAreErroring: false,
            virtualEventsAreLoading: false,
          }));
        });
      })
      .catch((e) => {
        console.error(e);
        setGlossaryNetworkState((prev) => ({
          ...prev,
          virtualEventsAreErroring: true,
          virtualEventsAreLoading: false,
        }));
      });
  }

  function getOnboardingFormSubmission() {
    setOnboardingFormNetworkState((prev) => ({
      ...prev,
      formDataIsLoading: true,
      formDataIsErroring: false,
    }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/onboarding-submissions/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: GetMyOnboardingSubmissionResponseBody) => {
          setTeam((prev) => {
            return {
              ...prev,
              dashboard_access: data.team.dashboard_access,
              onboardingSubmission: data.onboarding_submission,
            };
          });

          setOnboardingFormNetworkState((prev) => ({
            ...prev,
            formDataIsErroring: false,
            formDataIsLoading: false,
          }));
        });
      })
      .catch((e) => {
        console.error(e);
        setOnboardingFormNetworkState((prev) => ({
          ...prev,
          formDataIsErroring: true,
          formDataIsLoading: false,
        }));
      });
  }

  function createOnboardingFormSubmission(requestBody: CreateMyOnboardingSubmissionRequestBody) {
    setOnboardingFormNetworkState((prev) => ({
      ...prev,
      formSubmitIsLoading: true,
      formSubmitIsErroring: false,
    }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/onboarding-submissions/create`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
      body: JSON.stringify(requestBody),
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: CreateMyOnboardingSubmissionResponseBody) => {
          // set dashboard access based on form submission answers
          setTeam((prev) => {
            return {
              ...prev,
              dashboard_access: data.team.dashboard_access,
              onboardingSubmission: data.onboarding_submission,
            };
          });

          setOnboardingFormNetworkState((prev) => ({
            ...prev,
            formSubmitIsErroring: false,
            formSubmitIsLoading: false,
          }));
        });
      })
      .catch((e) => {
        console.error(e);
        setOnboardingFormNetworkState((prev) => ({
          ...prev,
          formSubmitIsErroring: true,
          formSubmitIsLoading: false,
        }));
      });
  }

  function getClientCredentials() {
    setClientCredentialsNetworkState((prev) => ({
      ...prev,
      credentialsAreLoading: true,
      credentialsAreErroring: false,
    }));
    fetch(`${eaveWindow.eavedash.apiBase}/public/me/client-credentials/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
    })
      .then((resp) => {
        if (isUnauthorized(resp)) {
          logUserOut();
          return;
        }
        if (isHTTPError(resp)) {
          throw resp;
        }
        return resp.json().then((data: GetMyClientCredentialsResponseBody) => {
          // set dashboard access based on form submission answers
          setTeam((prev) => {
            return {
              ...prev,
              clientCredentials: data.credentials,
            };
          });

          setClientCredentialsNetworkState((prev) => ({
            ...prev,
            credentialsAreErroring: false,
            credentialsAreLoading: false,
          }));
        });
      })
      .catch((e) => {
        console.error(e);
        setClientCredentialsNetworkState((prev) => ({
          ...prev,
          credentialsAreErroring: true,
          credentialsAreLoading: false,
        }));
      });
  }

  return {
    team,
    getTeam,
    listVirtualEvents,
    getVirtualEventDetails,
    getOnboardingFormSubmission,
    createOnboardingFormSubmission,
    getClientCredentials,
  };
};

export default useTeam;
