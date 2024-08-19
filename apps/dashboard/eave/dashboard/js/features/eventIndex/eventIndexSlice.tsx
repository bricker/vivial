// src/features/dataSlice.ts
import { PayloadAction, createAsyncThunk, createSlice } from "@reduxjs/toolkit";

interface EventIndexState {
  items: any[];
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
}

const initialState: EventIndexState = {
  items: [],
  status: "idle",
  error: null,
};

// Example async thunk for fetching data
export const fetchData = createAsyncThunk("data/fetchData", async () => {
  const response = await fetch("https://api.example.com/data");
  return response.json();
});

const dataSlice = createSlice({
  name: "data",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchData.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchData.fulfilled, (state, action: PayloadAction<any[]>) => {
        state.status = "succeeded";
        state.items = action.payload;
      })
      .addCase(fetchData.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const selectAllData = (state: EventIndexState) => state.items;
export default dataSlice.reducer;
