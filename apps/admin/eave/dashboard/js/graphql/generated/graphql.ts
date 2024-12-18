/* eslint-disable */
// @ts-nocheck
import type { DocumentTypeDecoration } from '@graphql-typed-document-node/core';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  /** Date with time (isoformat) */
  DateTime: { input: string; output: string; }
  UUID: { input: string; output: string; }
};

export type Account = {
  __typename?: 'Account';
  email: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
};

export type Activity = {
  __typename?: 'Activity';
  categoryGroup?: Maybe<ActivityCategoryGroup>;
  description?: Maybe<Scalars['String']['output']>;
  doorTips?: Maybe<Scalars['String']['output']>;
  insiderTips?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos: Photos;
  source: ActivitySource;
  sourceId: Scalars['String']['output'];
  ticketInfo?: Maybe<TicketInfo>;
  venue: ActivityVenue;
  websiteUri?: Maybe<Scalars['String']['output']>;
};

export type ActivityCategory = {
  __typename?: 'ActivityCategory';
  id: Scalars['UUID']['output'];
  isDefault: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
};

export type ActivityCategoryGroup = {
  __typename?: 'ActivityCategoryGroup';
  activityCategories: Array<ActivityCategory>;
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
};

export enum ActivitySource {
  Eventbrite = 'EVENTBRITE',
  GooglePlaces = 'GOOGLE_PLACES',
  Internal = 'INTERNAL'
}

export type ActivityVenue = {
  __typename?: 'ActivityVenue';
  location: Location;
  name: Scalars['String']['output'];
};

export type Address = {
  __typename?: 'Address';
  address1?: Maybe<Scalars['String']['output']>;
  address2?: Maybe<Scalars['String']['output']>;
  city?: Maybe<Scalars['String']['output']>;
  country?: Maybe<Scalars['String']['output']>;
  formattedMultiline: Scalars['String']['output'];
  formattedSingleline: Scalars['String']['output'];
  state?: Maybe<Scalars['String']['output']>;
  zipCode?: Maybe<Scalars['String']['output']>;
};

export type AuthenticatedViewerMutations = {
  __typename?: 'AuthenticatedViewerMutations';
  confirmBooking: ConfirmBookingResult;
  initiateBooking: InitiateBookingResult;
  submitReserverDetails: SubmitReserverDetailsResult;
  updateAccount: UpdateAccountResult;
  updateBooking: UpdateBookingResult;
  updateOutingPreferences: UpdateOutingPreferencesResult;
  updatePreferences: UpdateOutingPreferencesResult;
  updateReserverDetails: UpdateReserverDetailsResult;
  updateReserverDetailsAccount: UpdateReserverDetailsAccountResult;
};


export type AuthenticatedViewerMutationsConfirmBookingArgs = {
  input: ConfirmBookingInput;
};


export type AuthenticatedViewerMutationsInitiateBookingArgs = {
  input: InitiateBookingInput;
};


export type AuthenticatedViewerMutationsSubmitReserverDetailsArgs = {
  input: SubmitReserverDetailsInput;
};


export type AuthenticatedViewerMutationsUpdateAccountArgs = {
  input: UpdateAccountInput;
};


export type AuthenticatedViewerMutationsUpdateBookingArgs = {
  input: UpdateBookingInput;
};


export type AuthenticatedViewerMutationsUpdateOutingPreferencesArgs = {
  input: UpdateOutingPreferencesInput;
};


export type AuthenticatedViewerMutationsUpdatePreferencesArgs = {
  input: UpdateOutingPreferencesInput;
};


export type AuthenticatedViewerMutationsUpdateReserverDetailsArgs = {
  input: UpdateReserverDetailsInput;
};


export type AuthenticatedViewerMutationsUpdateReserverDetailsAccountArgs = {
  input: UpdateReserverDetailsAccountInput;
};

export type AuthenticatedViewerQueries = {
  __typename?: 'AuthenticatedViewerQueries';
  bookedOutingDetails: BookingDetails;
  bookedOutings: Array<BookingDetailPeek>;
  outingPreferences: OutingPreferences;
  reserverDetails: Array<ReserverDetails>;
};


export type AuthenticatedViewerQueriesBookedOutingDetailsArgs = {
  input: GetBookingDetailsQueryInput;
};

