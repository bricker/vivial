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
  /** Represents NULL values */
  Void: { input: null; output: null; }
};

export type Account = {
  __typename: 'Account';
  email: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
};

export type Activity = {
  __typename: 'Activity';
  description: Scalars['String']['output'];
  doorTips?: Maybe<Scalars['String']['output']>;
  id: Scalars['String']['output'];
  insiderTips?: Maybe<Scalars['String']['output']>;
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos?: Maybe<Photos>;
  source: ActivitySource;
  ticketInfo?: Maybe<ActivityTicketInfo>;
  venue: ActivityVenue;
  websiteUri?: Maybe<Scalars['String']['output']>;
};

export type ActivityCategory = {
  __typename: 'ActivityCategory';
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
  subcategories: Array<ActivitySubcategory>;
};

export enum ActivitySource {
  Eventbrite = 'EVENTBRITE',
  GooglePlaces = 'GOOGLE_PLACES',
  Internal = 'INTERNAL'
}

export type ActivitySubcategory = {
  __typename: 'ActivitySubcategory';
  id: Scalars['UUID']['output'];
  isDefault: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
};

export type ActivityTicketInfo = {
  __typename: 'ActivityTicketInfo';
  cost?: Maybe<Scalars['Int']['output']>;
  fee?: Maybe<Scalars['Int']['output']>;
  notes?: Maybe<Scalars['String']['output']>;
  tax?: Maybe<Scalars['Int']['output']>;
  type?: Maybe<Scalars['String']['output']>;
};

export type ActivityVenue = {
  __typename: 'ActivityVenue';
  location: Location;
  name: Scalars['String']['output'];
};

export type AuthTokenPair = {
  __typename: 'AuthTokenPair';
  accessToken: Scalars['String']['output'];
  refreshToken: Scalars['String']['output'];
};

export type Booking = {
  __typename: 'Booking';
  id: Scalars['UUID']['output'];
  reserverDetailsId: Scalars['UUID']['output'];
};

export type CreateAccountFailure = {
  __typename: 'CreateAccountFailure';
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
  __typename: 'CreateAccountSuccess';
  account: Account;
  authTokens: AuthTokenPair;
};

export type CreateBookingFailure = {
  __typename: 'CreateBookingFailure';
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
  __typename: 'CreateBookingSuccess';
  booking: Booking;
};

export type CreatePaymentIntentFailure = {
  __typename: 'CreatePaymentIntentFailure';
  failureReason: CreatePaymentIntentFailureReason;
};

export enum CreatePaymentIntentFailureReason {
  PaymentIntentFailed = 'PAYMENT_INTENT_FAILED',
  Unknown = 'UNKNOWN'
}

export type CreatePaymentIntentInput = {
  placeholder: Scalars['String']['input'];
};

export type CreatePaymentIntentResult = CreatePaymentIntentFailure | CreatePaymentIntentSuccess;

export type CreatePaymentIntentSuccess = {
  __typename: 'CreatePaymentIntentSuccess';
  paymentIntent: PaymentIntent;
};

export type Location = {
  __typename: 'Location';
  directionsUri: Scalars['String']['output'];
  formattedAddress: Scalars['String']['output'];
  latitude: Scalars['Float']['output'];
  longitude: Scalars['Float']['output'];
};

export type LoginFailure = {
  __typename: 'LoginFailure';
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
  __typename: 'LoginSuccess';
  account: Account;
  authTokens: AuthTokenPair;
};

export type Mutation = {
  __typename: 'Mutation';
  createAccount: CreateAccountResult;
  login: LoginResult;
  logout?: Maybe<Scalars['Void']['output']>;
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
  __typename: 'Outing';
  activity?: Maybe<Activity>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  budget: OutingBudget;
  drivingTime: Scalars['String']['output'];
  headcount: Scalars['Int']['output'];
  id: Scalars['UUID']['output'];
  restaurant?: Maybe<Restaurant>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
  surveyId: Scalars['UUID']['output'];
  visitorId: Scalars['UUID']['output'];
};

