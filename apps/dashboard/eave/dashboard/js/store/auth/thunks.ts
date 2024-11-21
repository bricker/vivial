import { createAsyncThunk } from '@reduxjs/toolkit'

export const authenticateUser = createAsyncThunk(
  'auth/authenticateUser',
  async ({ email, password }: {email: string, password: string}) => {
    // const item = await someHttpRequest(itemId)
    console.log(email);
    console.log(password);
    return { loggedInUserId: "xxxx" }
  }
);
