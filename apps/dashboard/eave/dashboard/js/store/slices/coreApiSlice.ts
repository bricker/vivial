import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { GRAPHQL_API_BASE } from '$eave-dashboard/js/util/http';


export const coreApiSlice = createApi({
  reducerPath: 'coreApi',
  baseQuery: fetchBaseQuery({ baseUrl: GRAPHQL_API_BASE }),
  endpoints: builder => ({
    getPosts: builder.query<string[], void>({
      query: () => '/posts'
    })
  })
});

export const { useGetPostsQuery } = coreApiSlice
