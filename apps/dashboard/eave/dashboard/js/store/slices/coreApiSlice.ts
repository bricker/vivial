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
  OutingDocument,
  OutingPreferencesDocument,
  OutingQuery,
  OutingQueryVariables,
  PlanOutingDocument,
  SearchRegionsDocument,
  SubmitReserverDetailsDocument,
  UpdateAccountDocument,
  UpdateAccountMutation,
  UpdateAccountMutationVariables,
  UpdateOutingPreferencesDocument,
  UpdateOutingPreferencesMutation,
  UpdateOutingPreferencesMutationVariables,
  UpdateReserverDetailsAccountDocument,
  UpdateReserverDetailsDocument,
  UpdateReserverDetailsMutation,
  UpdateReserverDetailsMutationVariables,
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
  type PlanOutingMutation,
  type PlanOutingMutationVariables,
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

    getOuting: builder.query<OutingQuery, OutingQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: OutingDocument, variables });
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

    updateOutingPreferences: builder.mutation<
      UpdateOutingPreferencesMutation,
      UpdateOutingPreferencesMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateOutingPreferencesDocument, variables });
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

    updateReserverDetails: builder.mutation<UpdateReserverDetailsMutation, UpdateReserverDetailsMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateReserverDetailsDocument, variables });
        return { data };
      },
    }),

    // TODO: combine + rm server
    updateReserverDetailsAccount: builder.mutation<
      UpdateReserverDetailsAccountMutation,
      UpdateReserverDetailsAccountMutationVariables
    >({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateReserverDetailsAccountDocument, variables });
        return { data };
      },
    }),

    planOuting: builder.mutation<PlanOutingMutation, PlanOutingMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: PlanOutingDocument, variables });
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
  useGetOutingQuery,

  // Core API GraphQL Mutation Hooks
  usePlanOutingMutation,
  useCreateAccountMutation,
  useLoginMutation,
  useCreatePaymentIntentMutation,
  useUpdateReserverDetailsAccountMutation,
  useUpdateAccountMutation,
  useCreateBookingMutation,
  useUpdateReserverDetailsMutation,
  useSubmitReserverDetailsMutation,
  useUpdateOutingPreferencesMutation,
} = coreApiSlice;
