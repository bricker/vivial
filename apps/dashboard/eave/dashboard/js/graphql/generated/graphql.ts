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
  email: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
};

export type Activity = {
  description: Scalars['String']['output'];
  doorTips?: Maybe<Scalars['String']['output']>;
  insiderTips?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos?: Maybe<Photos>;
  source: ActivitySource;
  sourceId: Scalars['String']['output'];
  ticketInfo?: Maybe<ActivityTicketInfo>;
  venue: ActivityVenue;
  websiteUri?: Maybe<Scalars['String']['output']>;
};

export type ActivityCategory = {
  id: Scalars['UUID']['output'];
  isDefault: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
};

export type ActivityCategoryGroup = {
  activityCategories: Array<ActivityCategory>;
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
};

export enum ActivitySource {
  Eventbrite = 'EVENTBRITE',
  GooglePlaces = 'GOOGLE_PLACES',
  Internal = 'INTERNAL'
}

export type ActivityTicketInfo = {
  cost?: Maybe<Scalars['Int']['output']>;
  fee?: Maybe<Scalars['Int']['output']>;
  notes?: Maybe<Scalars['String']['output']>;
  tax?: Maybe<Scalars['Int']['output']>;
  type?: Maybe<Scalars['String']['output']>;
};

export type ActivityVenue = {
  location: Location;
  name: Scalars['String']['output'];
};

export type AuthenticatedViewerMutations = {
  createBooking: CreateBookingResult;
  createPaymentIntent: CreatePaymentIntentResult;
  planOuting: PlanOutingResult;
  replanOuting: ReplanOutingResult;
  submitReserverDetails: SubmitReserverDetailsResult;
  updateAccount: UpdateAccountResult;
  updateOutingPreferences: UpdateOutingPreferencesResult;
  updatePreferences: UpdateOutingPreferencesResult;
  updateReserverDetailsAccount: UpdateReserverDetailsAccountResult;
};


export type AuthenticatedViewerMutationsCreateBookingArgs = {
  input: CreateBookingInput;
};


export type AuthenticatedViewerMutationsPlanOutingArgs = {
  input: PlanOutingInput;
};


export type AuthenticatedViewerMutationsReplanOutingArgs = {
  input: ReplanOutingInput;
};


export type AuthenticatedViewerMutationsSubmitReserverDetailsArgs = {
  input: SubmitReserverDetailsInput;
};


export type AuthenticatedViewerMutationsUpdateAccountArgs = {
  input: UpdateAccountInput;
};


export type AuthenticatedViewerMutationsUpdateOutingPreferencesArgs = {
  input: UpdateOutingPreferencesInput;
};


export type AuthenticatedViewerMutationsUpdatePreferencesArgs = {
  input: UpdateOutingPreferencesInput;
};


export type AuthenticatedViewerMutationsUpdateReserverDetailsAccountArgs = {
  input: UpdateReserverDetailsAccountInput;
};

export type AuthenticatedViewerQueries = {
  bookedOutings: Array<Outing>;
  outing: Outing;
  outingPreferences: OutingPreferences;
  reserverDetails: Array<ReserverDetails>;
};


export type AuthenticatedViewerQueriesBookedOutingsArgs = {
  input?: InputMaybe<ListBookedOutingsInput>;
};


export type AuthenticatedViewerQueriesOutingArgs = {
  outingId: Scalars['UUID']['input'];
};

export type Booking = {
  id: Scalars['UUID']['output'];
  reserverDetailsId: Scalars['UUID']['output'];
};

export type CreateAccountFailure = {
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
  account: Account;
};

