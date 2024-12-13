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
    "fragment OutingFields on Outing {\n  id\n  headcount\n  activityStartTime\n  restaurantArrivalTime\n  drivingTime\n  activity {\n    sourceId\n    source\n    name\n    description\n    websiteUri\n    doorTips\n    insiderTips\n    parkingTips\n    venue {\n      name\n      location {\n        directionsUri\n        latitude\n        longitude\n        formattedAddress\n      }\n    }\n    photos {\n      coverPhotoUri\n      supplementalPhotoUris\n    }\n    ticketInfo {\n      type\n      notes\n      cost\n      fee\n      tax\n    }\n  }\n  restaurant {\n    sourceId\n    source\n    name\n    reservable\n    rating\n    primaryTypeName\n    websiteUri\n    description\n    parkingTips\n    customerFavorites\n    location {\n      directionsUri\n      latitude\n      longitude\n      formattedAddress\n    }\n    photos {\n      coverPhotoUri\n      supplementalPhotoUris\n    }\n  }\n}": types.OutingFieldsFragmentDoc,
    "fragment PlanOutingFields on PlanOutingResult {\n  ... on PlanOutingSuccess {\n    outing {\n      ...OutingFields\n    }\n  }\n  ... on PlanOutingFailure {\n    failureReason\n  }\n}": types.PlanOutingFieldsFragmentDoc,
    "fragment ReplanOutingFields on ReplanOutingResult {\n  ... on ReplanOutingSuccess {\n    outing {\n      ...OutingFields\n    }\n  }\n  ... on ReplanOutingFailure {\n    failureReason\n  }\n}": types.ReplanOutingFieldsFragmentDoc,
    "mutation CreateAccount($input: CreateAccountInput!) {\n  createAccount(input: $input) {\n    ... on CreateAccountSuccess {\n      account {\n        id\n        email\n      }\n    }\n    ... on CreateAccountFailure {\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}": types.CreateAccountDocument,
    "mutation CreateBooking($input: CreateBookingInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createBooking(input: $input) {\n        ... on CreateBookingSuccess {\n          __typename\n          booking {\n            id\n          }\n        }\n        ... on CreateBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.CreateBookingDocument,
    "mutation CreatePaymentIntent {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createPaymentIntent {\n        __typename\n        ... on CreatePaymentIntentSuccess {\n          __typename\n          paymentIntent {\n            clientSecret\n          }\n        }\n        ... on CreatePaymentIntentFailure {\n          __typename\n          failureReason\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.CreatePaymentIntentDocument,
    "mutation Login($input: LoginInput!) {\n  login(input: $input) {\n    __typename\n    ... on LoginSuccess {\n      __typename\n      account {\n        id\n        email\n      }\n    }\n    ... on LoginFailure {\n      __typename\n      failureReason\n    }\n  }\n}": types.LoginDocument,
    "mutation PlanOuting($input: PlanOutingInput!) {\n  planOuting(input: $input) {\n    ...PlanOutingFields\n  }\n}": types.PlanOutingDocument,
    "mutation ReplanOuting($input: ReplanOutingInput!) {\n  replanOuting(input: $input) {\n    ...ReplanOutingFields\n  }\n}": types.ReplanOutingDocument,
    "mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      submitReserverDetails(input: $input) {\n        __typename\n        ... on SubmitReserverDetailsSuccess {\n          __typename\n          reserverDetails {\n            id\n          }\n        }\n        ... on SubmitReserverDetailsFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.SubmitReserverDetailsDocument,
    "mutation UpdateAccount($input: UpdateAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updateAccount(input: $input) {\n        __typename\n        ... on UpdateAccountSuccess {\n          account {\n            email\n          }\n        }\n        ... on UpdateAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateAccountDocument,
    "mutation UpdateOutingPreferences($input: UpdateOutingPreferencesInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updatePreferences(input: $input) {\n        __typename\n        ... on UpdateOutingPreferencesSuccess {\n          outingPreferences {\n            restaurantCategories {\n              id\n              name\n              isDefault\n            }\n            activityCategories {\n              id\n              name\n              isDefault\n            }\n          }\n        }\n        ... on UpdateOutingPreferencesFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateOutingPreferencesDocument,
    "mutation UpdateReserverDetails($input: UpdateReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetails(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsSuccess {\n          reserverDetails {\n            id\n            firstName\n            lastName\n            phoneNumber\n          }\n        }\n        ... on UpdateReserverDetailsFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateReserverDetailsDocument,
    "mutation UpdateReserverDetailsAccount($input: UpdateReserverDetailsAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetailsAccount(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsAccountSuccess {\n          reserverDetails {\n            id\n            firstName\n            lastName\n            phoneNumber\n          }\n          account {\n            id\n            email\n          }\n        }\n        ... on UpdateReserverDetailsAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateReserverDetailsAccountDocument,
    "query ListBookedOutings {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      bookedOutings {\n        id\n        activityStartTime\n        restaurantArrivalTime\n        activityName\n        restaurantName\n        photoUri\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.ListBookedOutingsDocument,
    "query ListReserverDetails {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      reserverDetails {\n        id\n        firstName\n        lastName\n        phoneNumber\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.ListReserverDetailsDocument,
    "query Outing($input: OutingInput!) {\n  outing(input: $input) {\n    ...OutingFields\n  }\n}": types.OutingDocument,
    "query OutingPreferences {\n  activityCategoryGroups {\n    id\n    name\n    activityCategories {\n      id\n      name\n      isDefault\n    }\n  }\n  restaurantCategories {\n    id\n    name\n    isDefault\n  }\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      outingPreferences {\n        restaurantCategories {\n          id\n          name\n          isDefault\n        }\n        activityCategories {\n          id\n          name\n          isDefault\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.OutingPreferencesDocument,
    "query SearchRegions {\n  searchRegions {\n    id\n    name\n  }\n}": types.SearchRegionsDocument,
    "query StripePortal {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      stripePortal {\n        url\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.StripePortalDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment OutingFields on Outing {\n  id\n  headcount\n  activityStartTime\n  restaurantArrivalTime\n  drivingTime\n  activity {\n    sourceId\n    source\n    name\n    description\n    websiteUri\n    doorTips\n    insiderTips\n    parkingTips\n    venue {\n      name\n      location {\n        directionsUri\n        latitude\n        longitude\n        formattedAddress\n      }\n    }\n    photos {\n      coverPhotoUri\n      supplementalPhotoUris\n    }\n    ticketInfo {\n      type\n      notes\n      cost\n      fee\n      tax\n    }\n  }\n  restaurant {\n    sourceId\n    source\n    name\n    reservable\n    rating\n    primaryTypeName\n    websiteUri\n    description\n    parkingTips\n    customerFavorites\n    location {\n      directionsUri\n      latitude\n      longitude\n      formattedAddress\n    }\n    photos {\n      coverPhotoUri\n      supplementalPhotoUris\n    }\n  }\n}"): typeof import('./graphql').OutingFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment PlanOutingFields on PlanOutingResult {\n  ... on PlanOutingSuccess {\n    outing {\n      ...OutingFields\n    }\n  }\n  ... on PlanOutingFailure {\n    failureReason\n  }\n}"): typeof import('./graphql').PlanOutingFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ReplanOutingFields on ReplanOutingResult {\n  ... on ReplanOutingSuccess {\n    outing {\n      ...OutingFields\n    }\n  }\n  ... on ReplanOutingFailure {\n    failureReason\n  }\n}"): typeof import('./graphql').ReplanOutingFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation CreateAccount($input: CreateAccountInput!) {\n  createAccount(input: $input) {\n    ... on CreateAccountSuccess {\n      account {\n        id\n        email\n      }\n    }\n    ... on CreateAccountFailure {\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}"): typeof import('./graphql').CreateAccountDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation CreateBooking($input: CreateBookingInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createBooking(input: $input) {\n        ... on CreateBookingSuccess {\n          __typename\n          booking {\n            id\n          }\n        }\n        ... on CreateBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').CreateBookingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation CreatePaymentIntent {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createPaymentIntent {\n        __typename\n        ... on CreatePaymentIntentSuccess {\n          __typename\n          paymentIntent {\n            clientSecret\n          }\n        }\n        ... on CreatePaymentIntentFailure {\n          __typename\n          failureReason\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').CreatePaymentIntentDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation Login($input: LoginInput!) {\n  login(input: $input) {\n    __typename\n    ... on LoginSuccess {\n      __typename\n      account {\n        id\n        email\n      }\n    }\n    ... on LoginFailure {\n      __typename\n      failureReason\n    }\n  }\n}"): typeof import('./graphql').LoginDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation PlanOuting($input: PlanOutingInput!) {\n  planOuting(input: $input) {\n    ...PlanOutingFields\n  }\n}"): typeof import('./graphql').PlanOutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation ReplanOuting($input: ReplanOutingInput!) {\n  replanOuting(input: $input) {\n    ...ReplanOutingFields\n  }\n}"): typeof import('./graphql').ReplanOutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      submitReserverDetails(input: $input) {\n        __typename\n        ... on SubmitReserverDetailsSuccess {\n          __typename\n          reserverDetails {\n            id\n          }\n        }\n        ... on SubmitReserverDetailsFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').SubmitReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateAccount($input: UpdateAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updateAccount(input: $input) {\n        __typename\n        ... on UpdateAccountSuccess {\n          account {\n            email\n          }\n        }\n        ... on UpdateAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateAccountDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateOutingPreferences($input: UpdateOutingPreferencesInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updatePreferences(input: $input) {\n        __typename\n        ... on UpdateOutingPreferencesSuccess {\n          outingPreferences {\n            restaurantCategories {\n              id\n              name\n              isDefault\n            }\n            activityCategories {\n              id\n              name\n              isDefault\n            }\n          }\n        }\n        ... on UpdateOutingPreferencesFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateOutingPreferencesDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateReserverDetails($input: UpdateReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetails(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsSuccess {\n          reserverDetails {\n            id\n            firstName\n            lastName\n            phoneNumber\n          }\n        }\n        ... on UpdateReserverDetailsFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateReserverDetailsAccount($input: UpdateReserverDetailsAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetailsAccount(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsAccountSuccess {\n          reserverDetails {\n            id\n            firstName\n            lastName\n            phoneNumber\n          }\n          account {\n            id\n            email\n          }\n        }\n        ... on UpdateReserverDetailsAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateReserverDetailsAccountDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query ListBookedOutings {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      bookedOutings {\n        id\n        activityStartTime\n        restaurantArrivalTime\n        activityName\n        restaurantName\n        photoUri\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').ListBookedOutingsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query ListReserverDetails {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      reserverDetails {\n        id\n        firstName\n        lastName\n        phoneNumber\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').ListReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query Outing($input: OutingInput!) {\n  outing(input: $input) {\n    ...OutingFields\n  }\n}"): typeof import('./graphql').OutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query OutingPreferences {\n  activityCategoryGroups {\n    id\n    name\n    activityCategories {\n      id\n      name\n      isDefault\n    }\n  }\n  restaurantCategories {\n    id\n    name\n    isDefault\n  }\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      outingPreferences {\n        restaurantCategories {\n          id\n          name\n          isDefault\n        }\n        activityCategories {\n          id\n          name\n          isDefault\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').OutingPreferencesDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query SearchRegions {\n  searchRegions {\n    id\n    name\n  }\n}"): typeof import('./graphql').SearchRegionsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query StripePortal {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      stripePortal {\n        url\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').StripePortalDocument;


export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}
