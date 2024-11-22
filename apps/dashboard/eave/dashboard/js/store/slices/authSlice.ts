import { createSlice } from '@reduxjs/toolkit'
import { authenticateUser } from './thunks';

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
  name: "auth",
  initialState,
  reducers: {
    loggedIn: (state, action) => {
      state.isLoggedIn = true;
    },
    loggedOut: (state, action) => {
      state.isLoggedIn = false;
    },
  },
})

export const { loggedIn, loggedOut } = authSlice.actions
