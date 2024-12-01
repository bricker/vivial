import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import {
  createApi,
  fetchBaseQuery,
} from "@reduxjs/toolkit/query/react";

import {
  CreateAccountDocument,
  CreatePaymentIntentDocument,
  ListReserverDetailsDocument,
  LoginDocument,
  SearchRegionsDocument,
  UpdateReserverDetailsAccountDocument,
  type CreateAccountMutation,
  type CreateAccountMutationVariables,
  type CreatePaymentIntentMutation,
  type CreatePaymentIntentMutationVariables,
  type ListReserverDetailsQuery,
  type ListReserverDetailsQueryVariables,
  type LoginMutation,
  type LoginMutationVariables,
  type SearchRegionsQuery,
  type SearchRegionsQueryVariables,
  type UpdateReserverDetailsAccountMutation,
  type UpdateReserverDetailsAccountMutationVariables,
} from "$eave-dashboard/js/graphql/generated/graphql";

import type {
} from '@reduxjs/toolkit/query'
import { executeOperation } from "$eave-dashboard/js/graphql/graphql-fetch";

export const coreApiSlice = createApi({
  reducerPath: "coreApi",
  baseQuery: fetchBaseQuery({ baseUrl: CORE_API_BASE }),
  endpoints: (builder) => ({
    /**
     * Core API - GraphQL Queries
     */
    getSearchRegions: builder.query<SearchRegionsQuery, SearchRegionsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: SearchRegionsDocument, variables });
        return { data };
      },
    }),

    listReserverDetails: builder.query<ListReserverDetailsQuery, ListReserverDetailsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ListReserverDetailsDocument, variables });
        return { data };
      },
    }),
    /**
     * Core API - GraphQL Mutations
     */
    createAccount: builder.mutation<CreateAccountMutation, CreateAccountMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: CreateAccountDocument, variables });
        return { data };
      },
    }),

    login: builder.mutation<LoginMutation, LoginMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: LoginDocument, variables });
        return { data };
      },
    }),

    createPaymentIntent: builder.mutation<CreatePaymentIntentMutation, CreatePaymentIntentMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: CreatePaymentIntentDocument, variables });
        return { data };
      },
    }),

    updateReserverDetailsAccount: builder.mutation<UpdateReserverDetailsAccountMutation, UpdateReserverDetailsAccountMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateReserverDetailsAccountDocument, variables });
        return { data };
      },
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
  useCreatePaymentIntentMutation,
  useUpdateReserverDetailsAccountMutation,
} = coreApiSlice;