export enum OutingBudget {
  Expensive = 'EXPENSIVE',
  Free = 'FREE',
  Inexpensive = 'INEXPENSIVE',
  Moderate = 'MODERATE',
  VeryExpensive = 'VERY_EXPENSIVE'
}

export enum OutingState {
  Future = 'FUTURE',
  Past = 'PAST'
}

export type PaymentIntent = {
  __typename: 'PaymentIntent';
  clientSecret: Scalars['String']['output'];
};

export type Photos = {
  __typename: 'Photos';
  coverPhotoUri: Scalars['String']['output'];
  supplementalPhotoUris?: Maybe<Array<Scalars['String']['output']>>;
};

export type PlanOutingFailure = {
  __typename: 'PlanOutingFailure';
  failureReason: PlanOutingFailureReason;
};

export enum PlanOutingFailureReason {
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type PlanOutingInput = {
  budget: OutingBudget;
  groupPreferences?: InputMaybe<Array<PreferencesInput>>;
  headcount: Scalars['Int']['input'];
  searchAreaIds: Array<Scalars['UUID']['input']>;
  startTime: Scalars['DateTime']['input'];
  visitorId: Scalars['UUID']['input'];
};

export type PlanOutingResult = PlanOutingFailure | PlanOutingSuccess;

export type PlanOutingSuccess = {
  __typename: 'PlanOutingSuccess';
  outing: Outing;
};

export type Preferences = {
  __typename: 'Preferences';
  activityCategories: Array<ActivityCategory>;
  openToBars: Scalars['Boolean']['output'];
  requiresWheelchairAccessibility: Scalars['Boolean']['output'];
  restaurantCategories: Array<RestaurantCategory>;
};

export type PreferencesInput = {
  activityCategoryIds: Array<Scalars['UUID']['input']>;
  openToBars: Scalars['Boolean']['input'];
  requiresWheelchairAccessibility: Scalars['Boolean']['input'];
  restaurantCategoryIds: Array<Scalars['UUID']['input']>;
};

export type Query = {
  __typename: 'Query';
  activityCategories: Array<ActivityCategory>;
  restaurantCategories: Array<RestaurantCategory>;
  searchRegions: Array<SearchRegion>;
  viewer: ViewerQueries;
};

export type RefreshTokensFailure = {
  __typename: 'RefreshTokensFailure';
  failureReason: RefreshTokensFailureReason;
};

export enum RefreshTokensFailureReason {
  InvalidTokens = 'INVALID_TOKENS'
}

export type RefreshTokensInput = {
  accessToken: Scalars['String']['input'];
  refreshToken: Scalars['String']['input'];
};

export type RefreshTokensResult = RefreshTokensFailure | RefreshTokensSuccess;

export type RefreshTokensSuccess = {
  __typename: 'RefreshTokensSuccess';
  authTokens: AuthTokenPair;
};

export type ReplanOutingFailure = {
  __typename: 'ReplanOutingFailure';
  failureReason: ReplanOutingFailureReason;
};

export enum ReplanOutingFailureReason {
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type ReplanOutingInput = {
  outingId: Scalars['UUID']['input'];
  visitorId: Scalars['UUID']['input'];
};

export type ReplanOutingResult = ReplanOutingFailure | ReplanOutingSuccess;

export type ReplanOutingSuccess = {
  __typename: 'ReplanOutingSuccess';
  outing: Outing;
};

export type ReserverDetails = {
  __typename: 'ReserverDetails';
  accountId: Scalars['UUID']['output'];
  firstName: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  lastName: Scalars['String']['output'];
  phoneNumber: Scalars['String']['output'];
};

export type Restaurant = {
  __typename: 'Restaurant';
  customerFavorites?: Maybe<Scalars['String']['output']>;
  description: Scalars['String']['output'];
  id: Scalars['String']['output'];
  location: Location;
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos?: Maybe<Photos>;
  primaryTypeName: Scalars['String']['output'];
  rating: Scalars['Float']['output'];
  reservable: Scalars['Boolean']['output'];
  source: RestaurantSource;
  websiteUri?: Maybe<Scalars['String']['output']>;
};

export type RestaurantCategory = {
  __typename: 'RestaurantCategory';
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
};

export enum RestaurantSource {
  GooglePlaces = 'GOOGLE_PLACES'
}

export type SearchRegion = {
  __typename: 'SearchRegion';
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
};

export type SubmitReserverDetailsFailure = {
  __typename: 'SubmitReserverDetailsFailure';
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
  __typename: 'SubmitReserverDetailsSuccess';
  reserverDetails: ReserverDetails;
};

export type UpdateAccountFailure = {
  __typename: 'UpdateAccountFailure';
  failureReason: UpdateAccountFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdateAccountFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdateAccountInput = {
  email?: InputMaybe<Scalars['String']['input']>;
  plaintextPassword?: InputMaybe<Scalars['String']['input']>;
};

export type UpdateAccountResult = UpdateAccountFailure | UpdateAccountSuccess;

export type UpdateAccountSuccess = {
  __typename: 'UpdateAccountSuccess';
  account: Account;
};

export type UpdatePreferencesFailure = {
  __typename: 'UpdatePreferencesFailure';
  failureReason: UpdatePreferencesFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum UpdatePreferencesFailureReason {
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type UpdatePreferencesInput = {
  activityCategoryIds?: InputMaybe<Array<Scalars['UUID']['input']>>;
  openToBars?: InputMaybe<Scalars['Boolean']['input']>;
  requiresWheelchairAccessibility?: InputMaybe<Scalars['Boolean']['input']>;
  restaurantCategoryIds?: InputMaybe<Array<Scalars['UUID']['input']>>;
};

export type UpdatePreferencesResult = UpdatePreferencesFailure | UpdatePreferencesSuccess;

export type UpdatePreferencesSuccess = {
  __typename: 'UpdatePreferencesSuccess';
  preferences: Preferences;
};

export type UpdateReserverDetailsAccountFailure = {
  __typename: 'UpdateReserverDetailsAccountFailure';
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
  __typename: 'UpdateReserverDetailsAccountSuccess';
  account: Account;
  reserverDetails: ReserverDetails;
};

export type ValidationError = {
  __typename: 'ValidationError';
  field: Scalars['String']['output'];
};

export type ViewerMutations = {
  __typename: 'ViewerMutations';
  createBooking: CreateBookingResult;
  createPaymentIntent: CreatePaymentIntentResult;
  planOuting: PlanOutingResult;
  refreshTokens: RefreshTokensResult;
  replanOuting: ReplanOutingResult;
  submitReserverDetails: SubmitReserverDetailsResult;
  updateAccount: UpdateAccountResult;
  updatePreferences: UpdatePreferencesResult;
  updateReserverDetailsAccount: UpdateReserverDetailsAccountResult;
};


export type ViewerMutationsCreateBookingArgs = {
  input: CreateBookingInput;
};


export type ViewerMutationsCreatePaymentIntentArgs = {
  input: CreatePaymentIntentInput;
};


export type ViewerMutationsPlanOutingArgs = {
  input: PlanOutingInput;
};


export type ViewerMutationsRefreshTokensArgs = {
  input: RefreshTokensInput;
};


export type ViewerMutationsReplanOutingArgs = {
  input: ReplanOutingInput;
};


export type ViewerMutationsSubmitReserverDetailsArgs = {
  input: SubmitReserverDetailsInput;
};


export type ViewerMutationsUpdateAccountArgs = {
  input: UpdateAccountInput;
};


export type ViewerMutationsUpdatePreferencesArgs = {
  input: UpdatePreferencesInput;
};


export type ViewerMutationsUpdateReserverDetailsAccountArgs = {
  input: UpdateReserverDetailsAccountInput;
};

export type ViewerQueries = {
  __typename: 'ViewerQueries';
  bookedOutings: Array<Outing>;
  outing: Outing;
  reserverDetails: Array<ReserverDetails>;
};


export type ViewerQueriesBookedOutingsArgs = {
  outingState: OutingState;
};


export type ViewerQueriesOutingArgs = {
  outingId: Scalars['UUID']['input'];
};

export type CreateAccountMutationVariables = Exact<{
  input: CreateAccountInput;
}>;


export type CreateAccountMutation = { __typename: 'Mutation', createAccount: { __typename: 'CreateAccountFailure', failureReason: CreateAccountFailureReason, validationErrors?: Array<{ __typename: 'ValidationError', field: string }> | null } | { __typename: 'CreateAccountSuccess', account: { __typename: 'Account', id: string, email: string }, authTokens: { __typename: 'AuthTokenPair', accessToken: string, refreshToken: string } } };

export type CreateBookingMutationVariables = Exact<{
  input: CreateBookingInput;
}>;


export type CreateBookingMutation = { __typename: 'Mutation', viewer: { __typename: 'ViewerMutations', createBooking: { __typename: 'CreateBookingFailure', failureReason: CreateBookingFailureReason, validationErrors?: Array<{ __typename: 'ValidationError', field: string }> | null } | { __typename: 'CreateBookingSuccess', booking: { __typename: 'Booking', id: string } } } };

export type CreatePaymentIntentMutationVariables = Exact<{
  input: CreatePaymentIntentInput;
}>;


export type CreatePaymentIntentMutation = { __typename: 'Mutation', viewer: { __typename: 'ViewerMutations', createPaymentIntent: { __typename: 'CreatePaymentIntentFailure', failureReason: CreatePaymentIntentFailureReason } | { __typename: 'CreatePaymentIntentSuccess', paymentIntent: { __typename: 'PaymentIntent', clientSecret: string } } } };

export type LoginMutationVariables = Exact<{
  input: LoginInput;
}>;


export type LoginMutation = { __typename: 'Mutation', login: { __typename: 'LoginFailure', failureReason: LoginFailureReason } | { __typename: 'LoginSuccess', account: { __typename: 'Account', id: string, email: string }, authTokens: { __typename: 'AuthTokenPair', accessToken: string, refreshToken: string } } };

export type PlanOutingMutationVariables = Exact<{
  input: PlanOutingInput;
}>;


export type PlanOutingMutation = { __typename: 'Mutation', planOuting: { __typename: 'PlanOutingFailure', failureReason: PlanOutingFailureReason } | { __typename: 'PlanOutingSuccess', outing: { __typename: 'Outing', id: string } } };

export type ReplanOutingMutationVariables = Exact<{
  input: ReplanOutingInput;
}>;


export type ReplanOutingMutation = { __typename: 'Mutation', replanOuting: { __typename: 'ReplanOutingFailure', failureReason: ReplanOutingFailureReason } | { __typename: 'ReplanOutingSuccess', outing: { __typename: 'Outing', id: string } } };

export type SubmitReserverDetailsMutationVariables = Exact<{
  input: SubmitReserverDetailsInput;
}>;


export type SubmitReserverDetailsMutation = { __typename: 'Mutation', viewer: { __typename: 'ViewerMutations', submitReserverDetails: { __typename: 'SubmitReserverDetailsFailure', failureReason: SubmitReserverDetailsFailureReason, validationErrors?: Array<{ __typename: 'ValidationError', field: string }> | null } | { __typename: 'SubmitReserverDetailsSuccess', reserverDetails: { __typename: 'ReserverDetails', id: string } } } };

export type UpdateReserverDetailsAccountMutationVariables = Exact<{
  input: UpdateReserverDetailsAccountInput;
}>;


export type UpdateReserverDetailsAccountMutation = { __typename: 'Mutation', viewer: { __typename: 'ViewerMutations', updateReserverDetailsAccount: { __typename: 'UpdateReserverDetailsAccountFailure', failureReason: UpdateReserverDetailsAccountFailureReason, validationErrors?: Array<{ __typename: 'ValidationError', field: string }> | null } | { __typename: 'UpdateReserverDetailsAccountSuccess', reserverDetails: { __typename: 'ReserverDetails', id: string, firstName: string, lastName: string, phoneNumber: string }, account: { __typename: 'Account', email: string } } } };

export type SearchRegionsQueryVariables = Exact<{ [key: string]: never; }>;


export type SearchRegionsQuery = { __typename: 'Query', searchRegions: Array<{ __typename: 'SearchRegion', id: string, name: string }> };

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

export const CreateAccountDocument = new TypedDocumentString(`
    mutation CreateAccount($input: CreateAccountInput!) {
  createAccount(input: $input) {
    __typename
    ... on CreateAccountSuccess {
      account {
        id
        email
      }
      authTokens {
        accessToken
        refreshToken
      }
    }
    ... on CreateAccountFailure {
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
    createBooking(input: $input) {
      __typename
      ... on CreateBookingSuccess {
        booking {
          id
        }
      }
      ... on CreateBookingFailure {
        failureReason
        validationErrors {
          field
        }
      }
    }
  }
}
    `) as unknown as TypedDocumentString<CreateBookingMutation, CreateBookingMutationVariables>;
export const CreatePaymentIntentDocument = new TypedDocumentString(`
    mutation CreatePaymentIntent($input: CreatePaymentIntentInput!) {
  viewer {
    createPaymentIntent(input: $input) {
      __typename
      ... on CreatePaymentIntentSuccess {
        paymentIntent {
          clientSecret
        }
      }
      ... on CreatePaymentIntentFailure {
        failureReason
      }
    }
  }
}
    `) as unknown as TypedDocumentString<CreatePaymentIntentMutation, CreatePaymentIntentMutationVariables>;
export const LoginDocument = new TypedDocumentString(`
    mutation Login($input: LoginInput!) {
  login(input: $input) {
    __typename
    ... on LoginSuccess {
      account {
        id
        email
      }
      authTokens {
        accessToken
        refreshToken
      }
    }
    ... on LoginFailure {
      failureReason
    }
  }
}
    `) as unknown as TypedDocumentString<LoginMutation, LoginMutationVariables>;
export const PlanOutingDocument = new TypedDocumentString(`
    mutation PlanOuting($input: PlanOutingInput!) {
  planOuting(input: $input) {
    __typename
    ... on PlanOutingSuccess {
      outing {
        id
      }
    }
    ... on PlanOutingFailure {
      failureReason
    }
  }
}
    `) as unknown as TypedDocumentString<PlanOutingMutation, PlanOutingMutationVariables>;
export const ReplanOutingDocument = new TypedDocumentString(`
    mutation ReplanOuting($input: ReplanOutingInput!) {
  replanOuting(input: $input) {
    __typename
    ... on ReplanOutingSuccess {
      outing {
        id
      }
    }
    ... on ReplanOutingFailure {
      failureReason
    }
  }
}
    `) as unknown as TypedDocumentString<ReplanOutingMutation, ReplanOutingMutationVariables>;
export const SubmitReserverDetailsDocument = new TypedDocumentString(`
    mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {
  viewer {
    submitReserverDetails(input: $input) {
      __typename
      ... on SubmitReserverDetailsSuccess {
        reserverDetails {
          id
        }
      }
      ... on SubmitReserverDetailsFailure {
        failureReason
        validationErrors {
          field
        }
      }
    }
  }
}
    `) as unknown as TypedDocumentString<SubmitReserverDetailsMutation, SubmitReserverDetailsMutationVariables>;
export const UpdateReserverDetailsAccountDocument = new TypedDocumentString(`
    mutation UpdateReserverDetailsAccount($input: UpdateReserverDetailsAccountInput!) {
  viewer {
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
}
    `) as unknown as TypedDocumentString<UpdateReserverDetailsAccountMutation, UpdateReserverDetailsAccountMutationVariables>;
export const SearchRegionsDocument = new TypedDocumentString(`
    query SearchRegions {
  searchRegions {
    id
    name
  }
}
    `) as unknown as TypedDocumentString<SearchRegionsQuery, SearchRegionsQueryVariables>;