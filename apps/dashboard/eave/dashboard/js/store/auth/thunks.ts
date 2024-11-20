import { createAsyncThunk } from '@reduxjs/toolkit'
import { AUTH } from './slice'

export const authenticateUser = createAsyncThunk(
  `${AUTH}/authenticateUser`,
  async ({ email, password }: {email: string, password: string}) => {
    // const item = await someHttpRequest(itemId)
    console.log(email);
    console.log(password);
    return { loggedInUserId: "xxxx" }
  }
);
