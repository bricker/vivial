import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import {
  CreateAccountDocument,
  CreateBookingDocument,
  CreatePaymentIntentDocument,
  ListBookedOutingsDocument,
  ListBookedOutingsQuery,
  ListBookedOutingsQueryVariables,
  ListReserverDetailsDocument,
  LoginDocument,
  OutingPreferencesDocument,
  PlanOutingAuthenticatedDocument,
  PlanOutingUnauthenticatedDocument,
  ReplanOutingAuthenticatedDocument,
  ReplanOutingUnauthenticatedDocument,
  SearchRegionsDocument,
  SubmitReserverDetailsDocument,
  UpdateAccountDocument,
  UpdateAccountMutation,
  UpdateAccountMutationVariables,
  UpdateReserverDetailsAccountDocument,
  type CreateAccountMutation,
  type CreateAccountMutationVariables,
  type CreateBookingMutation,
  type CreateBookingMutationVariables,
  type CreatePaymentIntentMutation,
  type CreatePaymentIntentMutationVariables,
  type ListReserverDetailsQuery,
  type ListReserverDetailsQueryVariables,
  type LoginMutation,
  type LoginMutationVariables,
  type OutingPreferencesQuery,
  type OutingPreferencesQueryVariables,
  type PlanOutingAuthenticatedMutation,
  type PlanOutingAuthenticatedMutationVariables,
  type PlanOutingUnauthenticatedMutation,
  type PlanOutingUnauthenticatedMutationVariables,
  type ReplanOutingAuthenticatedMutation,
  type ReplanOutingAuthenticatedMutationVariables,
  type ReplanOutingUnauthenticatedMutation,
  type ReplanOutingUnauthenticatedMutationVariables,
  type SearchRegionsQuery,
  type SearchRegionsQueryVariables,
  type SubmitReserverDetailsMutation,
  type SubmitReserverDetailsMutationVariables,
  type UpdateReserverDetailsAccountMutation,
  type UpdateReserverDetailsAccountMutationVariables,
} from "$eave-dashboard/js/graphql/generated/graphql";

import { executeOperation } from "$eave-dashboard/js/graphql/graphql-fetch";
import type {} from "@reduxjs/toolkit/query";

export const coreApiSlice = createApi({
  reducerPath: "coreApi",
  baseQuery: fetchBaseQuery({ baseUrl: CORE_API_BASE }),
  endpoints: (builder) => ({
    /**
     * Core API - GraphQL Queries
     */
    getOutingPreferences: builder.query<OutingPreferencesQuery, OutingPreferencesQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: OutingPreferencesDocument, variables });
        return { data };
      },
    }),

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

    listBookedOutings: builder.query<ListBookedOutingsQuery, ListBookedOutingsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ListBookedOutingsDocument, variables });
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

    updateAccount: builder.mutation<UpdateAccountMutation, UpdateAccountMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateAccountDocument, variables });
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

    submitReserverDetails: builder.mutation<SubmitReserverDetailsMutation, SubmitReserverDetailsMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: SubmitReserverDetailsDocument, variables });
        return { data };
      },
    }),

    updateReserverDetailsAccount: builder.mutation<
      UpdateReserverDetailsAccountMutation,
      UpdateReserverDetailsAccountMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateReserverDetailsAccountDocument, variables });
        return { data };
      },
    }),

    planOutingAuthenticated: builder.mutation<
      PlanOutingAuthenticatedMutation,
      PlanOutingAuthenticatedMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: PlanOutingAuthenticatedDocument, variables });
        return { data };
      },
    }),

    planOutingUnauthenticated: builder.mutation<
      PlanOutingUnauthenticatedMutation,
      PlanOutingUnauthenticatedMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: PlanOutingUnauthenticatedDocument, variables });
        return { data };
      },
    }),

    replanOutingAuthenticated: builder.mutation<
      ReplanOutingAuthenticatedMutation,
      ReplanOutingAuthenticatedMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ReplanOutingAuthenticatedDocument, variables });
        return { data };
      },
    }),

    replanOutingUnauthenticated: builder.mutation<
      ReplanOutingUnauthenticatedMutation,
      ReplanOutingUnauthenticatedMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ReplanOutingUnauthenticatedDocument, variables });
        return { data };
      },
    }),

    createBooking: builder.mutation<CreateBookingMutation, CreateBookingMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: CreateBookingDocument, variables });
        return { data };
      },
    }),
  }),
});

export const {
  // Core API GraphQL Query Hooks
  useGetSearchRegionsQuery,
  useListReserverDetailsQuery,
  useListBookedOutingsQuery,
  useGetOutingPreferencesQuery,

  // Core API GraphQL Mutation Hooks
  useCreateAccountMutation,
  useLoginMutation,
  useCreatePaymentIntentMutation,
  useUpdateReserverDetailsAccountMutation,
  useUpdateAccountMutation,
} = coreApiSlice;
