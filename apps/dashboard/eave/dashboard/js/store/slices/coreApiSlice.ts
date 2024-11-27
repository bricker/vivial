import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery, type FetchArgs } from "@reduxjs/toolkit/query/react";

import {
  CreateAccountDocument,
  ListReserverDetailsDocument,
  ListReserverDetailsQuery,
  LoginDocument,
  SearchRegionsDocument,
  UpdateReserverDetailsAccountDocument,
  UpdateReserverDetailsAccountInput,
  UpdateReserverDetailsAccountMutation,
  type CreateAccountInput,
  type CreateAccountMutation,
  type CreateAccountMutationVariables,
  type LoginMutation,
  type LoginMutationVariables,
  type SearchRegionsQuery,
} from "$eave-dashboard/js/graphql/generated/graphql";

const gqlParams: FetchArgs = {
  url: "/graphql",
  method: "POST",
  credentials: "include", // This is required so that the cookies are sent to the subdomain (api.)
};

export const coreApiSlice = createApi({
  reducerPath: "coreApi",
  baseQuery: fetchBaseQuery({
    baseUrl: CORE_API_BASE,
  }),

  endpoints: (builder) => ({
    /**
     * Core API - GraphQL Queries
     */
    getSearchRegions: builder.query<SearchRegionsQuery, void>({
      query: () => ({ ...gqlParams, body: { query: SearchRegionsDocument } }),
    }),
    listReserverDetails: builder.query<ListReserverDetailsQuery, void>({
      query: () => ({ ...gqlParams, body: { query: ListReserverDetailsDocument } }),
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
  // Core API GraphQL Query Hooks
  useGetSearchRegionsQuery,
  useListReserverDetailsQuery,

  // Core API GraphQL Mutation Hooks
  useCreateAccountMutation,
  useLoginMutation,
  useUpdateReserverDetailsAccountMutation,
} = coreApiSlice;
