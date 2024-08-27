import { RootState } from "$eave-dashboard/js/store";
import { VirtualEventDetails, eaveOrigin, eaveWindow } from "$eave-dashboard/js/types";
import { logUserOut } from "$eave-dashboard/js/util/http-util";
import { PayloadAction, createAsyncThunk, createSlice } from "@reduxjs/toolkit";

interface EventIndexState {
  virtualEvents: VirtualEventDetails[];
  selectedEvent: VirtualEventDetails | null;
  isOpen: boolean;
  searchValue: string;
  usingMobileLayout: boolean;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: EventIndexState = {
  virtualEvents: [],
  selectedEvent: null,
  isOpen: false,
  searchValue: "",
  usingMobileLayout: false,
  status: "idle",
  error: null,
};

export const listVirtualEvents = createAsyncThunk<
  VirtualEventDetails[],
  { query?: string | null },
  { rejectValue: string }
>("eventIndex/listVirtualEvents", async ({ query } = {}, { rejectWithValue }) => {
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
    return data.virtual_events as VirtualEventDetails[];
  } catch (error) {
    console.error(error);
    return rejectWithValue("Failed to fetch virtual events");
  }
});

export const getVirtualEventDetails = createAsyncThunk<VirtualEventDetails, string | null, { rejectValue: string }>(
  "eventIndex/getVirtualEventDetails",
  async (id, { rejectWithValue, getState }) => {
    const state = getState() as RootState;
    const existingVirtualEvent = state.eventIndex.virtualEvents.find((ve) => ve.id === id);

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

const eventIndexSlice = createSlice({
  name: "eventIndex",
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
    setSearchValue(state, action: PayloadAction<string>) {
      state.searchValue = action.payload;
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
        state.virtualEvents = newVirtualEvents;
        // Fake Data:
        //state.virtualEvents = fakeVirtualEvents;
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

export const { selectEvent, closePanel, setUsingMobileLayout, setSearchValue } = eventIndexSlice.actions;

export const selectEventIndex = (state: RootState) => state.eventIndex;

export default eventIndexSlice.reducer;
