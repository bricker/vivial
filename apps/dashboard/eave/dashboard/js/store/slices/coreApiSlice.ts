import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import {
  CreateAccountDocument,
  LoginDocument,
  SearchRegionsDocument,
  type CreateAccountMutation,
  type CreateAccountMutationVariables,
  type LoginMutation,
  type LoginMutationVariables,
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
     * Core API - REST Endpoints
     */
    logout: builder.mutation<void, void>({
      query: () => "/public/logout",
    }),
    /**
     * Core API - GraphQL Queries
     */
    getSearchRegions: builder.query<SearchRegionsQuery, void>({
      query: () => ({ ...gqlParams, body: { query: SearchRegionsDocument } }),
    }),
    /**
     * Core API - GraphQL Mutations
     */
    createAccount: builder.mutation<{ data: CreateAccountMutation }, CreateAccountMutationVariables>({
      query: (variables) => ({
        ...gqlParams,
        body: {
          query: CreateAccountDocument,
          variables,
        },
      }),
    }),
    login: builder.mutation<{ data: LoginMutation }, LoginMutationVariables>({
      query: (variables) => ({
        ...gqlParams,
        body: {
          query: LoginDocument,
          variables,
        },
      }),
    }),
  }),
});

export const {
  // Core API REST Hooks
  useLogoutMutation,

  // Core API GraphQL Query Hooks
  useGetSearchRegionsQuery,

  // Core API GraphQL Mutation Hooks
  useCreateAccountMutation,
  useLoginMutation,
} = coreApiSlice;
