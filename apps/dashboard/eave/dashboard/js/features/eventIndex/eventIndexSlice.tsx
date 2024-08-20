import { RootState } from "$eave-dashboard/js/store";
import { VirtualEventDetails, eaveOrigin, eaveWindow } from "$eave-dashboard/js/types";
import { logUserOut } from "$eave-dashboard/js/util/http-util";
import { PayloadAction, createAsyncThunk, createSelector, createSlice } from "@reduxjs/toolkit";

interface GlossaryState {
  virtualEvents: VirtualEventDetails[];
  selectedEvent: VirtualEventDetails | null;
  isOpen: boolean;
  usingMobileLayout: boolean;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: GlossaryState = {
  virtualEvents: [],
  selectedEvent: null,
  isOpen: false,
  usingMobileLayout: false,
  status: "idle",
  error: null,
};

export const listVirtualEvents = createAsyncThunk<
  VirtualEventDetails[],
  { query?: string | null },
  { rejectValue: string }
>("glossary/listVirtualEvents", async ({ query } = {}, { rejectWithValue }) => {
  try {
    const response = await fetch(`${eaveWindow.eavedash.apiBase}/public/me/virtual-events/list`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "eave-origin": eaveOrigin,
      },
      credentials: "include",
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        logUserOut();
        return rejectWithValue("Unauthorized");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(data);
    return data.virtual_events as VirtualEventDetails[];
  } catch (error) {
    console.error(error);
    return rejectWithValue("Failed to fetch virtual events");
  }
});

export const getVirtualEventDetails = createAsyncThunk<VirtualEventDetails, string | null, { rejectValue: string }>(
  "glossary/getVirtualEventDetails",
  async (id, { rejectWithValue, getState }) => {
    const state = getState() as RootState;
    const existingVirtualEvent = state.glossary.virtualEvents.find((ve) => ve.id === id);

    if (existingVirtualEvent && existingVirtualEvent.fields) {
      // The virtual event already has its fields loaded, no need to fetch again.
      return existingVirtualEvent;
    }

    try {
      const response = await fetch(`${eaveWindow.eavedash.apiBase}/public/me/virtual-events/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "eave-origin": eaveOrigin,
        },
        credentials: "include",
        body: JSON.stringify({ virtual_event: { id } }),
      });

      if (response.status === 401) {
        logUserOut();
        return rejectWithValue("Unauthorized");
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.virtual_event as VirtualEventDetails;
    } catch (error) {
      console.error(error);
      return rejectWithValue("Failed to fetch virtual event details");
    }
  },
);

const glossarySlice = createSlice({
  name: "glossary",
  initialState,
  reducers: {
    selectEvent(state, action: PayloadAction<VirtualEventDetails>) {
      state.selectedEvent = action.payload;
      state.isOpen = true;
    },
    closePanel(state) {
      state.isOpen = false;
    },
    setUsingMobileLayout(state, action: PayloadAction<boolean>) {
      state.usingMobileLayout = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Handle listVirtualEvents cases
      .addCase(listVirtualEvents.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(listVirtualEvents.fulfilled, (state, action: PayloadAction<VirtualEventDetails[]>) => {
        const newVirtualEvents: VirtualEventDetails[] = [];
        console.log(action.payload);
        for (const incoming of action.payload) {
          const existing = state.virtualEvents.find((current) => current.id === incoming.id);
          if (existing) {
            newVirtualEvents.push(existing);
          } else {
            newVirtualEvents.push(incoming);
          }
        }
        // state.virtualEvents = newVirtualEvents;
        // ! TESTING WITH FAKE DATA
        state.virtualEvents = fakeVirtualEvents;
        console.log(state.virtualEvents);
        state.status = "succeeded";
      })
      .addCase(listVirtualEvents.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })
      .addCase(getVirtualEventDetails.pending, (state) => {
        state.status = "loading";
      })
      .addCase(getVirtualEventDetails.fulfilled, (state, action: PayloadAction<VirtualEventDetails>) => {
        const idx = state.virtualEvents.findIndex((ve) => ve.id === action.payload.id);
        if (idx > -1) {
          // Update the virtual event with the extra data from the response.
          state.virtualEvents[idx] = action.payload;
        } else {
          // The virtual event was not in the list. Append it to the list.
          state.virtualEvents.push(action.payload);
        }
        state.status = "succeeded";
      })
      .addCase(getVirtualEventDetails.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      });
  },
});

export const { selectEvent, closePanel, setUsingMobileLayout } = glossarySlice.actions;

export const selectGlossary = (state: RootState) => state.glossary;

// Selector to get virtualEvents from glossary state
export const selectVirtualEvents = createSelector([selectGlossary], (glossary) => glossary.virtualEvents);

export default glossarySlice.reducer;

const fakeVirtualEvents: VirtualEventDetails[] = [
  {
    id: "event-123",
    view_id: "view-abc-123",
    readable_name: "Annual Tech Conference 2024",
    description: "A premier event showcasing the latest advancements in technology.",
    fields: [
      {
        name: "Agenda",
        description: "Detailed schedule of the conference.",
        field_type: "text",
        mode: "read-only",
        fields: [
          {
            name: "Day 1",
            description: "Opening ceremony and keynote speeches.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
          {
            name: "Day 2",
            description: "Workshops and breakout sessions.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
        ],
      },
      {
        name: "Speakers",
        description: "List of keynote speakers and panelists.",
        field_type: "list",
        mode: "editable",
        fields: [
          {
            name: "Keynote Speaker 1",
            description: "CEO of a leading tech company.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
          {
            name: "Panelist 1",
            description: "Expert in AI and machine learning.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
        ],
      },
    ],
  },
  {
    id: "event-456",
    view_id: "view-def-456",
    readable_name: "Global Sustainability Summit 2024",
    description: "An event focused on sustainable practices and innovations worldwide.",
    fields: [
      {
        name: "Sessions",
        description: "Topics covered during the summit.",
        field_type: "text",
        mode: "read-only",
        fields: [
          {
            name: "Climate Change Mitigation",
            description: "Strategies for reducing carbon emissions.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
          {
            name: "Renewable Energy",
            description: "Advancements in solar and wind technologies.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
        ],
      },
      {
        name: "Exhibitors",
        description: "Organizations showcasing their sustainable solutions.",
        field_type: "list",
        mode: "editable",
        fields: [
          {
            name: "Exhibitor 1",
            description: "Company specializing in electric vehicles.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
          {
            name: "Exhibitor 2",
            description: "Startup focused on biodegradable packaging.",
            field_type: "text",
            mode: "read-only",
            fields: null,
          },
        ],
      },
    ],
  },
];