export type CreateBookingFailure = {
  failureReason: CreateBookingFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum CreateBookingFailureReason {
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON',
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type CreateBookingInput = {
  outingId: Scalars['UUID']['input'];
  reserverDetailsId: Scalars['UUID']['input'];
};

export type CreateBookingResult = CreateBookingFailure | CreateBookingSuccess;

export type CreateBookingSuccess = {
  booking: Booking;
};

export type CreatePaymentIntentFailure = {
  failureReason: CreatePaymentIntentFailureReason;
};

export enum CreatePaymentIntentFailureReason {
  PaymentIntentFailed = 'PAYMENT_INTENT_FAILED',
  Unknown = 'UNKNOWN'
}

export type CreatePaymentIntentResult = CreatePaymentIntentFailure | CreatePaymentIntentSuccess;

export type CreatePaymentIntentSuccess = {
  paymentIntent: PaymentIntent;
};

export type ListBookedOutingsInput = {
  outingState: OutingState;
};

export type Location = {
  directionsUri?: Maybe<Scalars['String']['output']>;
  formattedAddress: Scalars['String']['output'];
  latitude: Scalars['Float']['output'];
  longitude: Scalars['Float']['output'];
};

export type LoginFailure = {
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
  account: Account;
};

export type Mutation = {
  createAccount: CreateAccountResult;
  login: LoginResult;
  planOuting: PlanOutingResult;
  replanOuting: ReplanOutingResult;
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


export type MutationReplanOutingArgs = {
  input: ReplanOutingInput;
};

export type Outing = {
  activity?: Maybe<Activity>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  drivingTime?: Maybe<Scalars['String']['output']>;
  headcount: Scalars['Int']['output'];
  id: Scalars['UUID']['output'];
  restaurant?: Maybe<Restaurant>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
};

export enum OutingBudget {
  Expensive = 'EXPENSIVE',
  Free = 'FREE',
  Inexpensive = 'INEXPENSIVE',
  Moderate = 'MODERATE',
  VeryExpensive = 'VERY_EXPENSIVE'
}

export type OutingPreferences = {
  activityCategories?: Maybe<Array<ActivityCategory>>;
  restaurantCategories?: Maybe<Array<RestaurantCategory>>;
};

export type OutingPreferencesInput = {
  activityCategoryIds: Array<Scalars['UUID']['input']>;
  restaurantCategoryIds: Array<Scalars['UUID']['input']>;
};

export enum OutingState {
  Future = 'FUTURE',
  Past = 'PAST'
}

export type PaymentIntent = {
  clientSecret: Scalars['String']['output'];
};

export type Photos = {
  coverPhotoUri: Scalars['String']['output'];
  supplementalPhotoUris?: Maybe<Array<Scalars['String']['output']>>;
};

export type PlanOutingFailure = {
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
  visitorId: Scalars['UUID']['input'];
};

export type PlanOutingResult = PlanOutingFailure | PlanOutingSuccess;

export type PlanOutingSuccess = {
  outing: Outing;
};

export type Query = {
  activityCategoryGroups: Array<ActivityCategoryGroup>;
  restaurantCategories: Array<RestaurantCategory>;
  searchRegions: Array<SearchRegion>;
  viewer: ViewerQueries;
};

export type ReplanOutingFailure = {
  failureReason: ReplanOutingFailureReason;
};

export enum ReplanOutingFailureReason {
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type ReplanOutingInput = {
  groupPreferences: Array<OutingPreferencesInput>;
  outingId: Scalars['UUID']['input'];
  visitorId: Scalars['UUID']['input'];
};

export type ReplanOutingResult = ReplanOutingFailure | ReplanOutingSuccess;

export type ReplanOutingSuccess = {
  outing: Outing;
};

export type ReserverDetails = {
  accountId: Scalars['UUID']['output'];
  firstName: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  lastName: Scalars['String']['output'];
  phoneNumber: Scalars['String']['output'];
};

export type Restaurant = {
  customerFavorites?: Maybe<Scalars['String']['output']>;
  description: Scalars['String']['output'];
  location: Location;
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos?: Maybe<Photos>;
  primaryTypeName: Scalars['String']['output'];
  rating: Scalars['Float']['output'];
  reservable: Scalars['Boolean']['output'];
  source: RestaurantSource;
  sourceId: Scalars['String']['output'];
  websiteUri?: Maybe<Scalars['String']['output']>;
};

export type RestaurantCategory = {
  id: Scalars['UUID']['output'];
  isDefault: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
};

export enum RestaurantSource {
  GooglePlaces = 'GOOGLE_PLACES'
}

export type SearchRegion = {
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
};

export type SubmitReserverDetailsFailure = {
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
  reserverDetails: ReserverDetails;
};

export type UnauthenticatedViewer = {
  authAction: ViewerAuthenticationAction;
};

export type UpdateAccountFailure = {
  failureReason: UpdateAccountFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateAccountFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS',
  WeakPassword = 'WEAK_PASSWORD'
}

export type UpdateAccountInput = {
  email: Scalars['String']['input'];
  plaintextPassword: Scalars['String']['input'];
};

export type UpdateAccountResult = UpdateAccountFailure | UpdateAccountSuccess;

export type UpdateAccountSuccess = {
  account: Account;
};

export type UpdateOutingPreferencesFailure = {
  failureReason: UpdateOutingPreferencesFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateOutingPreferencesFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdateOutingPreferencesInput = {
  activityCategoryIds: Array<Scalars['UUID']['input']>;
  restaurantCategoryIds: Array<Scalars['UUID']['input']>;
};

export type UpdateOutingPreferencesResult = UpdateOutingPreferencesFailure | UpdateOutingPreferencesSuccess;

export type UpdateOutingPreferencesSuccess = {
  outingPreferences: OutingPreferences;
};

export type UpdateReserverDetailsAccountFailure = {
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
  account: Account;
  reserverDetails: ReserverDetails;
};

export type ValidationError = {
  field: Scalars['String']['output'];
};

export enum ViewerAuthenticationAction {
  ForceLogout = 'FORCE_LOGOUT',
  RefreshAccessToken = 'REFRESH_ACCESS_TOKEN'
}

export type ViewerMutations = AuthenticatedViewerMutations | UnauthenticatedViewer;

export type ViewerQueries = AuthenticatedViewerQueries | UnauthenticatedViewer;

export type OutingFieldsFragment = { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null };

type PlanOutingFields_PlanOutingFailure_Fragment = { failureReason: PlanOutingFailureReason };

type PlanOutingFields_PlanOutingSuccess_Fragment = { outing: { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null } };

export type PlanOutingFieldsFragment = PlanOutingFields_PlanOutingFailure_Fragment | PlanOutingFields_PlanOutingSuccess_Fragment;

type ReplanOutingFields_ReplanOutingFailure_Fragment = { failureReason: ReplanOutingFailureReason };

type ReplanOutingFields_ReplanOutingSuccess_Fragment = { outing: { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null } };

export type ReplanOutingFieldsFragment = ReplanOutingFields_ReplanOutingFailure_Fragment | ReplanOutingFields_ReplanOutingSuccess_Fragment;

export type CreateAccountMutationVariables = Exact<{
  input: CreateAccountInput;
}>;


export type CreateAccountMutation = { createAccount: { __typename: 'CreateAccountFailure', failureReason: CreateAccountFailureReason, validationErrors?: Array<{ field: string }> | null } | { __typename: 'CreateAccountSuccess', account: { id: string, email: string } } };

export type CreateBookingMutationVariables = Exact<{
  input: CreateBookingInput;
}>;


export type CreateBookingMutation = { viewer: { __typename: 'AuthenticatedViewerMutations', createBooking: { __typename: 'CreateBookingFailure', failureReason: CreateBookingFailureReason, validationErrors?: Array<{ field: string }> | null } | { __typename: 'CreateBookingSuccess', booking: { id: string } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type CreatePaymentIntentMutationVariables = Exact<{ [key: string]: never; }>;


export type CreatePaymentIntentMutation = { viewer: { __typename: 'AuthenticatedViewerMutations', createPaymentIntent: { __typename: 'CreatePaymentIntentFailure', failureReason: CreatePaymentIntentFailureReason } | { __typename: 'CreatePaymentIntentSuccess', paymentIntent: { clientSecret: string } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type LoginMutationVariables = Exact<{
  input: LoginInput;
}>;


export type LoginMutation = { login: { __typename: 'LoginFailure', failureReason: LoginFailureReason } | { __typename: 'LoginSuccess', account: { id: string, email: string } } };

export type PlanOutingAuthenticatedMutationVariables = Exact<{
  input: PlanOutingInput;
}>;


export type PlanOutingAuthenticatedMutation = { viewer: { planOuting: { failureReason: PlanOutingFailureReason } | { outing: { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type PlanOutingUnauthenticatedMutationVariables = Exact<{
  input: PlanOutingInput;
}>;


export type PlanOutingUnauthenticatedMutation = { planOuting: { failureReason: PlanOutingFailureReason } | { outing: { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null } } };

export type ReplanOutingAuthenticatedMutationVariables = Exact<{
  input: ReplanOutingInput;
}>;


export type ReplanOutingAuthenticatedMutation = { viewer: { replanOuting: { failureReason: ReplanOutingFailureReason } | { outing: { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type ReplanOutingUnauthenticatedMutationVariables = Exact<{
  input: ReplanOutingInput;
}>;


export type ReplanOutingUnauthenticatedMutation = { replanOuting: { failureReason: ReplanOutingFailureReason } | { outing: { id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null } } };

export type SubmitReserverDetailsMutationVariables = Exact<{
  input: SubmitReserverDetailsInput;
}>;


export type SubmitReserverDetailsMutation = { viewer: { __typename: 'AuthenticatedViewerMutations', submitReserverDetails: { __typename: 'SubmitReserverDetailsFailure', failureReason: SubmitReserverDetailsFailureReason, validationErrors?: Array<{ field: string }> | null } | { __typename: 'SubmitReserverDetailsSuccess', reserverDetails: { id: string } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type UpdateAccountMutationVariables = Exact<{
  input: UpdateAccountInput;
}>;


export type UpdateAccountMutation = { viewer: { __typename: 'AuthenticatedViewerMutations', updateAccount: { __typename: 'UpdateAccountFailure', failureReason: UpdateAccountFailureReason, validationErrors?: Array<{ field: string }> | null } | { __typename: 'UpdateAccountSuccess', account: { email: string } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type UpdateReserverDetailsAccountMutationVariables = Exact<{
  input: UpdateReserverDetailsAccountInput;
}>;


export type UpdateReserverDetailsAccountMutation = { viewer: { __typename: 'AuthenticatedViewerMutations', updateReserverDetailsAccount: { __typename: 'UpdateReserverDetailsAccountFailure', failureReason: UpdateReserverDetailsAccountFailureReason, validationErrors?: Array<{ field: string }> | null } | { __typename: 'UpdateReserverDetailsAccountSuccess', reserverDetails: { id: string, firstName: string, lastName: string, phoneNumber: string }, account: { id: string, email: string } } } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type ListBookedOutingsQueryVariables = Exact<{
  input?: InputMaybe<ListBookedOutingsInput>;
}>;


export type ListBookedOutingsQuery = { viewer: { __typename: 'AuthenticatedViewerQueries', bookedOutings: Array<{ id: string, headcount: number, activityStartTime?: string | null, restaurantArrivalTime?: string | null, drivingTime?: string | null, activity?: { sourceId: string, source: ActivitySource, name: string, description: string, websiteUri?: string | null, doorTips?: string | null, insiderTips?: string | null, parkingTips?: string | null, venue: { name: string, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string } }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null, ticketInfo?: { type?: string | null, notes?: string | null, cost?: number | null, fee?: number | null, tax?: number | null } | null } | null, restaurant?: { sourceId: string, source: RestaurantSource, name: string, reservable: boolean, rating: number, primaryTypeName: string, websiteUri?: string | null, description: string, parkingTips?: string | null, customerFavorites?: string | null, location: { directionsUri?: string | null, latitude: number, longitude: number, formattedAddress: string }, photos?: { coverPhotoUri: string, supplementalPhotoUris?: Array<string> | null } | null } | null }> } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type ListReserverDetailsQueryVariables = Exact<{ [key: string]: never; }>;


export type ListReserverDetailsQuery = { viewer: { __typename: 'AuthenticatedViewerQueries', reserverDetails: Array<{ id: string, firstName: string, lastName: string, phoneNumber: string }> } | { __typename: 'UnauthenticatedViewer', authAction: ViewerAuthenticationAction } };

export type SearchRegionsQueryVariables = Exact<{ [key: string]: never; }>;


export type SearchRegionsQuery = { searchRegions: Array<{ id: string, name: string }> };

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
export const OutingFieldsFragmentDoc = new TypedDocumentString(`
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}
    `, {"fragmentName":"OutingFields"}) as unknown as TypedDocumentString<OutingFieldsFragment, unknown>;
export const PlanOutingFieldsFragmentDoc = new TypedDocumentString(`
    fragment PlanOutingFields on PlanOutingResult {
  ... on PlanOutingSuccess {
    outing {
      ...OutingFields
    }
  }
  ... on PlanOutingFailure {
    failureReason
  }
}
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}`, {"fragmentName":"PlanOutingFields"}) as unknown as TypedDocumentString<PlanOutingFieldsFragment, unknown>;
export const ReplanOutingFieldsFragmentDoc = new TypedDocumentString(`
    fragment ReplanOutingFields on ReplanOutingResult {
  ... on ReplanOutingSuccess {
    outing {
      ...OutingFields
    }
  }
  ... on ReplanOutingFailure {
    failureReason
  }
}
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}`, {"fragmentName":"ReplanOutingFields"}) as unknown as TypedDocumentString<ReplanOutingFieldsFragment, unknown>;
export const CreateAccountDocument = new TypedDocumentString(`
    mutation CreateAccount($input: CreateAccountInput!) {
  createAccount(input: $input) {
    __typename
    ... on CreateAccountSuccess {
      __typename
      account {
        id
        email
      }
    }
    ... on CreateAccountFailure {
      __typename
      failureReason
      validationErrors {
        field
      }
    }
  }
}
    `) as unknown as TypedDocumentString<CreateAccountMutation, CreateAccountMutationVariables>;
export const CreateBookingDocument = new TypedDocumentString(`
    mutation CreateBooking($input: CreateBookingInput!) {
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      createBooking(input: $input) {
        ... on CreateBookingSuccess {
          __typename
          booking {
            id
          }
        }
        ... on CreateBookingFailure {
          __typename
          failureReason
          validationErrors {
            field
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<CreateBookingMutation, CreateBookingMutationVariables>;
export const CreatePaymentIntentDocument = new TypedDocumentString(`
    mutation CreatePaymentIntent {
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      createPaymentIntent {
        __typename
        ... on CreatePaymentIntentSuccess {
          __typename
          paymentIntent {
            clientSecret
          }
        }
        ... on CreatePaymentIntentFailure {
          __typename
          failureReason
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<CreatePaymentIntentMutation, CreatePaymentIntentMutationVariables>;
export const LoginDocument = new TypedDocumentString(`
    mutation Login($input: LoginInput!) {
  login(input: $input) {
    __typename
    ... on LoginSuccess {
      __typename
      account {
        id
        email
      }
    }
    ... on LoginFailure {
      __typename
      failureReason
    }
  }
}
    `) as unknown as TypedDocumentString<LoginMutation, LoginMutationVariables>;
export const PlanOutingAuthenticatedDocument = new TypedDocumentString(`
    mutation PlanOutingAuthenticated($input: PlanOutingInput!) {
  viewer {
    ... on AuthenticatedViewerMutations {
      planOuting(input: $input) {
        ...PlanOutingFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}
fragment PlanOutingFields on PlanOutingResult {
  ... on PlanOutingSuccess {
    outing {
      ...OutingFields
    }
  }
  ... on PlanOutingFailure {
    failureReason
  }
}`) as unknown as TypedDocumentString<PlanOutingAuthenticatedMutation, PlanOutingAuthenticatedMutationVariables>;
export const PlanOutingUnauthenticatedDocument = new TypedDocumentString(`
    mutation PlanOutingUnauthenticated($input: PlanOutingInput!) {
  planOuting(input: $input) {
    ...PlanOutingFields
  }
}
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}
fragment PlanOutingFields on PlanOutingResult {
  ... on PlanOutingSuccess {
    outing {
      ...OutingFields
    }
  }
  ... on PlanOutingFailure {
    failureReason
  }
}`) as unknown as TypedDocumentString<PlanOutingUnauthenticatedMutation, PlanOutingUnauthenticatedMutationVariables>;
export const ReplanOutingAuthenticatedDocument = new TypedDocumentString(`
    mutation ReplanOutingAuthenticated($input: ReplanOutingInput!) {
  viewer {
    ... on AuthenticatedViewerMutations {
      replanOuting(input: $input) {
        ...ReplanOutingFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}
fragment ReplanOutingFields on ReplanOutingResult {
  ... on ReplanOutingSuccess {
    outing {
      ...OutingFields
    }
  }
  ... on ReplanOutingFailure {
    failureReason
  }
}`) as unknown as TypedDocumentString<ReplanOutingAuthenticatedMutation, ReplanOutingAuthenticatedMutationVariables>;
export const ReplanOutingUnauthenticatedDocument = new TypedDocumentString(`
    mutation ReplanOutingUnauthenticated($input: ReplanOutingInput!) {
  replanOuting(input: $input) {
    ...ReplanOutingFields
  }
}
    fragment OutingFields on Outing {
  id
  headcount
  activityStartTime
  restaurantArrivalTime
  drivingTime
  activity {
    sourceId
    source
    name
    description
    websiteUri
    doorTips
    insiderTips
    parkingTips
    venue {
      name
      location {
        directionsUri
        latitude
        longitude
        formattedAddress
      }
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
    ticketInfo {
      type
      notes
      cost
      fee
      tax
    }
  }
  restaurant {
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
      directionsUri
      latitude
      longitude
      formattedAddress
    }
    photos {
      coverPhotoUri
      supplementalPhotoUris
    }
  }
}
fragment ReplanOutingFields on ReplanOutingResult {
  ... on ReplanOutingSuccess {
    outing {
      ...OutingFields
    }
  }
  ... on ReplanOutingFailure {
    failureReason
  }
}`) as unknown as TypedDocumentString<ReplanOutingUnauthenticatedMutation, ReplanOutingUnauthenticatedMutationVariables>;
export const SubmitReserverDetailsDocument = new TypedDocumentString(`
    mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      submitReserverDetails(input: $input) {
        __typename
        ... on SubmitReserverDetailsSuccess {
          __typename
          reserverDetails {
            id
          }
        }
        ... on SubmitReserverDetailsFailure {
          __typename
          failureReason
          validationErrors {
            field
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<SubmitReserverDetailsMutation, SubmitReserverDetailsMutationVariables>;
export const UpdateAccountDocument = new TypedDocumentString(`
    mutation UpdateAccount($input: UpdateAccountInput!) {
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      updateAccount(input: $input) {
        __typename
        ... on UpdateAccountSuccess {
          account {
            email
          }
        }
        ... on UpdateAccountFailure {
          failureReason
          validationErrors {
            field
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<UpdateAccountMutation, UpdateAccountMutationVariables>;
export const UpdateReserverDetailsAccountDocument = new TypedDocumentString(`
    mutation UpdateReserverDetailsAccount($input: UpdateReserverDetailsAccountInput!) {
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      updateReserverDetailsAccount(input: $input) {
        __typename
        ... on UpdateReserverDetailsAccountSuccess {
          reserverDetails {
            id
            firstName
            lastName
            phoneNumber
          }
          account {
            id
            email
          }
        }
        ... on UpdateReserverDetailsAccountFailure {
          failureReason
          validationErrors {
            field
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<UpdateReserverDetailsAccountMutation, UpdateReserverDetailsAccountMutationVariables>;
export const ListBookedOutingsDocument = new TypedDocumentString(`
    query ListBookedOutings($input: ListBookedOutingsInput) {
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      bookedOutings(input: $input) {
        id
        headcount
        activityStartTime
        restaurantArrivalTime
        drivingTime
        activity {
          sourceId
          source
          name
          description
          websiteUri
          doorTips
          insiderTips
          parkingTips
          venue {
            name
            location {
              directionsUri
              latitude
              longitude
              formattedAddress
            }
          }
          photos {
            coverPhotoUri
            supplementalPhotoUris
          }
          ticketInfo {
            type
            notes
            cost
            fee
            tax
          }
        }
        restaurant {
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
            directionsUri
            latitude
            longitude
            formattedAddress
          }
          photos {
            coverPhotoUri
            supplementalPhotoUris
          }
        }
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<ListBookedOutingsQuery, ListBookedOutingsQueryVariables>;
export const ListReserverDetailsDocument = new TypedDocumentString(`
    query ListReserverDetails {
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      reserverDetails {
        id
        firstName
        lastName
        phoneNumber
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authAction
    }
  }
}
    `) as unknown as TypedDocumentString<ListReserverDetailsQuery, ListReserverDetailsQueryVariables>;
export const SearchRegionsDocument = new TypedDocumentString(`
    query SearchRegions {
  searchRegions {
    id
    name
  }
}
    `) as unknown as TypedDocumentString<SearchRegionsQuery, SearchRegionsQueryVariables>;