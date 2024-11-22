import { createSlice } from '@reduxjs/toolkit'


interface AuthState {
  isLoggedIn: boolean | null;
}

const initialState: AuthState = {
  isLoggedIn: null,
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
