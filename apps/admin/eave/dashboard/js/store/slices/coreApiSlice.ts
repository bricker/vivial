import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { CORE_API_INTERNAL_BASE } from "../../util/http";

import {
  AdminBookingInfoDocument,
  AdminBookingInfoQuery,
  AdminBookingInfoQueryVariables,
  ListBookedOutingsDocument,
  ListBookedOutingsQuery,
  ListBookedOutingsQueryVariables,
  ReserverDetailsDocument,
  ReserverDetailsQuery,
  ReserverDetailsQueryVariables,
  UpdateBookingDocument,
  UpdateBookingMutation,
  UpdateBookingMutationVariables,
} from "$eave-dashboard/js/graphql/generated/graphql";
import type {} from "@reduxjs/toolkit/query";
import { executeOperation } from "../../graphql/graphql-fetch";

export const coreApiSlice = createApi({
  reducerPath: "coreApi",
  baseQuery: fetchBaseQuery({ baseUrl: CORE_API_INTERNAL_BASE }),
  endpoints: (builder) => ({
    /**
     * Admin Core API - GraphQL Queries
     */
    getReserverDetails: builder.query<ReserverDetailsQuery, ReserverDetailsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ReserverDetailsDocument, variables });
        return { data };
      },
    }),

    listBookedOutings: builder.query<ListBookedOutingsQuery, ListBookedOutingsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: ListBookedOutingsDocument, variables });
        return { data };
      },
    }),

    getBookingInfo: builder.query<AdminBookingInfoQuery, AdminBookingInfoQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: AdminBookingInfoDocument, variables });
        return { data };
      },
    }),

    /**
     * Admin Core API - GraphQL Mutations
     */
    updateBooking: builder.mutation<UpdateBookingMutation, UpdateBookingMutationVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: UpdateBookingDocument, variables });
        return { data };
      },
    }),
  }),
});

export const {
  // Admin Core API GraphQL Query Hooks
  useGetReserverDetailsQuery,
  useListBookedOutingsQuery,
  useGetBookingInfoQuery,

  // Admin Core API GraphQL Mutation Hooks
  useUpdateBookingMutation,
} = coreApiSlice;
