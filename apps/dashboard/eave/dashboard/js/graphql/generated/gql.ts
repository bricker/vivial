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
    "fragment AccountFields on Account {\n  id\n  email\n  stripeCustomerId\n}": types.AccountFieldsFragmentDoc,
    "fragment ActivityFields on Activity {\n  categoryGroup {\n    id\n    name\n    activityCategories {\n      ...ActivityCategoryFields\n    }\n  }\n  sourceId\n  source\n  name\n  description\n  websiteUri\n  doorTips\n  insiderTips\n  parkingTips\n  primaryTypeName\n  ticketInfo {\n    name\n    notes\n    costBreakdown {\n      ...CostBreakdownFields\n    }\n  }\n  venue {\n    name\n    location {\n      ...LocationFields\n    }\n  }\n  photos {\n    ...PhotosFields\n  }\n}": types.ActivityFieldsFragmentDoc,
    "fragment ActivityPlanFields on ActivityPlan {\n  startTime\n  headcount\n  costBreakdown {\n    ...CostBreakdownFields\n  }\n  activity {\n    ...ActivityFields\n  }\n}": types.ActivityPlanFieldsFragmentDoc,
    "fragment AddressFields on Address {\n  address1\n  address2\n  city\n  state\n  zipCode\n  country\n  formattedMultiline\n  formattedSingleline\n}": types.AddressFieldsFragmentDoc,
    "fragment BookingFields on Booking {\n  id\n  state\n  reserverDetails {\n    ...ReserverDetailsFields\n  }\n}\n\nfragment BookingDetailsPeekFields on BookingDetailsPeek {\n  id\n  activityStartTime\n  restaurantArrivalTime\n  activityName\n  restaurantName\n  photoUri\n  state\n}": types.BookingFieldsFragmentDoc,
    "fragment ActivityCategoryFields on ActivityCategory {\n  id\n  name\n  isDefault\n}\n\nfragment ActivityCategoryGroupFields on ActivityCategoryGroup {\n  id\n  name\n  activityCategories {\n    ...ActivityCategoryFields\n  }\n}\n\nfragment RestaurantCategoryFields on RestaurantCategory {\n  id\n  name\n  isDefault\n}": types.ActivityCategoryFieldsFragmentDoc,
    "fragment CostBreakdownFields on CostBreakdown {\n  baseCostCents\n  feeCents\n  taxCents\n  totalCostCents\n}": types.CostBreakdownFieldsFragmentDoc,
    "fragment CustomerSessionFields on CustomerSession {\n  clientSecret\n}": types.CustomerSessionFieldsFragmentDoc,
    "fragment ItineraryFields on Itinerary {\n  id\n  startTime\n  headcount\n  survey {\n    ...SurveyFields\n  }\n  searchRegions {\n    ...SearchRegionFields\n  }\n  costBreakdown {\n    ...CostBreakdownFields\n  }\n  activityPlan {\n    ...ActivityPlanFields\n  }\n  reservation {\n    ...ReservationFields\n  }\n}\n\nfragment TravelFields on Itinerary {\n  travel {\n    durationText\n    distanceText\n  }\n}": types.ItineraryFieldsFragmentDoc,
    "fragment LocationFields on Location {\n  directionsUri\n  coordinates {\n    lat\n    lon\n  }\n  address {\n    ...AddressFields\n  }\n  searchRegion {\n    ...SearchRegionFields\n  }\n}": types.LocationFieldsFragmentDoc,
    "fragment OutingPreferencesFields on OutingPreferences {\n  restaurantCategories {\n    ...RestaurantCategoryFields\n  }\n  activityCategories {\n    ...ActivityCategoryFields\n  }\n}": types.OutingPreferencesFieldsFragmentDoc,
    "fragment PaymentIntentFields on PaymentIntent {\n  id\n  clientSecret\n}": types.PaymentIntentFieldsFragmentDoc,
    "fragment PaymentMethodFields on PaymentMethod {\n  id\n  card {\n    brand\n    last4\n    expMonth\n    expYear\n  }\n}": types.PaymentMethodFieldsFragmentDoc,
    "fragment PhotosFields on Photos {\n  coverPhoto {\n    ...PhotoFields\n  }\n  supplementalPhotos {\n    ...PhotoFields\n  }\n}\n\nfragment PhotoFields on Photo {\n  id\n  src\n  alt\n  attributions\n}": types.PhotosFieldsFragmentDoc,
    "fragment ReservationFields on Reservation {\n  arrivalTime\n  headcount\n  costBreakdown {\n    ...CostBreakdownFields\n  }\n  restaurant {\n    sourceId\n    source\n    name\n    reservable\n    rating\n    primaryTypeName\n    websiteUri\n    description\n    parkingTips\n    customerFavorites\n    location {\n      ...LocationFields\n    }\n    photos {\n      coverPhoto {\n        ...PhotoFields\n      }\n      supplementalPhotos {\n        ...PhotoFields\n      }\n    }\n  }\n}": types.ReservationFieldsFragmentDoc,
    "fragment ReserverDetailsFields on ReserverDetails {\n  id\n  firstName\n  lastName\n  phoneNumber\n}": types.ReserverDetailsFieldsFragmentDoc,
    "fragment SearchRegionFields on SearchRegion {\n  id\n  name\n}": types.SearchRegionFieldsFragmentDoc,
    "fragment SurveyFields on Survey {\n  id\n  budget\n  headcount\n  searchRegions {\n    ...SearchRegionFields\n  }\n  startTime\n}": types.SurveyFieldsFragmentDoc,
    "mutation ConfirmBooking($input: ConfirmBookingInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      confirmBooking(input: $input) {\n        ... on ConfirmBookingSuccess {\n          __typename\n          booking {\n            ...BookingFields\n          }\n        }\n        ... on ConfirmBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.ConfirmBookingDocument,
    "mutation CreateAccount($input: CreateAccountInput!) {\n  createAccount(input: $input) {\n    ... on CreateAccountSuccess {\n      account {\n        ...AccountFields\n      }\n    }\n    ... on CreateAccountFailure {\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}": types.CreateAccountDocument,
    "mutation InitiateBooking($input: InitiateBookingInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      initiateBooking(input: $input) {\n        ... on InitiateBookingSuccess {\n          __typename\n          booking {\n            ...ItineraryFields\n          }\n          paymentIntent {\n            ...PaymentIntentFields\n          }\n          customerSession {\n            ...CustomerSessionFields\n          }\n        }\n        ... on InitiateBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.InitiateBookingDocument,
    "mutation Login($input: LoginInput!) {\n  login(input: $input) {\n    __typename\n    ... on LoginSuccess {\n      __typename\n      account {\n        ...AccountFields\n      }\n    }\n    ... on LoginFailure {\n      __typename\n      failureReason\n    }\n  }\n}": types.LoginDocument,
    "mutation PlanOuting($input: PlanOutingInput!) {\n  planOuting(input: $input) {\n    ... on PlanOutingSuccess {\n      outing {\n        ...ItineraryFields\n        ...TravelFields\n      }\n    }\n    ... on PlanOutingFailure {\n      failureReason\n    }\n  }\n}": types.PlanOutingDocument,
    "mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      submitReserverDetails(input: $input) {\n        __typename\n        ... on SubmitReserverDetailsSuccess {\n          __typename\n          reserverDetails {\n            ...ReserverDetailsFields\n          }\n        }\n        ... on SubmitReserverDetailsFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.SubmitReserverDetailsDocument,
    "mutation UpdateAccount($input: UpdateAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updateAccount(input: $input) {\n        __typename\n        ... on UpdateAccountSuccess {\n          account {\n            ...AccountFields\n          }\n        }\n        ... on UpdateAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateAccountDocument,
    "mutation UpdateOutingPreferences($input: UpdateOutingPreferencesInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updatePreferences(input: $input) {\n        __typename\n        ... on UpdateOutingPreferencesSuccess {\n          outingPreferences {\n            ...OutingPreferencesFields\n          }\n        }\n        ... on UpdateOutingPreferencesFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateOutingPreferencesDocument,
    "mutation UpdateReserverDetails($input: UpdateReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetails(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsSuccess {\n          reserverDetails {\n            ...ReserverDetailsFields\n          }\n        }\n        ... on UpdateReserverDetailsFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateReserverDetailsDocument,
    "mutation UpdateReserverDetailsAccount($input: UpdateReserverDetailsAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetailsAccount(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsAccountSuccess {\n          reserverDetails {\n            ...ReserverDetailsFields\n          }\n          account {\n            ...AccountFields\n          }\n        }\n        ... on UpdateReserverDetailsAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.UpdateReserverDetailsAccountDocument,
    "query BookedOutings {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      bookedOutings {\n        ...BookingDetailsPeekFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.BookedOutingsDocument,
    "query BookingDetails($input: GetBookingDetailsQueryInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      bookedOutingDetails(input: $input) {\n        ...ItineraryFields\n        ...TravelFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      authFailureReason\n    }\n  }\n}": types.BookingDetailsDocument,
    "query OneClickBookingCriteria {\n  viewer {\n    ... on AuthenticatedViewerQueries {\n      reserverDetails {\n        ...ReserverDetailsFields\n      }\n      paymentMethods {\n        ...PaymentMethodFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.OneClickBookingCriteriaDocument,
    "query Outing($input: OutingInput!) {\n  outing(input: $input) {\n    ...ItineraryFields\n    ...TravelFields\n  }\n}": types.OutingDocument,
    "query OutingPreferences {\n  activityCategoryGroups {\n    ...ActivityCategoryGroupFields\n  }\n  restaurantCategories {\n    ...RestaurantCategoryFields\n  }\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      outingPreferences {\n        ...OutingPreferencesFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.OutingPreferencesDocument,
    "query ReserverDetails {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      reserverDetails {\n        ...ReserverDetailsFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}": types.ReserverDetailsDocument,
    "query SearchRegions {\n  searchRegions {\n    ...SearchRegionFields\n  }\n}": types.SearchRegionsDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment AccountFields on Account {\n  id\n  email\n  stripeCustomerId\n}"): typeof import('./graphql').AccountFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ActivityFields on Activity {\n  categoryGroup {\n    id\n    name\n    activityCategories {\n      ...ActivityCategoryFields\n    }\n  }\n  sourceId\n  source\n  name\n  description\n  websiteUri\n  doorTips\n  insiderTips\n  parkingTips\n  primaryTypeName\n  ticketInfo {\n    name\n    notes\n    costBreakdown {\n      ...CostBreakdownFields\n    }\n  }\n  venue {\n    name\n    location {\n      ...LocationFields\n    }\n  }\n  photos {\n    ...PhotosFields\n  }\n}"): typeof import('./graphql').ActivityFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ActivityPlanFields on ActivityPlan {\n  startTime\n  headcount\n  costBreakdown {\n    ...CostBreakdownFields\n  }\n  activity {\n    ...ActivityFields\n  }\n}"): typeof import('./graphql').ActivityPlanFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment AddressFields on Address {\n  address1\n  address2\n  city\n  state\n  zipCode\n  country\n  formattedMultiline\n  formattedSingleline\n}"): typeof import('./graphql').AddressFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment BookingFields on Booking {\n  id\n  state\n  reserverDetails {\n    ...ReserverDetailsFields\n  }\n}\n\nfragment BookingDetailsPeekFields on BookingDetailsPeek {\n  id\n  activityStartTime\n  restaurantArrivalTime\n  activityName\n  restaurantName\n  photoUri\n  state\n}"): typeof import('./graphql').BookingFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ActivityCategoryFields on ActivityCategory {\n  id\n  name\n  isDefault\n}\n\nfragment ActivityCategoryGroupFields on ActivityCategoryGroup {\n  id\n  name\n  activityCategories {\n    ...ActivityCategoryFields\n  }\n}\n\nfragment RestaurantCategoryFields on RestaurantCategory {\n  id\n  name\n  isDefault\n}"): typeof import('./graphql').ActivityCategoryFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment CostBreakdownFields on CostBreakdown {\n  baseCostCents\n  feeCents\n  taxCents\n  totalCostCents\n}"): typeof import('./graphql').CostBreakdownFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment CustomerSessionFields on CustomerSession {\n  clientSecret\n}"): typeof import('./graphql').CustomerSessionFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ItineraryFields on Itinerary {\n  id\n  startTime\n  headcount\n  survey {\n    ...SurveyFields\n  }\n  searchRegions {\n    ...SearchRegionFields\n  }\n  costBreakdown {\n    ...CostBreakdownFields\n  }\n  activityPlan {\n    ...ActivityPlanFields\n  }\n  reservation {\n    ...ReservationFields\n  }\n}\n\nfragment TravelFields on Itinerary {\n  travel {\n    durationText\n    distanceText\n  }\n}"): typeof import('./graphql').ItineraryFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment LocationFields on Location {\n  directionsUri\n  coordinates {\n    lat\n    lon\n  }\n  address {\n    ...AddressFields\n  }\n  searchRegion {\n    ...SearchRegionFields\n  }\n}"): typeof import('./graphql').LocationFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment OutingPreferencesFields on OutingPreferences {\n  restaurantCategories {\n    ...RestaurantCategoryFields\n  }\n  activityCategories {\n    ...ActivityCategoryFields\n  }\n}"): typeof import('./graphql').OutingPreferencesFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment PaymentIntentFields on PaymentIntent {\n  id\n  clientSecret\n}"): typeof import('./graphql').PaymentIntentFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment PaymentMethodFields on PaymentMethod {\n  id\n  card {\n    brand\n    last4\n    expMonth\n    expYear\n  }\n}"): typeof import('./graphql').PaymentMethodFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment PhotosFields on Photos {\n  coverPhoto {\n    ...PhotoFields\n  }\n  supplementalPhotos {\n    ...PhotoFields\n  }\n}\n\nfragment PhotoFields on Photo {\n  id\n  src\n  alt\n  attributions\n}"): typeof import('./graphql').PhotosFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ReservationFields on Reservation {\n  arrivalTime\n  headcount\n  costBreakdown {\n    ...CostBreakdownFields\n  }\n  restaurant {\n    sourceId\n    source\n    name\n    reservable\n    rating\n    primaryTypeName\n    websiteUri\n    description\n    parkingTips\n    customerFavorites\n    location {\n      ...LocationFields\n    }\n    photos {\n      coverPhoto {\n        ...PhotoFields\n      }\n      supplementalPhotos {\n        ...PhotoFields\n      }\n    }\n  }\n}"): typeof import('./graphql').ReservationFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment ReserverDetailsFields on ReserverDetails {\n  id\n  firstName\n  lastName\n  phoneNumber\n}"): typeof import('./graphql').ReserverDetailsFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment SearchRegionFields on SearchRegion {\n  id\n  name\n}"): typeof import('./graphql').SearchRegionFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "fragment SurveyFields on Survey {\n  id\n  budget\n  headcount\n  searchRegions {\n    ...SearchRegionFields\n  }\n  startTime\n}"): typeof import('./graphql').SurveyFieldsFragmentDoc;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation ConfirmBooking($input: ConfirmBookingInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      confirmBooking(input: $input) {\n        ... on ConfirmBookingSuccess {\n          __typename\n          booking {\n            ...BookingFields\n          }\n        }\n        ... on ConfirmBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').ConfirmBookingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation CreateAccount($input: CreateAccountInput!) {\n  createAccount(input: $input) {\n    ... on CreateAccountSuccess {\n      account {\n        ...AccountFields\n      }\n    }\n    ... on CreateAccountFailure {\n      failureReason\n      validationErrors {\n        field\n      }\n    }\n  }\n}"): typeof import('./graphql').CreateAccountDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation InitiateBooking($input: InitiateBookingInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      initiateBooking(input: $input) {\n        ... on InitiateBookingSuccess {\n          __typename\n          booking {\n            ...ItineraryFields\n          }\n          paymentIntent {\n            ...PaymentIntentFields\n          }\n          customerSession {\n            ...CustomerSessionFields\n          }\n        }\n        ... on InitiateBookingFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').InitiateBookingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation Login($input: LoginInput!) {\n  login(input: $input) {\n    __typename\n    ... on LoginSuccess {\n      __typename\n      account {\n        ...AccountFields\n      }\n    }\n    ... on LoginFailure {\n      __typename\n      failureReason\n    }\n  }\n}"): typeof import('./graphql').LoginDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation PlanOuting($input: PlanOutingInput!) {\n  planOuting(input: $input) {\n    ... on PlanOutingSuccess {\n      outing {\n        ...ItineraryFields\n        ...TravelFields\n      }\n    }\n    ... on PlanOutingFailure {\n      failureReason\n    }\n  }\n}"): typeof import('./graphql').PlanOutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      submitReserverDetails(input: $input) {\n        __typename\n        ... on SubmitReserverDetailsSuccess {\n          __typename\n          reserverDetails {\n            ...ReserverDetailsFields\n          }\n        }\n        ... on SubmitReserverDetailsFailure {\n          __typename\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').SubmitReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateAccount($input: UpdateAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updateAccount(input: $input) {\n        __typename\n        ... on UpdateAccountSuccess {\n          account {\n            ...AccountFields\n          }\n        }\n        ... on UpdateAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateAccountDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateOutingPreferences($input: UpdateOutingPreferencesInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      updatePreferences(input: $input) {\n        __typename\n        ... on UpdateOutingPreferencesSuccess {\n          outingPreferences {\n            ...OutingPreferencesFields\n          }\n        }\n        ... on UpdateOutingPreferencesFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateOutingPreferencesDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateReserverDetails($input: UpdateReserverDetailsInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetails(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsSuccess {\n          reserverDetails {\n            ...ReserverDetailsFields\n          }\n        }\n        ... on UpdateReserverDetailsFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "mutation UpdateReserverDetailsAccount($input: UpdateReserverDetailsAccountInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerMutations {\n      __typename\n      updateReserverDetailsAccount(input: $input) {\n        __typename\n        ... on UpdateReserverDetailsAccountSuccess {\n          reserverDetails {\n            ...ReserverDetailsFields\n          }\n          account {\n            ...AccountFields\n          }\n        }\n        ... on UpdateReserverDetailsAccountFailure {\n          failureReason\n          validationErrors {\n            field\n          }\n        }\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').UpdateReserverDetailsAccountDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query BookedOutings {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      bookedOutings {\n        ...BookingDetailsPeekFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').BookedOutingsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query BookingDetails($input: GetBookingDetailsQueryInput!) {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      bookedOutingDetails(input: $input) {\n        ...ItineraryFields\n        ...TravelFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').BookingDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query OneClickBookingCriteria {\n  viewer {\n    ... on AuthenticatedViewerQueries {\n      reserverDetails {\n        ...ReserverDetailsFields\n      }\n      paymentMethods {\n        ...PaymentMethodFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').OneClickBookingCriteriaDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query Outing($input: OutingInput!) {\n  outing(input: $input) {\n    ...ItineraryFields\n    ...TravelFields\n  }\n}"): typeof import('./graphql').OutingDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query OutingPreferences {\n  activityCategoryGroups {\n    ...ActivityCategoryGroupFields\n  }\n  restaurantCategories {\n    ...RestaurantCategoryFields\n  }\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      outingPreferences {\n        ...OutingPreferencesFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').OutingPreferencesDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query ReserverDetails {\n  viewer {\n    __typename\n    ... on AuthenticatedViewerQueries {\n      __typename\n      reserverDetails {\n        ...ReserverDetailsFields\n      }\n    }\n    ... on UnauthenticatedViewer {\n      __typename\n      authFailureReason\n    }\n  }\n}"): typeof import('./graphql').ReserverDetailsDocument;
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "query SearchRegions {\n  searchRegions {\n    ...SearchRegionFields\n  }\n}"): typeof import('./graphql').SearchRegionsDocument;


export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}
