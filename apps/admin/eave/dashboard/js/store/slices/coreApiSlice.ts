import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { CORE_API_INTERNAL_BASE } from "../../util/http";

import {
  BookingDetailsDocument,
  ListBookedOutingsDocument,
  ListBookedOutingsQuery,
  ListBookedOutingsQueryVariables,
  ListReserverDetailsDocument,
  UpdateBookingDocument,
  type BookingDetailsQuery,
  type BookingDetailsQueryVariables,
  type ListReserverDetailsQuery,
  type ListReserverDetailsQueryVariables,
  type UpdateBookingMutation,
  type UpdateBookingMutationVariables,
} from "../../graphql/generated/graphql";

import type {} from "@reduxjs/toolkit/query";
import { executeOperation } from "../../graphql/graphql-fetch";

export const coreApiSlice = createApi({
  reducerPath: "coreApi",
  baseQuery: fetchBaseQuery({ baseUrl: CORE_API_INTERNAL_BASE }),
  endpoints: (builder) => ({
    /**
     * Admin Core API - GraphQL Queries
     */
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

    getBookingDetials: builder.query<BookingDetailsQuery, BookingDetailsQueryVariables>({
      async queryFn(variables, _api, _extraOptions, _baseQuery) {
        const data = await executeOperation({ query: BookingDetailsDocument, variables });
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
  useListReserverDetailsQuery,
  useListBookedOutingsQuery,
  useGetBookingDetialsQuery,

  // Admin Core API GraphQL Mutation Hooks
  useUpdateBookingMutation,
} = coreApiSlice;
