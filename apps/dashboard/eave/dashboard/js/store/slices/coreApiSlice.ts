import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { GRAPHQL_API_BASE } from '$eave-dashboard/js/util/http';

import { SearchRegionsDocument } from "$eave-dashboard/js/graphql/generated"

type SearchRegion = {
  id: string;
  name: string;
}

type SearchRegionQueryResponse = {
  data: {
    searchRegions: SearchRegion[];
  }
}

export const coreApiSlice = createApi({
  reducerPath: 'coreApi',
  baseQuery: fetchBaseQuery({ baseUrl: GRAPHQL_API_BASE }),
  endpoints: (builder) => ({
    getSearchRegions: builder.query<SearchRegionQueryResponse, void>({
      query: () => ({
        document: SearchRegionsDocument,
        variables: {},
      }),
      // query: () => "/posts"
    }),
  }),

  // endpoints: builder => ({
    // getSearchRegions: builder.query<SearchRegionQueryResponse, void>({
    //   query: () => ({
    //     document: SearchRegionsDocument,
    //     // variables: {},
    // })
  // })
});

export const { useGetSearchRegionsQuery } = coreApiSlice
