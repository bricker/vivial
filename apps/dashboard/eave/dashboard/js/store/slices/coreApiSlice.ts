import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import {
  BillingPortalUrlDocument,
  BookedOutingsDocument,
  BookingDetailsDocument,
  ConfirmBookingDocument,
  CreateAccountDocument,
  InitiateBookingDocument,
  LoginDocument,
  OneClickBookingCriteriaDocument,
  OutingDocument,
  OutingPreferencesDocument,
  OutingQuery,
  OutingQueryVariables,
  PlanOutingDocument,
  ReserverDetailsDocument,
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
  type BillingPortalUrlQuery,
  type BillingPortalUrlQueryVariables,
  type BookedOutingsQuery,
  type BookedOutingsQueryVariables,
  type BookingDetailsQuery,
  type BookingDetailsQueryVariables,
  type ConfirmBookingMutation,
  type ConfirmBookingMutationVariables,
  type CreateAccountMutation,
  type CreateAccountMutationVariables,
  type InitiateBookingMutation,
  type InitiateBookingMutationVariables,
  type LoginMutation,
  type LoginMutationVariables,
  type OneClickBookingCriteriaQuery,
  type OneClickBookingCriteriaQueryVariables,
  type OutingPreferencesQuery,
  type OutingPreferencesQueryVariables,
  type PlanOutingMutation,
  type PlanOutingMutationVariables,
  type ReserverDetailsQuery,
  type ReserverDetailsQueryVariables,
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
      forceRefetch(_args) {
        // Temporary hack; Outing Preferences aren't being handled in the cache correctly atm
        return true;
      },
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

    listReserverDetails: builder.query<ReserverDetailsQuery, ReserverDetailsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ReserverDetailsDocument, variables });
        return { data };
      },
    }),

    listBookedOutings: builder.query<BookedOutingsQuery, BookedOutingsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: BookedOutingsDocument, variables });
        return { data };
      },
    }),

    getOuting: builder.query<OutingQuery, OutingQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: OutingDocument, variables });
        return { data };
      },
    }),

    getBookingDetails: builder.query<BookingDetailsQuery, BookingDetailsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: BookingDetailsDocument, variables });
        return { data };
      },
    }),

    getOneClickBookingCriteria: builder.query<OneClickBookingCriteriaQuery, OneClickBookingCriteriaQueryVariables>({
      forceRefetch(_args) {
        // This operation gets data from Stripe, and the payment methods may have changed through some other means besides this client.
        // Therefore, we have to force-refetch to get the most up to date data.
        return true;
      },
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: OneClickBookingCriteriaDocument, variables });
        return { data };
      },
    }),

    getBillingPortalUrl: builder.query<BillingPortalUrlQuery, BillingPortalUrlQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: BillingPortalUrlDocument, variables });
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
        console.info("Planning outing with the following inputs:", variables.input);
        const data = await executeOperation({ query: PlanOutingDocument, variables });
        return { data };
      },
    }),

    initiateBooking: builder.query<InitiateBookingMutation, InitiateBookingMutationVariables>({
      // This is marked as query on purpose.
      // On the server it's a mutation but this needs to be called when a component loads and rtk-query
      // doesn't seem to allow that.
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: InitiateBookingDocument, variables });
        return { data };
      },
    }),

    initiateAndConfirmBooking: builder.mutation<InitiateBookingMutation, InitiateBookingMutationVariables>({
      // This is marked as query on purpose.
      // On the server it's a mutation but this needs to be called when a component loads and rtk-query
      // doesn't seem to allow that.
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: InitiateBookingDocument, variables });
        return { data };
      },
    }),

    confirmBooking: builder.mutation<ConfirmBookingMutation, ConfirmBookingMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ConfirmBookingDocument, variables });
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
  useGetBookingDetailsQuery,
  useGetOneClickBookingCriteriaQuery,
  useGetBillingPortalUrlQuery,

  // Core API GraphQL Mutation Hooks
  usePlanOutingMutation,
  useCreateAccountMutation,
  useLoginMutation,
  useUpdateReserverDetailsAccountMutation,
  useUpdateAccountMutation,
  useInitiateAndConfirmBookingMutation,
  useInitiateBookingQuery, // This is actually a mutation but we need to make it available as a query so we can run it on component load
  useConfirmBookingMutation,
  useUpdateReserverDetailsMutation,
  useSubmitReserverDetailsMutation,
  useUpdateOutingPreferencesMutation,
} = coreApiSlice;
