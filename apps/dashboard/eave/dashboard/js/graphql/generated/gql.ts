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
    "mutation CreateBooking($input: CreateBookingInput!) {\n  viewer {\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createBooking(input: $input) {\n        ... on CreateBookingSuccess {\n          __typename\n          booking {\n            id\n          }\n        }\n        ... on CreateBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      reason\n    }\n  }\n}": types.CreateBookingDocument,
    "mutation CreatePaymentIntent($input: CreatePaymentIntentInput!) {\n  viewer {\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createPaymentIntent(input: $input) {\n        __typename\n        ... on CreatePaymentIntentSuccess {\n          __typename\n          paymentIntent {\n            clientSecret\n          }\n        }\n        ... on CreatePaymentIntentFailure {\n          __typename\n          failureReason\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      reason\n    }\n  }\n}": types.CreatePaymentIntentDocument,
    "mutation PlanOuting($input: PlanOutingInput!) {\n  planOuting(input: $input) {\n    __typename\n    ... on PlanOutingSuccess {\n      outing {\n        id\n      }\n    }\n    ... on PlanOutingFailure {\n      failureReason\n    }\n  }\n}": types.PlanOutingDocument,
    "mutation ReplanOuting($input: ReplanOutingInput!) {\n  replanOuting(input: $input) {\n    __typename\n    ... on ReplanOutingSuccess {\n      outing {\n        id\n      }\n    }\n    ... on ReplanOutingFailure {\n      failureReason\n    }\n  }\n}": types.ReplanOutingDocument,
    "mutation SubmitReserverDetails($input: ReserverDetailsInput!) {\n  viewer {\n    ... on AuthenticatedViewerMutations {\n      __typename\n      submitReserverDetails(input: $input) {\n        __typename\n        ... on SubmitReserverDetailsSuccess {\n          __typename\n          reserverDetails {\n            id\n          }\n        }\n        ... on SubmitReserverDetailsFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      reason\n    }\n  }\n}": types.SubmitReserverDetailsDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation CreateBooking($input: CreateBookingInput!) {\n  viewer {\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createBooking(input: $input) {\n        ... on CreateBookingSuccess {\n          __typename\n          booking {\n            id\n          }\n        }\n        ... on CreateBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      reason\n    }\n  }\n}"): typeof import('./graphql').CreateBookingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation CreatePaymentIntent($input: CreatePaymentIntentInput!) {\n  viewer {\n    ... on AuthenticatedViewerMutations {\n      __typename\n      createPaymentIntent(input: $input) {\n        __typename\n        ... on CreatePaymentIntentSuccess {\n          __typename\n          paymentIntent {\n            clientSecret\n          }\n        }\n        ... on CreatePaymentIntentFailure {\n          __typename\n          failureReason\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      reason\n    }\n  }\n}"): typeof import('./graphql').CreatePaymentIntentDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation PlanOuting($input: PlanOutingInput!) {\n  planOuting(input: $input) {\n    __typename\n    ... on PlanOutingSuccess {\n      outing {\n        id\n      }\n    }\n    ... on PlanOutingFailure {\n      failureReason\n    }\n  }\n}"): typeof import('./graphql').PlanOutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation ReplanOuting($input: ReplanOutingInput!) {\n  replanOuting(input: $input) {\n    __typename\n    ... on ReplanOutingSuccess {\n      outing {\n        id\n      }\n    }\n    ... on ReplanOutingFailure {\n      failureReason\n    }\n  }\n}"): typeof import('./graphql').ReplanOutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation SubmitReserverDetails($input: ReserverDetailsInput!) {\n  viewer {\n    ... on AuthenticatedViewerMutations {\n      __typename\n      submitReserverDetails(input: $input) {\n        __typename\n        ... on SubmitReserverDetailsSuccess {\n          __typename\n          reserverDetails {\n            id\n          }\n        }\n        ... on SubmitReserverDetailsFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      reason\n    }\n  }\n}"): typeof import('./graphql').SubmitReserverDetailsDocument;


export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}
