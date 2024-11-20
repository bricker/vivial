import { createSlice } from '@reduxjs/toolkit'
import { authenticateUser } from './thunks';
export const AUTH = "auth";

// TODO: status enum

interface AuthState {
  isLoggedIn: boolean | null;
  status: 'idle' | 'pending' | 'succeeded' | 'failed';
  error: string | null
}

const initialState: AuthState = {
  status: 'idle',
  isLoggedIn: null,
  error: null,
}

export const authSlice = createSlice({
  name: AUTH,
  initialState,
  reducers: {
    // loggedIn: (state, action) => {
    //   state.isLoggedIn = true;
    // },
    // loggedOut: (state, action) => {
    //   state.isLoggedIn = false;
    // },
  },
  extraReducers: builder => {
    builder
      .addCase(authenticateUser.pending, (state, action) => {
        state.status = 'pending'
      })
      .addCase(authenticateUser.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.isLoggedIn = true;
      })
      .addCase(authenticateUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Unknown Error';
        state.isLoggedIn = null;
      })
  }
})

// export const { loggedIn, loggedOut } = authSlice.actions

export default authSlice.reducer;