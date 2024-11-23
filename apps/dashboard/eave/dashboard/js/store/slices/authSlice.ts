import { createSlice } from '@reduxjs/toolkit'

interface AuthState {
  isLoggedIn: boolean | null;
  accessToken: string | null;
  refreshToken: string | null;
}

const initialState: AuthState = {
  isLoggedIn: null,
  accessToken: null,
  refreshToken: null,
}

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logIn: (state, { payload }) => {
      state.isLoggedIn = true;
      state.accessToken = payload.accessToken;
      state.refreshToken = payload.refreshToken;
    },
    logOut: (state) => {
      state.isLoggedIn = false;
      state.accessToken = null;
      state.refreshToken = null;
    },
  },
})

export const { logIn, logOut } = authSlice.actions
