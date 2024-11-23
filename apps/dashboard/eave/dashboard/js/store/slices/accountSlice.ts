import { createSlice } from '@reduxjs/toolkit'

interface AccountState {
  id: string | null;
  email: string | null;
}

const initialState: AccountState = {
  id: null,
  email: null,
}

export const authSlice = createSlice({
  name: "account",
  initialState,
  reducers: {
    updateAccount: (state, { payload }) => {
      state.id = payload.id;
      state.email = payload.email;
    },
  },
})

export const { updateAccount } = authSlice.actions
