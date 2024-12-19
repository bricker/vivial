/* eslint-disable */
import * as types from './graphql';



/**
 * Map of all GraphQL operations in the project.
 *
 * This map has several performance disadvantages:
 * 1. It is not tree-shakeable, so it will include all operations in the project.
 * 2. It is not minifiable, so the string of a GraphQL query will be multiple times inside the bundle.
 * 3. It does not support dead code elimination, so it will add unused operations.
 *
 * Therefore it is highly recommended to use the babel or swc plugin for production.
 * Learn more about it here: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client#reducing-bundle-size
 */
const documents = {
    "fragment AddressFields on Address {\n  address1\n  address2\n  city\n  state\n  zipCode\n  country\n  formattedMultiline\n  formattedSingleline\n}": types.AddressFieldsFragmentDoc,
    "fragment BookingFields on Booking {\n  id\n  state\n  reserverDetails {\n    id\n    firstName\n    lastName\n    phoneNumber\n  }\n}": types.BookingFieldsFragmentDoc,
    "fragment CostBreakdownFields on CostBreakdown {\n  baseCostCents\n  feeCents\n  taxCents\n  totalCostCents\n}": types.CostBreakdownFieldsFragmentDoc,
    "fragment LocationFields on Location {\n  directionsUri\n  coordinates {\n    lat\n    lon\n  }\n  address {\n    ...AddressFields\n  }\n  searchRegion {\n    id\n    name\n  }\n}": types.LocationFieldsFragmentDoc,
    "fragment PhotoFields on Photo {\n  id\n  src\n  alt\n  attributions\n}": types.PhotoFieldsFragmentDoc,
    "mutation UpdateBooking($input: AdminUpdateBookingInput!) {\n  adminUpdateBooking(input: $input) {\n    ... on AdminUpdateBookingSuccess {\n      __typename\n      booking {\n        ...BookingFields\n      }\n    }\n    ... on AdminUpdateBookingFailure {\n      __typename\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}": types.UpdateBookingDocument,
    "mutation UpdateReserverDetails($input: AdminUpdateReserverDetailsInput!) {\n  adminUpdateReserverDetails(input: $input) {\n    __typename\n    ... on AdminUpdateReserverDetailsSuccess {\n      reserverDetails {\n        id\n        firstName\n        lastName\n        phoneNumber\n      }\n    }\n    ... on AdminUpdateReserverDetailsFailure {\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}": types.UpdateReserverDetailsDocument,
    "query AdminBookingInfo($bookingId: UUID!) {\n  adminBooking(bookingId: $bookingId) {\n    id\n    accounts {\n      id\n      email\n    }\n    activityStartTime\n    activityName\n    activityBookingLink\n    activitySource\n    activitySourceId\n    restaurantArrivalTime\n    restaurantName\n    restaurantBookingLink\n    restaurantSource\n    restaurantSourceId\n    state\n    reserverDetails {\n      id\n      firstName\n      lastName\n      phoneNumber\n    }\n    stripePaymentId\n    survey {\n      id\n      headcount\n      budget\n      startTime\n      searchRegions {\n        id\n        name\n      }\n    }\n  }\n  adminBookingActivityDetail(bookingId: $bookingId) {\n    categoryGroup {\n      id\n      name\n      activityCategories {\n        id\n        name\n        isDefault\n      }\n    }\n    sourceId\n    source\n    name\n    description\n    websiteUri\n    doorTips\n    insiderTips\n    parkingTips\n    ticketInfo {\n      name\n      notes\n      costBreakdown {\n        ...CostBreakdownFields\n      }\n    }\n    venue {\n      name\n      location {\n        ...LocationFields\n      }\n    }\n    photos {\n      coverPhoto {\n        ...PhotoFields\n      }\n      supplementalPhotos {\n        ...PhotoFields\n      }\n    }\n  }\n  adminBookingRestaurantDetail(bookingId: $bookingId) {\n    sourceId\n    source\n    name\n    reservable\n    rating\n    primaryTypeName\n    websiteUri\n    description\n    parkingTips\n    customerFavorites\n    location {\n      ...LocationFields\n    }\n    photos {\n      coverPhoto {\n        ...PhotoFields\n      }\n      supplementalPhotos {\n        ...PhotoFields\n      }\n    }\n  }\n}": types.AdminBookingInfoDocument,
    "query ListBookedOutings($accountId: UUID!) {\n  adminBookings(accountId: $accountId) {\n    id\n    activityStartTime\n    restaurantArrivalTime\n    activityName\n    restaurantName\n    photoUri\n    state\n  }\n}": types.ListBookedOutingsDocument,
    "query ReserverDetails($reserverDetailsId: UUID!) {\n  adminReserverDetails(reserverDetailsId: $reserverDetailsId) {\n    id\n    firstName\n    lastName\n    phoneNumber\n  }\n}": types.ReserverDetailsDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment AddressFields on Address {\n  address1\n  address2\n  city\n  state\n  zipCode\n  country\n  formattedMultiline\n  formattedSingleline\n}"): typeof import('./graphql').AddressFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment BookingFields on Booking {\n  id\n  state\n  reserverDetails {\n    id\n    firstName\n    lastName\n    phoneNumber\n  }\n}"): typeof import('./graphql').BookingFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment CostBreakdownFields on CostBreakdown {\n  baseCostCents\n  feeCents\n  taxCents\n  totalCostCents\n}"): typeof import('./graphql').CostBreakdownFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment LocationFields on Location {\n  directionsUri\n  coordinates {\n    lat\n    lon\n  }\n  address {\n    ...AddressFields\n  }\n  searchRegion {\n    id\n    name\n  }\n}"): typeof import('./graphql').LocationFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment PhotoFields on Photo {\n  id\n  src\n  alt\n  attributions\n}"): typeof import('./graphql').PhotoFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateBooking($input: AdminUpdateBookingInput!) {\n  adminUpdateBooking(input: $input) {\n    ... on AdminUpdateBookingSuccess {\n      __typename\n      booking {\n        ...BookingFields\n      }\n    }\n    ... on AdminUpdateBookingFailure {\n      __typename\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}"): typeof import('./graphql').UpdateBookingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateReserverDetails($input: AdminUpdateReserverDetailsInput!) {\n  adminUpdateReserverDetails(input: $input) {\n    __typename\n    ... on AdminUpdateReserverDetailsSuccess {\n      reserverDetails {\n        id\n        firstName\n        lastName\n        phoneNumber\n      }\n    }\n    ... on AdminUpdateReserverDetailsFailure {\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}"): typeof import('./graphql').UpdateReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query AdminBookingInfo($bookingId: UUID!) {\n  adminBooking(bookingId: $bookingId) {\n    id\n    accounts {\n      id\n      email\n    }\n    activityStartTime\n    activityName\n    activityBookingLink\n    activitySource\n    activitySourceId\n    restaurantArrivalTime\n    restaurantName\n    restaurantBookingLink\n    restaurantSource\n    restaurantSourceId\n    state\n    reserverDetails {\n      id\n      firstName\n      lastName\n      phoneNumber\n    }\n    stripePaymentId\n    survey {\n      id\n      headcount\n      budget\n      startTime\n      searchRegions {\n        id\n        name\n      }\n    }\n  }\n  adminBookingActivityDetail(bookingId: $bookingId) {\n    categoryGroup {\n      id\n      name\n      activityCategories {\n        id\n        name\n        isDefault\n      }\n    }\n    sourceId\n    source\n    name\n    description\n    websiteUri\n    doorTips\n    insiderTips\n    parkingTips\n    ticketInfo {\n      name\n      notes\n      costBreakdown {\n        ...CostBreakdownFields\n      }\n    }\n    venue {\n      name\n      location {\n        ...LocationFields\n      }\n    }\n    photos {\n      coverPhoto {\n        ...PhotoFields\n      }\n      supplementalPhotos {\n        ...PhotoFields\n      }\n    }\n  }\n  adminBookingRestaurantDetail(bookingId: $bookingId) {\n    sourceId\n    source\n    name\n    reservable\n    rating\n    primaryTypeName\n    websiteUri\n    description\n    parkingTips\n    customerFavorites\n    location {\n      ...LocationFields\n    }\n    photos {\n      coverPhoto {\n        ...PhotoFields\n      }\n      supplementalPhotos {\n        ...PhotoFields\n      }\n    }\n  }\n}"): typeof import('./graphql').AdminBookingInfoDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query ListBookedOutings($accountId: UUID!) {\n  adminBookings(accountId: $accountId) {\n    id\n    activityStartTime\n    restaurantArrivalTime\n    activityName\n    restaurantName\n    photoUri\n    state\n  }\n}"): typeof import('./graphql').ListBookedOutingsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query ReserverDetails($reserverDetailsId: UUID!) {\n  adminReserverDetails(reserverDetailsId: $reserverDetailsId) {\n    id\n    firstName\n    lastName\n    phoneNumber\n  }\n}"): typeof import('./graphql').ReserverDetailsDocument;


export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}
