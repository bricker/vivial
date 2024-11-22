import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'


export const coreApiSlice = createApi({
  reducerPath: 'coreApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/fakeApi' }),
  endpoints: builder => ({
    getPosts: builder.query<string[], void>({
      query: () => '/posts'
    })
  })
});

export const { useGetPostsQuery } = coreApiSlice
