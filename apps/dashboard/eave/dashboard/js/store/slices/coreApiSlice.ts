import { CORE_API_BASE } from "$eave-dashboard/js/util/http";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import {
  ActivityCategoriesDocument,
  CreateAccountDocument,
  CreatePaymentIntentDocument,
  ListBookedOutingsDocument,
  ListBookedOutingsQuery,
  ListBookedOutingsQueryVariables,
  ListReserverDetailsDocument,
  LoginDocument,
  RestaurantCategoriesDocument,
  SearchRegionsDocument,
  UpdateAccountDocument,
  UpdateAccountMutation,
  UpdateAccountMutationVariables,
  UpdateReserverDetailsAccountDocument,
  type ActivityCategoriesQuery,
  type ActivityCategoriesQueryVariables,
  type CreateAccountMutation,
  type CreateAccountMutationVariables,
  type CreatePaymentIntentMutation,
  type CreatePaymentIntentMutationVariables,
  type ListReserverDetailsQuery,
  type ListReserverDetailsQueryVariables,
  type LoginMutation,
  type LoginMutationVariables,
  type RestaurantCategoriesQuery,
  type RestaurantCategoriesQueryVariables,
  type SearchRegionsQuery,
  type SearchRegionsQueryVariables,
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
    getActivityCategories: builder.query<ActivityCategoriesQuery, ActivityCategoriesQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ActivityCategoriesDocument, variables });
        return { data };
      },
    }),

    getRestaurantCategories: builder.query<RestaurantCategoriesQuery, RestaurantCategoriesQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: RestaurantCategoriesDocument, variables });
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

    updateReserverDetailsAccount: builder.mutation<
      UpdateReserverDetailsAccountMutation,
      UpdateReserverDetailsAccountMutationVariables
    >({
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
  useGetActivityCategoriesQuery,
  useGetRestaurantCategoriesQuery,
  useListReserverDetailsQuery,
  useListBookedOutingsQuery,

  // Core API GraphQL Mutation Hooks
  useCreateAccountMutation,
  useLoginMutation,
  useCreatePaymentIntentMutation,
  useUpdateReserverDetailsAccountMutation,
  useUpdateAccountMutation,
} = coreApiSlice;
