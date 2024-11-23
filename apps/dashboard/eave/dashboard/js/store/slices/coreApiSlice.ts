import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import {
  CreateAccountDocument,
  SearchRegionsDocument,
  type CreateAccountInput,
  type CreateAccountMutation,
  type SearchRegionsQuery,
} from "$eave-dashboard/js/graphql/generated/graphql";

const gqlParams = {
  url: "/graphql",
  method: "POST",
};
export const coreApiSlice = createApi({
  reducerPath: "coreApi",
  baseQuery: fetchBaseQuery({
    baseUrl: CORE_API_BASE,
  }),

  endpoints: (builder) => ({
    /**
     * Core API Queries
     */
    getSearchRegions: builder.query<SearchRegionsQuery, void>({
      query: () => ({ ...gqlParams, body: { query: SearchRegionsDocument } }),
    }),
    /**
     * Core API Mutations
     */
    createAccount: builder.mutation<{ data: CreateAccountMutation }, CreateAccountInput>({
      query: (input) => ({
        ...gqlParams,
        body: {
          query: CreateAccountDocument,
          variables: { input },
        },
      }),
    }),
  }),
});

export const {
  // Core API Query Hooks
  useGetSearchRegionsQuery,

  // Core API Mutation Hooks
  useCreateAccountMutation,
} = coreApiSlice;
