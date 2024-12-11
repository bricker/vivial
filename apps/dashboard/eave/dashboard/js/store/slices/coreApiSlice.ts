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
  OutingAnonymousDocument,
  OutingAnonymousQuery,
  OutingAnonymousQueryVariables,
  OutingAuthenticatedDocument,
  OutingAuthenticatedQuery,
  OutingAuthenticatedQueryVariables,
  OutingPreferencesDocument,
  PlanOutingAnonymousDocument,
  PlanOutingAuthenticatedDocument,
  ReplanOutingAnonymousDocument,
  ReplanOutingAuthenticatedDocument,
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
  type PlanOutingAnonymousMutation,
  type PlanOutingAnonymousMutationVariables,
  type PlanOutingAuthenticatedMutation,
  type PlanOutingAuthenticatedMutationVariables,
  type ReplanOutingAnonymousMutation,
  type ReplanOutingAnonymousMutationVariables,
  type ReplanOutingAuthenticatedMutation,
  type ReplanOutingAuthenticatedMutationVariables,
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

    getOutingAnonymous: builder.query<OutingAnonymousQuery, OutingAnonymousQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: OutingAnonymousDocument, variables });
        return { data };
      },
    }),

    getOutingAuthenticated: builder.query<OutingAuthenticatedQuery, OutingAuthenticatedQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: OutingAuthenticatedDocument, variables });
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

    planOutingAnonymous: builder.mutation<PlanOutingAnonymousMutation, PlanOutingAnonymousMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: PlanOutingAnonymousDocument, variables });
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

    replanOutingAnonymous: builder.mutation<ReplanOutingAnonymousMutation, ReplanOutingAnonymousMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ReplanOutingAnonymousDocument, variables });
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
  useGetOutingAnonymousQuery,
  useGetOutingAuthenticatedQuery,

  // Core API GraphQL Mutation Hooks
  usePlanOutingAnonymousMutation,
  usePlanOutingAuthenticatedMutation,
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
