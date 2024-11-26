import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import {
  CreateAccountDocument,
  LoginDocument,
  SearchRegionsDocument,
  UpdateReserverDetailsAccountDocument,
  UpdateReserverDetailsAccountInput,
  UpdateReserverDetailsAccountMutation,
  type CreateAccountInput,
  type CreateAccountMutation,
  type LoginInput,
  type LoginMutation,
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
    createAccount: builder.mutation<{ data: CreateAccountMutation }, CreateAccountInput>({
      query: (input) => ({
        ...gqlParams,
        body: {
          query: CreateAccountDocument,
          variables: { input },
        },
      }),
    }),
    login: builder.mutation<{ data: LoginMutation }, LoginInput>({
      query: (input) => ({
        ...gqlParams,
        body: {
          query: LoginDocument,
          variables: { input },
        },
      }),
    }),
    updateReserverDetailsAccount: builder.mutation<
      { data: UpdateReserverDetailsAccountMutation },
      UpdateReserverDetailsAccountInput
    >({
      query: (input) => ({
        ...gqlParams,
        body: {
          query: UpdateReserverDetailsAccountDocument,
          variables: { input },
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
  useUpdateReserverDetailsAccountMutation,
} = coreApiSlice;