export enum AuthenticationFailureReason {
  AccessTokenExpired = 'ACCESS_TOKEN_EXPIRED',
  AccessTokenInvalid = 'ACCESS_TOKEN_INVALID'
}

export type Booking = {
  __typename?: 'Booking';
  id: Scalars['UUID']['output'];
  reserverDetails?: Maybe<ReserverDetails>;
  state: BookingState;
};

export type BookingDetailPeek = {
  __typename?: 'BookingDetailPeek';
  activityName?: Maybe<Scalars['String']['output']>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  id: Scalars['UUID']['output'];
  photoUri?: Maybe<Scalars['String']['output']>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
  restaurantName?: Maybe<Scalars['String']['output']>;
  state: BookingState;
};

export type BookingDetails = {
  __typename?: 'BookingDetails';
  activity?: Maybe<Activity>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  costBreakdown: CostBreakdown;
  drivingTime?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  restaurant?: Maybe<Restaurant>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
  survey?: Maybe<Survey>;
};

export enum BookingState {
  Booked = 'BOOKED',
  Canceled = 'CANCELED',
  Confirmed = 'CONFIRMED',
  Initiated = 'INITIATED'
}

export type ConfirmBookingFailure = {
  __typename?: 'ConfirmBookingFailure';
  failureReason: ConfirmBookingFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum ConfirmBookingFailureReason {
  BookingNotFound = 'BOOKING_NOT_FOUND',
  InvalidPaymentIntent = 'INVALID_PAYMENT_INTENT',
  PaymentRequired = 'PAYMENT_REQUIRED',
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type ConfirmBookingInput = {
  bookingId: Scalars['UUID']['input'];
  paymentIntent?: InputMaybe<PaymentIntentInput>;
};

export type ConfirmBookingResult = ConfirmBookingFailure | ConfirmBookingSuccess;

export type ConfirmBookingSuccess = {
  __typename?: 'ConfirmBookingSuccess';
  booking: Booking;
};

export type CostBreakdown = {
  __typename?: 'CostBreakdown';
  baseCostCents: Scalars['Int']['output'];
  feeCents: Scalars['Int']['output'];
  taxCents: Scalars['Int']['output'];
  totalCostCents: Scalars['Int']['output'];
};

export type CreateAccountFailure = {
  __typename?: 'CreateAccountFailure';
  failureReason: CreateAccountFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum CreateAccountFailureReason {
  AccountExists = 'ACCOUNT_EXISTS',
  ValidationErrors = 'VALIDATION_ERRORS',
  WeakPassword = 'WEAK_PASSWORD'
}

export type CreateAccountInput = {
  email: Scalars['String']['input'];
  plaintextPassword: Scalars['String']['input'];
};

export type CreateAccountResult = CreateAccountFailure | CreateAccountSuccess;

export type CreateAccountSuccess = {
  __typename?: 'CreateAccountSuccess';
  account: Account;
};

export type GeoPoint = {
  __typename?: 'GeoPoint';
  lat: Scalars['Float']['output'];
  lon: Scalars['Float']['output'];
};

export type GetBookingDetailsQueryInput = {
  bookingId: Scalars['UUID']['input'];
};

export type InitiateBookingFailure = {
  __typename?: 'InitiateBookingFailure';
  failureReason: InitiateBookingFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum InitiateBookingFailureReason {
  PaymentIntentFailed = 'PAYMENT_INTENT_FAILED',
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON',
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type InitiateBookingInput = {
  outingId: Scalars['UUID']['input'];
};

export type InitiateBookingResult = InitiateBookingFailure | InitiateBookingSuccess;

export type InitiateBookingSuccess = {
  __typename?: 'InitiateBookingSuccess';
  booking: BookingDetails;
  paymentIntent?: Maybe<PaymentIntent>;
};

export type Location = {
  __typename?: 'Location';
  address: Address;
  coordinates: GeoPoint;
  directionsUri?: Maybe<Scalars['String']['output']>;
  searchRegion: SearchRegion;
};

export type LoginFailure = {
  __typename?: 'LoginFailure';
  failureReason: LoginFailureReason;
};

export enum LoginFailureReason {
  InvalidCredentials = 'INVALID_CREDENTIALS'
}

export type LoginInput = {
  email: Scalars['String']['input'];
  plaintextPassword: Scalars['String']['input'];
};

export type LoginResult = LoginFailure | LoginSuccess;

export type LoginSuccess = {
  __typename?: 'LoginSuccess';
  account: Account;
};

export type Mutation = {
  __typename?: 'Mutation';
  createAccount: CreateAccountResult;
  login: LoginResult;
  planOuting: PlanOutingResult;
  viewer: ViewerMutations;
};


export type MutationCreateAccountArgs = {
  input: CreateAccountInput;
};


export type MutationLoginArgs = {
  input: LoginInput;
};


export type MutationPlanOutingArgs = {
  input: PlanOutingInput;
};

export type Outing = {
  __typename?: 'Outing';
  activity?: Maybe<Activity>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  costBreakdown: CostBreakdown;
  drivingTime?: Maybe<Scalars['String']['output']>;
  id: Scalars['UUID']['output'];
  restaurant?: Maybe<Restaurant>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
  survey?: Maybe<Survey>;
};

export enum OutingBudget {
  Expensive = 'EXPENSIVE',
  Free = 'FREE',
  Inexpensive = 'INEXPENSIVE',
  Moderate = 'MODERATE',
  VeryExpensive = 'VERY_EXPENSIVE'
}

export type OutingInput = {
  id: Scalars['UUID']['input'];
};

export type OutingPreferences = {
  __typename?: 'OutingPreferences';
  activityCategories?: Maybe<Array<ActivityCategory>>;
  restaurantCategories?: Maybe<Array<RestaurantCategory>>;
};

export type OutingPreferencesInput = {
  activityCategoryIds: Array<Scalars['UUID']['input']>;
  restaurantCategoryIds: Array<Scalars['UUID']['input']>;
};

export type PaymentIntent = {
  __typename?: 'PaymentIntent';
  clientSecret: Scalars['String']['output'];
  id: Scalars['String']['output'];
};

export type PaymentIntentInput = {
  clientSecret: Scalars['String']['input'];
  id: Scalars['String']['input'];
};

export type Photo = {
  __typename?: 'Photo';
  alt?: Maybe<Scalars['String']['output']>;
  attributions: Array<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  src: Scalars['String']['output'];
};

export type Photos = {
  __typename?: 'Photos';
  coverPhoto?: Maybe<Photo>;
  supplementalPhotos: Array<Photo>;
};

export type PlanOutingFailure = {
  __typename?: 'PlanOutingFailure';
  failureReason: PlanOutingFailureReason;
};

export enum PlanOutingFailureReason {
  SearchAreaIdsEmpty = 'SEARCH_AREA_IDS_EMPTY',
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type PlanOutingInput = {
  budget: OutingBudget;
  groupPreferences: Array<OutingPreferencesInput>;
  headcount: Scalars['Int']['input'];
  searchAreaIds: Array<Scalars['UUID']['input']>;
  startTime: Scalars['DateTime']['input'];
};

export type PlanOutingResult = PlanOutingFailure | PlanOutingSuccess;

export type PlanOutingSuccess = {
  __typename?: 'PlanOutingSuccess';
  outing: Outing;
};

export type Query = {
  __typename?: 'Query';
  activityCategoryGroups: Array<ActivityCategoryGroup>;
  outing?: Maybe<Outing>;
  restaurantCategories: Array<RestaurantCategory>;
  searchRegions: Array<SearchRegion>;
  viewer: ViewerQueries;
};


export type QueryOutingArgs = {
  input: OutingInput;
};

export type ReserverDetails = {
  __typename?: 'ReserverDetails';
  firstName: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  lastName: Scalars['String']['output'];
  phoneNumber: Scalars['String']['output'];
};

export type Restaurant = {
  __typename?: 'Restaurant';
  customerFavorites?: Maybe<Scalars['String']['output']>;
  description: Scalars['String']['output'];
  location: Location;
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos: Photos;
  primaryTypeName: Scalars['String']['output'];
  rating: Scalars['Float']['output'];
  reservable: Scalars['Boolean']['output'];
  source: RestaurantSource;
  sourceId: Scalars['String']['output'];
  websiteUri?: Maybe<Scalars['String']['output']>;
};

export type RestaurantCategory = {
  __typename?: 'RestaurantCategory';
  id: Scalars['UUID']['output'];
  isDefault: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
};

export enum RestaurantSource {
  GooglePlaces = 'GOOGLE_PLACES'
}

export type SearchRegion = {
  __typename?: 'SearchRegion';
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
};

export type SubmitReserverDetailsFailure = {
  __typename?: 'SubmitReserverDetailsFailure';
  failureReason: SubmitReserverDetailsFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum SubmitReserverDetailsFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type SubmitReserverDetailsInput = {
  firstName: Scalars['String']['input'];
  lastName: Scalars['String']['input'];
  phoneNumber: Scalars['String']['input'];
};

export type SubmitReserverDetailsResult = SubmitReserverDetailsFailure | SubmitReserverDetailsSuccess;

export type SubmitReserverDetailsSuccess = {
  __typename?: 'SubmitReserverDetailsSuccess';
  reserverDetails: ReserverDetails;
};

export type Survey = {
  __typename?: 'Survey';
  budget: OutingBudget;
  headcount: Scalars['Int']['output'];
  id: Scalars['UUID']['output'];
  searchRegions: Array<SearchRegion>;
  startTime: Scalars['DateTime']['output'];
};

export type TicketInfo = {
  __typename?: 'TicketInfo';
  costBreakdown: CostBreakdown;
  name?: Maybe<Scalars['String']['output']>;
  notes?: Maybe<Scalars['String']['output']>;
};

export type UnauthenticatedViewer = {
  __typename?: 'UnauthenticatedViewer';
  /** @deprecated Use authFailureReason */
  authAction: ViewerAuthenticationAction;
  authFailureReason: AuthenticationFailureReason;
};

export type UpdateAccountFailure = {
  __typename?: 'UpdateAccountFailure';
  failureReason: UpdateAccountFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateAccountFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS',
  WeakPassword = 'WEAK_PASSWORD'
}

export type UpdateAccountInput = {
  email?: InputMaybe<Scalars['String']['input']>;
  plaintextPassword?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateAccountResult = UpdateAccountFailure | UpdateAccountSuccess;

export type UpdateAccountSuccess = {
  __typename?: 'UpdateAccountSuccess';
  account: Account;
};

export type UpdateBookingFailure = {
  __typename?: 'UpdateBookingFailure';
  failureReason: UpdateBookingFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateBookingFailureReason {
  BookingNotFound = 'BOOKING_NOT_FOUND',
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdateBookingInput = {
  bookingId: Scalars['UUID']['input'];
  reserverDetailsId?: InputMaybe<Scalars['UUID']['input']>;
};

export type UpdateBookingResult = UpdateBookingFailure | UpdateBookingSuccess;

export type UpdateBookingSuccess = {
  __typename?: 'UpdateBookingSuccess';
  booking: Booking;
};

export type UpdateOutingPreferencesFailure = {
  __typename?: 'UpdateOutingPreferencesFailure';
  failureReason: UpdateOutingPreferencesFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateOutingPreferencesFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdateOutingPreferencesInput = {
  activityCategoryIds?: InputMaybe<Array<Scalars['UUID']['input']>>;
  restaurantCategoryIds?: InputMaybe<Array<Scalars['UUID']['input']>>;
};

export type UpdateOutingPreferencesResult = UpdateOutingPreferencesFailure | UpdateOutingPreferencesSuccess;

export type UpdateOutingPreferencesSuccess = {
  __typename?: 'UpdateOutingPreferencesSuccess';
  outingPreferences: OutingPreferences;
};

export type UpdateReserverDetailsAccountFailure = {
  __typename?: 'UpdateReserverDetailsAccountFailure';
  failureReason: UpdateReserverDetailsAccountFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateReserverDetailsAccountFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdateReserverDetailsAccountInput = {
  email: Scalars['String']['input'];
  firstName: Scalars['String']['input'];
  id: Scalars['UUID']['input'];
  lastName: Scalars['String']['input'];
  phoneNumber: Scalars['String']['input'];
};

export type UpdateReserverDetailsAccountResult = UpdateReserverDetailsAccountFailure | UpdateReserverDetailsAccountSuccess;

export type UpdateReserverDetailsAccountSuccess = {
  __typename?: 'UpdateReserverDetailsAccountSuccess';
  account: Account;
  reserverDetails: ReserverDetails;
};

export type UpdateReserverDetailsFailure = {
  __typename?: 'UpdateReserverDetailsFailure';
  failureReason: UpdateReserverDetailsFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateReserverDetailsFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdateReserverDetailsInput = {
  firstName: Scalars['String']['input'];
  id: Scalars['UUID']['input'];
  lastName: Scalars['String']['input'];
  phoneNumber: Scalars['String']['input'];
};

export type UpdateReserverDetailsResult = UpdateReserverDetailsFailure | UpdateReserverDetailsSuccess;

export type UpdateReserverDetailsSuccess = {
  __typename?: 'UpdateReserverDetailsSuccess';
  reserverDetails: ReserverDetails;
};

export type ValidationError = {
  __typename?: 'ValidationError';
  field: Scalars['String']['output'];
  subject: Scalars['String']['output'];
};

export enum ViewerAuthenticationAction {
  ForceLogout = 'FORCE_LOGOUT',
  RefreshAccessToken = 'REFRESH_ACCESS_TOKEN'
}

export type ViewerMutations = AuthenticatedViewerMutations | UnauthenticatedViewer;

export type ViewerQueries = AuthenticatedViewerQueries | UnauthenticatedViewer;

export type AddressFieldsFragment = { __typename: 'Address', address1?: string | null, address2?: string | null, city?: string | null, state?: string | null, zipCode?: string | null, country?: string | null, formattedMultiline: string, formattedSingleline: string };

export type BookingDetailsFieldsFragment = { __typename: 'BookingDetails', id: string, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, survey?: { __typename: 'Survey', id: string, budget: OutingBudget, headcount: number, startTime: string, searchRegions: Array<{ __typename: 'SearchRegion', id: string, name: string }> } | null, costBreakdown: { __typename: 'CostBreakdown', baseCostCents: number, feeCents: number, taxCents: number, totalCostCents: number }, activity?: { __typename: 'Activity', sourceId: string, source: ActivitySource, name: string, description?: string | null, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, categoryGroup?: { __typename: 'ActivityCategoryGroup', id: string, name: string, activityCategories: Array<{ __typename: 'ActivityCategory', id: string, name: string, isDefault: boolean }> } | null, ticketInfo?: { __typename: 'TicketInfo', name?: string | null, notes?: string | null, costBreakdown: { __typename: 'CostBreakdown', baseCostCents: number, feeCents: number, taxCents: number, totalCostCents: number } } | null, venue: { __typename: 'ActivityVenue', name: string, location: { __typename: 'Location', directionsUri?: string | null, coordinates: { __typename: 'GeoPoint', lat: number, lon: number }, address: { __typename: 'Address', address1?: string | null, address2?: string | null, city?: string | null, state?: string | null, zipCode?: string | null, country?: string | null, formattedMultiline: string, formattedSingleline: string }, searchRegion: { __typename: 'SearchRegion', id: string, name: string } } }, photos: { __typename: 'Photos', coverPhoto?: { __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> } | null, supplementalPhotos: Array<{ __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> }> } } | null, restaurant?: { __typename: 'Restaurant', sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { __typename: 'Location', directionsUri?: string | null, coordinates: { __typename: 'GeoPoint', lat: number, lon: number }, address: { __typename: 'Address', address1?: string | null, address2?: string | null, city?: string | null, state?: string | null, zipCode?: string | null, country?: string | null, formattedMultiline: string, formattedSingleline: string }, searchRegion: { __typename: 'SearchRegion', id: string, name: string } }, photos: { __typename: 'Photos', coverPhoto?: { __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> } | null, supplementalPhotos: Array<{ __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> }> } } | null };

export type BookingFieldsFragment = { __typename: 'Booking', id: string, state: BookingState, reserverDetails?: { __typename: 'ReserverDetails', id: string, firstName: string, lastName: string, phoneNumber: string } | null };

export type CostBreakdownFieldsFragment = { __typename: 'CostBreakdown', baseCostCents: number, feeCents: number, taxCents: number, totalCostCents: number };

export type LocationFieldsFragment = { __typename: 'Location', directionsUri?: string | null, coordinates: { __typename: 'GeoPoint', lat: number, lon: number }, address: { __typename: 'Address', address1?: string | null, address2?: string | null, city?: string | null, state?: string | null, zipCode?: string | null, country?: string | null, formattedMultiline: string, formattedSingleline: string }, searchRegion: { __typename: 'SearchRegion', id: string, name: string } };

export type PhotoFieldsFragment = { __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> };

export type UpdateBookingMutationVariables = Exact<{
  input: UpdateBookingInput;
}>;


export type UpdateBookingMutation = { __typename: 'Mutation', viewer: { __typename: 'AuthenticatedViewerMutations', updateBooking: { __typename: 'UpdateBookingFailure', failureReason: UpdateBookingFailureReason, validationErrors?: Array<{ __typename: 'ValidationError', field: string }> | null } | { __typename: 'UpdateBookingSuccess', booking: { __typename: 'Booking', id: string, state: BookingState, reserverDetails?: { __typename: 'ReserverDetails', id: string, firstName: string, lastName: string, phoneNumber: string } | null } } } | { __typename: 'UnauthenticatedViewer', authFailureReason: AuthenticationFailureReason } };

export type UpdateReserverDetailsMutationVariables = Exact<{
  input: UpdateReserverDetailsInput;
}>;


export type UpdateReserverDetailsMutation = { __typename: 'Mutation', viewer: { __typename: 'AuthenticatedViewerMutations', updateReserverDetails: { __typename: 'UpdateReserverDetailsFailure', failureReason: UpdateReserverDetailsFailureReason, validationErrors?: Array<{ __typename: 'ValidationError', field: string }> | null } | { __typename: 'UpdateReserverDetailsSuccess', reserverDetails: { __typename: 'ReserverDetails', id: string, firstName: string, lastName: string, phoneNumber: string } } } | { __typename: 'UnauthenticatedViewer', authFailureReason: AuthenticationFailureReason } };

export type BookingDetailsQueryVariables = Exact<{
  input: GetBookingDetailsQueryInput;
}>;


export type BookingDetailsQuery = { __typename: 'Query', viewer: { __typename: 'AuthenticatedViewerQueries', bookedOutingDetails: { __typename: 'BookingDetails', id: string, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, survey?: { __typename: 'Survey', id: string, budget: OutingBudget, headcount: number, startTime: string, searchRegions: Array<{ __typename: 'SearchRegion', id: string, name: string }> } | null, costBreakdown: { __typename: 'CostBreakdown', baseCostCents: number, feeCents: number, taxCents: number, totalCostCents: number }, activity?: { __typename: 'Activity', sourceId: string, source: ActivitySource, name: string, description?: string | null, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, categoryGroup?: { __typename: 'ActivityCategoryGroup', id: string, name: string, activityCategories: Array<{ __typename: 'ActivityCategory', id: string, name: string, isDefault: boolean }> } | null, ticketInfo?: { __typename: 'TicketInfo', name?: string | null, notes?: string | null, costBreakdown: { __typename: 'CostBreakdown', baseCostCents: number, feeCents: number, taxCents: number, totalCostCents: number } } | null, venue: { __typename: 'ActivityVenue', name: string, location: { __typename: 'Location', directionsUri?: string | null, coordinates: { __typename: 'GeoPoint', lat: number, lon: number }, address: { __typename: 'Address', address1?: string | null, address2?: string | null, city?: string | null, state?: string | null, zipCode?: string | null, country?: string | null, formattedMultiline: string, formattedSingleline: string }, searchRegion: { __typename: 'SearchRegion', id: string, name: string } } }, photos: { __typename: 'Photos', coverPhoto?: { __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> } | null, supplementalPhotos: Array<{ __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> }> } } | null, restaurant?: { __typename: 'Restaurant', sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { __typename: 'Location', directionsUri?: string | null, coordinates: { __typename: 'GeoPoint', lat: number, lon: number }, address: { __typename: 'Address', address1?: string | null, address2?: string | null, city?: string | null, state?: string | null, zipCode?: string | null, country?: string | null, formattedMultiline: string, formattedSingleline: string }, searchRegion: { __typename: 'SearchRegion', id: string, name: string } }, photos: { __typename: 'Photos', coverPhoto?: { __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> } | null, supplementalPhotos: Array<{ __typename: 'Photo', id: string, src: string, alt?: string | null, attributions: Array<string> }> } } | null } } | { __typename: 'UnauthenticatedViewer', authFailureReason: AuthenticationFailureReason } };

export type ListBookedOutingsQueryVariables = Exact<{ [key: string]: never; }>;


export type ListBookedOutingsQuery = { __typename: 'Query', viewer: { __typename: 'AuthenticatedViewerQueries', bookedOutings: Array<{ __typename: 'BookingDetailPeek', id: string, activityStartTime?: string | null, restaurantArrivalTime?: string | null, activityName?: string | null, restaurantName?: string | null, photoUri?: string | null, state: BookingState }> } | { __typename: 'UnauthenticatedViewer', authFailureReason: AuthenticationFailureReason } };

export type ListReserverDetailsQueryVariables = Exact<{ [key: string]: never; }>;


export type ListReserverDetailsQuery = { __typename: 'Query', viewer: { __typename: 'AuthenticatedViewerQueries', reserverDetails: Array<{ __typename: 'ReserverDetails', id: string, firstName: string, lastName: string, phoneNumber: string }> } | { __typename: 'UnauthenticatedViewer', authFailureReason: AuthenticationFailureReason } };

export class TypedDocumentString<TResult, TVariables>
  extends String
  implements DocumentTypeDecoration<TResult, TVariables>
{
  __apiType?: DocumentTypeDecoration<TResult, TVariables>['__apiType'];

  constructor(private value: string, public __meta__?: Record<string, any> | undefined) {
    super(value);
  }

  toString(): string & DocumentTypeDecoration<TResult, TVariables> {
    return this.value;
  }
}
export const CostBreakdownFieldsFragmentDoc = new TypedDocumentString(`
    fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
    `, {"fragmentName":"CostBreakdownFields"}) as unknown as TypedDocumentString<CostBreakdownFieldsFragment, unknown>;
export const AddressFieldsFragmentDoc = new TypedDocumentString(`
    fragment AddressFields on Address {
  __typename
  address1
  address2
  city
  state
  zipCode
  country
  formattedMultiline
  formattedSingleline
}
    `, {"fragmentName":"AddressFields"}) as unknown as TypedDocumentString<AddressFieldsFragment, unknown>;
export const LocationFieldsFragmentDoc = new TypedDocumentString(`
    fragment LocationFields on Location {
  __typename
  directionsUri
  coordinates {
    __typename
    lat
    lon
  }
  address {
    __typename
    ...AddressFields
  }
  searchRegion {
    __typename
    id
    name
  }
}
    fragment AddressFields on Address {
  __typename
  address1
  address2
  city
  state
  zipCode
  country
  formattedMultiline
  formattedSingleline
}`, {"fragmentName":"LocationFields"}) as unknown as TypedDocumentString<LocationFieldsFragment, unknown>;
export const PhotoFieldsFragmentDoc = new TypedDocumentString(`
    fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
    `, {"fragmentName":"PhotoFields"}) as unknown as TypedDocumentString<PhotoFieldsFragment, unknown>;
export const BookingDetailsFieldsFragmentDoc = new TypedDocumentString(`
    fragment BookingDetailsFields on BookingDetails {
  __typename
  id
  activityStartTime
  restaurantArrivalTime
  survey {
    __typename
    id
    budget
    headcount
    searchRegions {
      __typename
      id
      name
    }
    startTime
  }
  drivingTime
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    categoryGroup {
      __typename
      id
      name
      activityCategories {
        __typename
        id
        name
        isDefault
      }
    }
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    ticketInfo {
      __typename
      name
      notes
      costBreakdown {
        __typename
        ...CostBreakdownFields
      }
    }
    venue {
      __typename
      name
      location {
        __typename
        ...LocationFields
      }
    }
    photos {
      __typename
      coverPhoto {
        __typename
        ...PhotoFields
      }
      supplementalPhotos {
        __typename
        ...PhotoFields
      }
    }
  }
  restaurant {
    __typename
    sourceId
    source
    name
    reservable
    rating
    primaryTypeName
    websiteUri
    description
    parkingTips
    customerFavorites
    location {
      __typename
      ...LocationFields
    }
    photos {
      __typename
      coverPhoto {
        __typename
        ...PhotoFields
      }
      supplementalPhotos {
        __typename
        ...PhotoFields
      }
    }
  }
}
    fragment AddressFields on Address {
  __typename
  address1
  address2
  city
  state
  zipCode
  country
  formattedMultiline
  formattedSingleline
}
fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
fragment LocationFields on Location {
  __typename
  directionsUri
  coordinates {
    __typename
    lat
    lon
  }
  address {
    __typename
    ...AddressFields
  }
  searchRegion {
    __typename
    id
    name
  }
}
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}`, {"fragmentName":"BookingDetailsFields"}) as unknown as TypedDocumentString<BookingDetailsFieldsFragment, unknown>;
export const BookingFieldsFragmentDoc = new TypedDocumentString(`
    fragment BookingFields on Booking {
  __typename
  id
  state
  reserverDetails {
    __typename
    id
    firstName
    lastName
    phoneNumber
  }
}
    `, {"fragmentName":"BookingFields"}) as unknown as TypedDocumentString<BookingFieldsFragment, unknown>;
export const UpdateBookingDocument = new TypedDocumentString(`
    mutation UpdateBooking($input: UpdateBookingInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      updateBooking(input: $input) {
        __typename
        ... on UpdateBookingSuccess {
          __typename
          booking {
            __typename
            ...BookingFields
          }
        }
        ... on UpdateBookingFailure {
          __typename
          failureReason
          validationErrors {
            __typename
            field
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment BookingFields on Booking {
  __typename
  id
  state
  reserverDetails {
    __typename
    id
    firstName
    lastName
    phoneNumber
  }
}`) as unknown as TypedDocumentString<UpdateBookingMutation, UpdateBookingMutationVariables>;
export const UpdateReserverDetailsDocument = new TypedDocumentString(`
    mutation UpdateReserverDetails($input: UpdateReserverDetailsInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      updateReserverDetails(input: $input) {
        __typename
        ... on UpdateReserverDetailsSuccess {
          __typename
          reserverDetails {
            __typename
            id
            firstName
            lastName
            phoneNumber
          }
        }
        ... on UpdateReserverDetailsFailure {
          __typename
          failureReason
          validationErrors {
            __typename
            field
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    `) as unknown as TypedDocumentString<UpdateReserverDetailsMutation, UpdateReserverDetailsMutationVariables>;
export const BookingDetailsDocument = new TypedDocumentString(`
    query BookingDetails($input: GetBookingDetailsQueryInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      bookedOutingDetails(input: $input) {
        __typename
        ...BookingDetailsFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment AddressFields on Address {
  __typename
  address1
  address2
  city
  state
  zipCode
  country
  formattedMultiline
  formattedSingleline
}
fragment BookingDetailsFields on BookingDetails {
  __typename
  id
  activityStartTime
  restaurantArrivalTime
  survey {
    __typename
    id
    budget
    headcount
    searchRegions {
      __typename
      id
      name
    }
    startTime
  }
  drivingTime
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    categoryGroup {
      __typename
      id
      name
      activityCategories {
        __typename
        id
        name
        isDefault
      }
    }
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    ticketInfo {
      __typename
      name
      notes
      costBreakdown {
        __typename
        ...CostBreakdownFields
      }
    }
    venue {
      __typename
      name
      location {
        __typename
        ...LocationFields
      }
    }
    photos {
      __typename
      coverPhoto {
        __typename
        ...PhotoFields
      }
      supplementalPhotos {
        __typename
        ...PhotoFields
      }
    }
  }
  restaurant {
    __typename
    sourceId
    source
    name
    reservable
    rating
    primaryTypeName
    websiteUri
    description
    parkingTips
    customerFavorites
    location {
      __typename
      ...LocationFields
    }
    photos {
      __typename
      coverPhoto {
        __typename
        ...PhotoFields
      }
      supplementalPhotos {
        __typename
        ...PhotoFields
      }
    }
  }
}
fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
fragment LocationFields on Location {
  __typename
  directionsUri
  coordinates {
    __typename
    lat
    lon
  }
  address {
    __typename
    ...AddressFields
  }
  searchRegion {
    __typename
    id
    name
  }
}
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}`) as unknown as TypedDocumentString<BookingDetailsQuery, BookingDetailsQueryVariables>;
export const ListBookedOutingsDocument = new TypedDocumentString(`
    query ListBookedOutings {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      bookedOutings {
        __typename
        id
        activityStartTime
        restaurantArrivalTime
        activityName
        restaurantName
        photoUri
        state
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    `) as unknown as TypedDocumentString<ListBookedOutingsQuery, ListBookedOutingsQueryVariables>;
export const ListReserverDetailsDocument = new TypedDocumentString(`
    query ListReserverDetails {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      reserverDetails {
        __typename
        id
        firstName
        lastName
        phoneNumber
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    `) as unknown as TypedDocumentString<ListReserverDetailsQuery, ListReserverDetailsQueryVariables>;