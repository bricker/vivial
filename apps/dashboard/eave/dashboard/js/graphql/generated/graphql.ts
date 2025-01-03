// @ts-nocheck
/* eslint-disable */
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
  DateTime: { input: string; output: string; }
  UUID: { input: string; output: string; }
};

export type Account = {
  __typename?: 'Account';
  email: Scalars['String']['output'];
  id: Scalars['UUID']['output'];
  stripeCustomerId?: Maybe<Scalars['String']['output']>;
};

export type Activity = {
  __typename?: 'Activity';
  categoryGroup?: Maybe<ActivityCategoryGroup>;
  description?: Maybe<Scalars['String']['output']>;
  doorTips?: Maybe<Scalars['String']['output']>;
  insiderTips?: Maybe<Scalars['String']['output']>;
  isBookable: Scalars['Boolean']['output'];
  name: Scalars['String']['output'];
  parkingTips?: Maybe<Scalars['String']['output']>;
  photos: Photos;
  primaryTypeName?: Maybe<Scalars['String']['output']>;
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

export type ActivityPlan = {
  __typename?: 'ActivityPlan';
  activity: Activity;
  costBreakdown: CostBreakdown;
  headcount: Scalars['Int']['output'];
  startTime: Scalars['DateTime']['output'];
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
  account: Account;
  billingPortalUrl: Scalars['String']['output'];
  bookedOutingDetails?: Maybe<BookingDetails>;
  bookedOutings: Array<BookingDetailsPeek>;
  outingPreferences: OutingPreferences;
  paymentMethods: Array<PaymentMethod>;
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

export type BookingDetails = Itinerary & {
  __typename?: 'BookingDetails';
  activityPlan?: Maybe<ActivityPlan>;
  costBreakdown: CostBreakdown;
  headcount: Scalars['Int']['output'];
  id: Scalars['UUID']['output'];
  reservation?: Maybe<Reservation>;
  searchRegions: Array<SearchRegion>;
  startTime: Scalars['DateTime']['output'];
  state: BookingState;
  survey?: Maybe<Survey>;
  travel?: Maybe<TravelInfo>;
};

export type BookingDetailsPeek = {
  __typename?: 'BookingDetailsPeek';
  activityName?: Maybe<Scalars['String']['output']>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  id: Scalars['UUID']['output'];
  photoUri?: Maybe<Scalars['String']['output']>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
  restaurantName?: Maybe<Scalars['String']['output']>;
  state: BookingState;
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
  PaymentRequired = 'PAYMENT_REQUIRED',
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type ConfirmBookingInput = {
  bookingId: Scalars['UUID']['input'];
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

export type CustomerSession = {
  __typename?: 'CustomerSession';
  clientSecret: Scalars['String']['output'];
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
  BookingAlreadyConfirmed = 'BOOKING_ALREADY_CONFIRMED',
  PaymentIntentFailed = 'PAYMENT_INTENT_FAILED',
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON',
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type InitiateBookingInput = {
  autoConfirm?: Scalars['Boolean']['input'];
  outingId: Scalars['UUID']['input'];
};

export type InitiateBookingResult = InitiateBookingFailure | InitiateBookingSuccess;

export type InitiateBookingSuccess = {
  __typename?: 'InitiateBookingSuccess';
  booking: BookingDetails;
  customerSession?: Maybe<CustomerSession>;
  paymentIntent?: Maybe<PaymentIntent>;
};

export type Itinerary = {
  activityPlan?: Maybe<ActivityPlan>;
  costBreakdown: CostBreakdown;
  headcount: Scalars['Int']['output'];
  id: Scalars['UUID']['output'];
  reservation?: Maybe<Reservation>;
  searchRegions: Array<SearchRegion>;
  startTime: Scalars['DateTime']['output'];
  survey?: Maybe<Survey>;
  travel?: Maybe<TravelInfo>;
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

export type Outing = Itinerary & {
  __typename?: 'Outing';
  activityPlan?: Maybe<ActivityPlan>;
  costBreakdown: CostBreakdown;
  headcount: Scalars['Int']['output'];
  id: Scalars['UUID']['output'];
  reservation?: Maybe<Reservation>;
  searchRegions: Array<SearchRegion>;
  startTime: Scalars['DateTime']['output'];
  survey?: Maybe<Survey>;
  travel?: Maybe<TravelInfo>;
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

export type PaymentCard = {
  __typename?: 'PaymentCard';
  brand: Scalars['String']['output'];
  expMonth: Scalars['Int']['output'];
  expYear: Scalars['Int']['output'];
  last4: Scalars['String']['output'];
};

export type PaymentIntent = {
  __typename?: 'PaymentIntent';
  clientSecret: Scalars['String']['output'];
  id: Scalars['String']['output'];
};

export type PaymentMethod = {
  __typename?: 'PaymentMethod';
  card?: Maybe<PaymentCard>;
  id: Scalars['String']['output'];
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
  StartTimeTooLate = 'START_TIME_TOO_LATE',
  StartTimeTooSoon = 'START_TIME_TOO_SOON'
}

export type PlanOutingInput = {
  budget: OutingBudget;
  excludedEventbriteEventIds?: InputMaybe<Array<Scalars['String']['input']>>;
  excludedEvergreenActivityIds?: InputMaybe<Array<Scalars['UUID']['input']>>;
  excludedGooglePlaceIds?: InputMaybe<Array<Scalars['String']['input']>>;
  groupPreferences: Array<OutingPreferencesInput>;
  headcount: Scalars['Int']['input'];
  isReroll?: Scalars['Boolean']['input'];
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

export type Reservation = {
  __typename?: 'Reservation';
  arrivalTime: Scalars['DateTime']['output'];
  costBreakdown: CostBreakdown;
  headcount: Scalars['Int']['output'];
  restaurant: Restaurant;
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

export type TravelInfo = {
  __typename?: 'TravelInfo';
  durationMinutes: Scalars['Int']['output'];
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
  firstName?: InputMaybe<Scalars['String']['input']>;
  id: Scalars['UUID']['input'];
  lastName?: InputMaybe<Scalars['String']['input']>;
  phoneNumber?: InputMaybe<Scalars['String']['input']>;
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

export type AccountFieldsFragment = {
  __typename: 'Account',
  id: string,
  email: string,
  stripeCustomerId?: string | null
};

export type ActivityFieldsFragment = {
  __typename: 'Activity',
  sourceId: string,
  source: ActivitySource,
  isBookable: boolean,
  name: string,
  description?: string | null,
  websiteUri?: string | null,
  doorTips?: string | null,
  insiderTips?: string | null,
  parkingTips?: string | null,
  primaryTypeName?: string | null,
  categoryGroup?: {
    __typename: 'ActivityCategoryGroup',
    id: string,
    name: string,
    activityCategories: Array<{
      __typename: 'ActivityCategory',
      id: string,
      name: string,
      isDefault: boolean
    }>
  } | null,
  ticketInfo?: {
    __typename: 'TicketInfo',
    name?: string | null,
    notes?: string | null,
    costBreakdown: {
      __typename: 'CostBreakdown',
      baseCostCents: number,
      feeCents: number,
      taxCents: number,
      totalCostCents: number
    }
  } | null,
  venue: {
    __typename: 'ActivityVenue',
    name: string,
    location: {
      __typename: 'Location',
      directionsUri?: string | null,
      coordinates: {
        __typename: 'GeoPoint',
        lat: number,
        lon: number
      },
      address: {
        __typename: 'Address',
        address1?: string | null,
        address2?: string | null,
        city?: string | null,
        state?: string | null,
        zipCode?: string | null,
        country?: string | null,
        formattedMultiline: string,
        formattedSingleline: string
      },
      searchRegion: {
        __typename: 'SearchRegion',
        id: string,
        name: string
      }
    }
  },
  photos: {
    __typename: 'Photos',
    coverPhoto?: {
      __typename: 'Photo',
      id: string,
      src: string,
      alt?: string | null,
      attributions: Array<string>
    } | null,
    supplementalPhotos: Array<{
      __typename: 'Photo',
      id: string,
      src: string,
      alt?: string | null,
      attributions: Array<string>
    }>
  }
};

export type ActivityPlanFieldsFragment = {
  __typename: 'ActivityPlan',
  startTime: string,
  headcount: number,
  costBreakdown: {
    __typename: 'CostBreakdown',
    baseCostCents: number,
    feeCents: number,
    taxCents: number,
    totalCostCents: number
  },
  activity: {
    __typename: 'Activity',
    sourceId: string,
    source: ActivitySource,
    isBookable: boolean,
    name: string,
    description?: string | null,
    websiteUri?: string | null,
    doorTips?: string | null,
    insiderTips?: string | null,
    parkingTips?: string | null,
    primaryTypeName?: string | null,
    categoryGroup?: {
      __typename: 'ActivityCategoryGroup',
      id: string,
      name: string,
      activityCategories: Array<{
        __typename: 'ActivityCategory',
        id: string,
        name: string,
        isDefault: boolean
      }>
    } | null,
    ticketInfo?: {
      __typename: 'TicketInfo',
      name?: string | null,
      notes?: string | null,
      costBreakdown: {
        __typename: 'CostBreakdown',
        baseCostCents: number,
        feeCents: number,
        taxCents: number,
        totalCostCents: number
      }
    } | null,
    venue: {
      __typename: 'ActivityVenue',
      name: string,
      location: {
        __typename: 'Location',
        directionsUri?: string | null,
        coordinates: {
          __typename: 'GeoPoint',
          lat: number,
          lon: number
        },
        address: {
          __typename: 'Address',
          address1?: string | null,
          address2?: string | null,
          city?: string | null,
          state?: string | null,
          zipCode?: string | null,
          country?: string | null,
          formattedMultiline: string,
          formattedSingleline: string
        },
        searchRegion: {
          __typename: 'SearchRegion',
          id: string,
          name: string
        }
      }
    },
    photos: {
      __typename: 'Photos',
      coverPhoto?: {
        __typename: 'Photo',
        id: string,
        src: string,
        alt?: string | null,
        attributions: Array<string>
      } | null,
      supplementalPhotos: Array<{
        __typename: 'Photo',
        id: string,
        src: string,
        alt?: string | null,
        attributions: Array<string>
      }>
    }
  }
};

export type AddressFieldsFragment = {
  __typename: 'Address',
  address1?: string | null,
  address2?: string | null,
  city?: string | null,
  state?: string | null,
  zipCode?: string | null,
  country?: string | null,
  formattedMultiline: string,
  formattedSingleline: string
};

export type BookingFieldsFragment = {
  __typename: 'Booking',
  id: string,
  state: BookingState,
  reserverDetails?: {
    __typename: 'ReserverDetails',
    id: string,
    firstName: string,
    lastName: string,
    phoneNumber: string
  } | null
};

export type BookingDetailsPeekFieldsFragment = {
  __typename: 'BookingDetailsPeek',
  id: string,
  activityStartTime?: string | null,
  restaurantArrivalTime?: string | null,
  activityName?: string | null,
  restaurantName?: string | null,
  photoUri?: string | null,
  state: BookingState
};

export type ActivityCategoryFieldsFragment = {
  __typename: 'ActivityCategory',
  id: string,
  name: string,
  isDefault: boolean
};

export type ActivityCategoryGroupFieldsFragment = {
  __typename: 'ActivityCategoryGroup',
  id: string,
  name: string,
  activityCategories: Array<{
    __typename: 'ActivityCategory',
    id: string,
    name: string,
    isDefault: boolean
  }>
};

export type RestaurantCategoryFieldsFragment = {
  __typename: 'RestaurantCategory',
  id: string,
  name: string,
  isDefault: boolean
};

export type CostBreakdownFieldsFragment = {
  __typename: 'CostBreakdown',
  baseCostCents: number,
  feeCents: number,
  taxCents: number,
  totalCostCents: number
};

export type CustomerSessionFieldsFragment = {
  __typename: 'CustomerSession',
  clientSecret: string
};

type ItineraryFields_BookingDetails_Fragment = {
  __typename: 'BookingDetails',
  id: string,
  startTime: string,
  headcount: number,
  survey?: {
    __typename: 'Survey',
    id: string,
    budget: OutingBudget,
    headcount: number,
    startTime: string,
    searchRegions: Array<{
      __typename: 'SearchRegion',
      id: string,
      name: string
    }>
  } | null,
  searchRegions: Array<{
    __typename: 'SearchRegion',
    id: string,
    name: string
  }>,
  costBreakdown: {
    __typename: 'CostBreakdown',
    baseCostCents: number,
    feeCents: number,
    taxCents: number,
    totalCostCents: number
  },
  activityPlan?: {
    __typename: 'ActivityPlan',
    startTime: string,
    headcount: number,
    costBreakdown: {
      __typename: 'CostBreakdown',
      baseCostCents: number,
      feeCents: number,
      taxCents: number,
      totalCostCents: number
    },
    activity: {
      __typename: 'Activity',
      sourceId: string,
      source: ActivitySource,
      isBookable: boolean,
      name: string,
      description?: string | null,
      websiteUri?: string | null,
      doorTips?: string | null,
      insiderTips?: string | null,
      parkingTips?: string | null,
      primaryTypeName?: string | null,
      categoryGroup?: {
        __typename: 'ActivityCategoryGroup',
        id: string,
        name: string,
        activityCategories: Array<{
          __typename: 'ActivityCategory',
          id: string,
          name: string,
          isDefault: boolean
        }>
      } | null,
      ticketInfo?: {
        __typename: 'TicketInfo',
        name?: string | null,
        notes?: string | null,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        }
      } | null,
      venue: {
        __typename: 'ActivityVenue',
        name: string,
        location: {
          __typename: 'Location',
          directionsUri?: string | null,
          coordinates: {
            __typename: 'GeoPoint',
            lat: number,
            lon: number
          },
          address: {
            __typename: 'Address',
            address1?: string | null,
            address2?: string | null,
            city?: string | null,
            state?: string | null,
            zipCode?: string | null,
            country?: string | null,
            formattedMultiline: string,
            formattedSingleline: string
          },
          searchRegion: {
            __typename: 'SearchRegion',
            id: string,
            name: string
          }
        }
      },
      photos: {
        __typename: 'Photos',
        coverPhoto?: {
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        } | null,
        supplementalPhotos: Array<{
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        }>
      }
    }
  } | null,
  reservation?: {
    __typename: 'Reservation',
    arrivalTime: string,
    headcount: number,
    costBreakdown: {
      __typename: 'CostBreakdown',
      baseCostCents: number,
      feeCents: number,
      taxCents: number,
      totalCostCents: number
    },
    restaurant: {
      __typename: 'Restaurant',
      sourceId: string,
      source: RestaurantSource,
      name: string,
      reservable: boolean,
      rating: number,
      primaryTypeName: string,
      websiteUri?: string | null,
      description: string,
      parkingTips?: string | null,
      customerFavorites?: string | null,
      location: {
        __typename: 'Location',
        directionsUri?: string | null,
        coordinates: {
          __typename: 'GeoPoint',
          lat: number,
          lon: number
        },
        address: {
          __typename: 'Address',
          address1?: string | null,
          address2?: string | null,
          city?: string | null,
          state?: string | null,
          zipCode?: string | null,
          country?: string | null,
          formattedMultiline: string,
          formattedSingleline: string
        },
        searchRegion: {
          __typename: 'SearchRegion',
          id: string,
          name: string
        }
      },
      photos: {
        __typename: 'Photos',
        coverPhoto?: {
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        } | null,
        supplementalPhotos: Array<{
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        }>
      }
    }
  } | null
};

type ItineraryFields_Outing_Fragment = {
  __typename: 'Outing',
  id: string,
  startTime: string,
  headcount: number,
  survey?: {
    __typename: 'Survey',
    id: string,
    budget: OutingBudget,
    headcount: number,
    startTime: string,
    searchRegions: Array<{
      __typename: 'SearchRegion',
      id: string,
      name: string
    }>
  } | null,
  searchRegions: Array<{
    __typename: 'SearchRegion',
    id: string,
    name: string
  }>,
  costBreakdown: {
    __typename: 'CostBreakdown',
    baseCostCents: number,
    feeCents: number,
    taxCents: number,
    totalCostCents: number
  },
  activityPlan?: {
    __typename: 'ActivityPlan',
    startTime: string,
    headcount: number,
    costBreakdown: {
      __typename: 'CostBreakdown',
      baseCostCents: number,
      feeCents: number,
      taxCents: number,
      totalCostCents: number
    },
    activity: {
      __typename: 'Activity',
      sourceId: string,
      source: ActivitySource,
      isBookable: boolean,
      name: string,
      description?: string | null,
      websiteUri?: string | null,
      doorTips?: string | null,
      insiderTips?: string | null,
      parkingTips?: string | null,
      primaryTypeName?: string | null,
      categoryGroup?: {
        __typename: 'ActivityCategoryGroup',
        id: string,
        name: string,
        activityCategories: Array<{
          __typename: 'ActivityCategory',
          id: string,
          name: string,
          isDefault: boolean
        }>
      } | null,
      ticketInfo?: {
        __typename: 'TicketInfo',
        name?: string | null,
        notes?: string | null,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        }
      } | null,
      venue: {
        __typename: 'ActivityVenue',
        name: string,
        location: {
          __typename: 'Location',
          directionsUri?: string | null,
          coordinates: {
            __typename: 'GeoPoint',
            lat: number,
            lon: number
          },
          address: {
            __typename: 'Address',
            address1?: string | null,
            address2?: string | null,
            city?: string | null,
            state?: string | null,
            zipCode?: string | null,
            country?: string | null,
            formattedMultiline: string,
            formattedSingleline: string
          },
          searchRegion: {
            __typename: 'SearchRegion',
            id: string,
            name: string
          }
        }
      },
      photos: {
        __typename: 'Photos',
        coverPhoto?: {
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        } | null,
        supplementalPhotos: Array<{
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        }>
      }
    }
  } | null,
  reservation?: {
    __typename: 'Reservation',
    arrivalTime: string,
    headcount: number,
    costBreakdown: {
      __typename: 'CostBreakdown',
      baseCostCents: number,
      feeCents: number,
      taxCents: number,
      totalCostCents: number
    },
    restaurant: {
      __typename: 'Restaurant',
      sourceId: string,
      source: RestaurantSource,
      name: string,
      reservable: boolean,
      rating: number,
      primaryTypeName: string,
      websiteUri?: string | null,
      description: string,
      parkingTips?: string | null,
      customerFavorites?: string | null,
      location: {
        __typename: 'Location',
        directionsUri?: string | null,
        coordinates: {
          __typename: 'GeoPoint',
          lat: number,
          lon: number
        },
        address: {
          __typename: 'Address',
          address1?: string | null,
          address2?: string | null,
          city?: string | null,
          state?: string | null,
          zipCode?: string | null,
          country?: string | null,
          formattedMultiline: string,
          formattedSingleline: string
        },
        searchRegion: {
          __typename: 'SearchRegion',
          id: string,
          name: string
        }
      },
      photos: {
        __typename: 'Photos',
        coverPhoto?: {
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        } | null,
        supplementalPhotos: Array<{
          __typename: 'Photo',
          id: string,
          src: string,
          alt?: string | null,
          attributions: Array<string>
        }>
      }
    }
  } | null
};

export type ItineraryFieldsFragment = ItineraryFields_BookingDetails_Fragment | ItineraryFields_Outing_Fragment;

type TravelFields_BookingDetails_Fragment = {
  __typename: 'BookingDetails',
  travel?: {
    __typename: 'TravelInfo',
    durationMinutes: number
  } | null
};

type TravelFields_Outing_Fragment = {
  __typename: 'Outing',
  travel?: {
    __typename: 'TravelInfo',
    durationMinutes: number
  } | null
};

export type TravelFieldsFragment = TravelFields_BookingDetails_Fragment | TravelFields_Outing_Fragment;

export type LocationFieldsFragment = {
  __typename: 'Location',
  directionsUri?: string | null,
  coordinates: {
    __typename: 'GeoPoint',
    lat: number,
    lon: number
  },
  address: {
    __typename: 'Address',
    address1?: string | null,
    address2?: string | null,
    city?: string | null,
    state?: string | null,
    zipCode?: string | null,
    country?: string | null,
    formattedMultiline: string,
    formattedSingleline: string
  },
  searchRegion: {
    __typename: 'SearchRegion',
    id: string,
    name: string
  }
};

export type OutingPreferencesFieldsFragment = {
  __typename: 'OutingPreferences',
  restaurantCategories?: Array<{
    __typename: 'RestaurantCategory',
    id: string,
    name: string,
    isDefault: boolean
  }> | null,
  activityCategories?: Array<{
    __typename: 'ActivityCategory',
    id: string,
    name: string,
    isDefault: boolean
  }> | null
};

export type PaymentIntentFieldsFragment = {
  __typename: 'PaymentIntent',
  id: string,
  clientSecret: string
};

export type PaymentMethodFieldsFragment = {
  __typename: 'PaymentMethod',
  id: string,
  card?: {
    __typename: 'PaymentCard',
    brand: string,
    last4: string,
    expMonth: number,
    expYear: number
  } | null
};

export type PhotosFieldsFragment = {
  __typename: 'Photos',
  coverPhoto?: {
    __typename: 'Photo',
    id: string,
    src: string,
    alt?: string | null,
    attributions: Array<string>
  } | null,
  supplementalPhotos: Array<{
    __typename: 'Photo',
    id: string,
    src: string,
    alt?: string | null,
    attributions: Array<string>
  }>
};

export type PhotoFieldsFragment = {
  __typename: 'Photo',
  id: string,
  src: string,
  alt?: string | null,
  attributions: Array<string>
};

export type ReservationFieldsFragment = {
  __typename: 'Reservation',
  arrivalTime: string,
  headcount: number,
  costBreakdown: {
    __typename: 'CostBreakdown',
    baseCostCents: number,
    feeCents: number,
    taxCents: number,
    totalCostCents: number
  },
  restaurant: {
    __typename: 'Restaurant',
    sourceId: string,
    source: RestaurantSource,
    name: string,
    reservable: boolean,
    rating: number,
    primaryTypeName: string,
    websiteUri?: string | null,
    description: string,
    parkingTips?: string | null,
    customerFavorites?: string | null,
    location: {
      __typename: 'Location',
      directionsUri?: string | null,
      coordinates: {
        __typename: 'GeoPoint',
        lat: number,
        lon: number
      },
      address: {
        __typename: 'Address',
        address1?: string | null,
        address2?: string | null,
        city?: string | null,
        state?: string | null,
        zipCode?: string | null,
        country?: string | null,
        formattedMultiline: string,
        formattedSingleline: string
      },
      searchRegion: {
        __typename: 'SearchRegion',
        id: string,
        name: string
      }
    },
    photos: {
      __typename: 'Photos',
      coverPhoto?: {
        __typename: 'Photo',
        id: string,
        src: string,
        alt?: string | null,
        attributions: Array<string>
      } | null,
      supplementalPhotos: Array<{
        __typename: 'Photo',
        id: string,
        src: string,
        alt?: string | null,
        attributions: Array<string>
      }>
    }
  }
};

export type ReserverDetailsFieldsFragment = {
  __typename: 'ReserverDetails',
  id: string,
  firstName: string,
  lastName: string,
  phoneNumber: string
};

export type SearchRegionFieldsFragment = {
  __typename: 'SearchRegion',
  id: string,
  name: string
};

export type SurveyFieldsFragment = {
  __typename: 'Survey',
  id: string,
  budget: OutingBudget,
  headcount: number,
  startTime: string,
  searchRegions: Array<{
    __typename: 'SearchRegion',
    id: string,
    name: string
  }>
};

export type ConfirmBookingMutationVariables = Exact<{
  input: ConfirmBookingInput;
}>;


export type ConfirmBookingMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    confirmBooking: {
      __typename: 'ConfirmBookingFailure',
      failureReason: ConfirmBookingFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'ConfirmBookingSuccess',
      booking: {
        __typename: 'Booking',
        id: string,
        state: BookingState,
        reserverDetails?: {
          __typename: 'ReserverDetails',
          id: string,
          firstName: string,
          lastName: string,
          phoneNumber: string
        } | null
      }
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type CreateAccountMutationVariables = Exact<{
  input: CreateAccountInput;
}>;


export type CreateAccountMutation = {
  __typename: 'Mutation',
  createAccount: {
    __typename: 'CreateAccountFailure',
    failureReason: CreateAccountFailureReason,
    validationErrors?: Array<{
      __typename: 'ValidationError',
      field: string
    }> | null
  } | {
    __typename: 'CreateAccountSuccess',
    account: {
      __typename: 'Account',
      id: string,
      email: string,
      stripeCustomerId?: string | null
    }
  }
};

export type InitiateBookingMutationVariables = Exact<{
  input: InitiateBookingInput;
}>;


export type InitiateBookingMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    initiateBooking: {
      __typename: 'InitiateBookingFailure',
      failureReason: InitiateBookingFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'InitiateBookingSuccess',
      booking: {
        __typename: 'BookingDetails',
        id: string,
        startTime: string,
        headcount: number,
        survey?: {
          __typename: 'Survey',
          id: string,
          budget: OutingBudget,
          headcount: number,
          startTime: string,
          searchRegions: Array<{
            __typename: 'SearchRegion',
            id: string,
            name: string
          }>
        } | null,
        searchRegions: Array<{
          __typename: 'SearchRegion',
          id: string,
          name: string
        }>,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        },
        activityPlan?: {
          __typename: 'ActivityPlan',
          startTime: string,
          headcount: number,
          costBreakdown: {
            __typename: 'CostBreakdown',
            baseCostCents: number,
            feeCents: number,
            taxCents: number,
            totalCostCents: number
          },
          activity: {
            __typename: 'Activity',
            sourceId: string,
            source: ActivitySource,
            isBookable: boolean,
            name: string,
            description?: string | null,
            websiteUri?: string | null,
            doorTips?: string | null,
            insiderTips?: string | null,
            parkingTips?: string | null,
            primaryTypeName?: string | null,
            categoryGroup?: {
              __typename: 'ActivityCategoryGroup',
              id: string,
              name: string,
              activityCategories: Array<{
                __typename: 'ActivityCategory',
                id: string,
                name: string,
                isDefault: boolean
              }>
            } | null,
            ticketInfo?: {
              __typename: 'TicketInfo',
              name?: string | null,
              notes?: string | null,
              costBreakdown: {
                __typename: 'CostBreakdown',
                baseCostCents: number,
                feeCents: number,
                taxCents: number,
                totalCostCents: number
              }
            } | null,
            venue: {
              __typename: 'ActivityVenue',
              name: string,
              location: {
                __typename: 'Location',
                directionsUri?: string | null,
                coordinates: {
                  __typename: 'GeoPoint',
                  lat: number,
                  lon: number
                },
                address: {
                  __typename: 'Address',
                  address1?: string | null,
                  address2?: string | null,
                  city?: string | null,
                  state?: string | null,
                  zipCode?: string | null,
                  country?: string | null,
                  formattedMultiline: string,
                  formattedSingleline: string
                },
                searchRegion: {
                  __typename: 'SearchRegion',
                  id: string,
                  name: string
                }
              }
            },
            photos: {
              __typename: 'Photos',
              coverPhoto?: {
                __typename: 'Photo',
                id: string,
                src: string,
                alt?: string | null,
                attributions: Array<string>
              } | null,
              supplementalPhotos: Array<{
                __typename: 'Photo',
                id: string,
                src: string,
                alt?: string | null,
                attributions: Array<string>
              }>
            }
          }
        } | null,
        reservation?: {
          __typename: 'Reservation',
          arrivalTime: string,
          headcount: number,
          costBreakdown: {
            __typename: 'CostBreakdown',
            baseCostCents: number,
            feeCents: number,
            taxCents: number,
            totalCostCents: number
          },
          restaurant: {
            __typename: 'Restaurant',
            sourceId: string,
            source: RestaurantSource,
            name: string,
            reservable: boolean,
            rating: number,
            primaryTypeName: string,
            websiteUri?: string | null,
            description: string,
            parkingTips?: string | null,
            customerFavorites?: string | null,
            location: {
              __typename: 'Location',
              directionsUri?: string | null,
              coordinates: {
                __typename: 'GeoPoint',
                lat: number,
                lon: number
              },
              address: {
                __typename: 'Address',
                address1?: string | null,
                address2?: string | null,
                city?: string | null,
                state?: string | null,
                zipCode?: string | null,
                country?: string | null,
                formattedMultiline: string,
                formattedSingleline: string
              },
              searchRegion: {
                __typename: 'SearchRegion',
                id: string,
                name: string
              }
            },
            photos: {
              __typename: 'Photos',
              coverPhoto?: {
                __typename: 'Photo',
                id: string,
                src: string,
                alt?: string | null,
                attributions: Array<string>
              } | null,
              supplementalPhotos: Array<{
                __typename: 'Photo',
                id: string,
                src: string,
                alt?: string | null,
                attributions: Array<string>
              }>
            }
          }
        } | null
      },
      paymentIntent?: {
        __typename: 'PaymentIntent',
        id: string,
        clientSecret: string
      } | null,
      customerSession?: {
        __typename: 'CustomerSession',
        clientSecret: string
      } | null
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type LoginMutationVariables = Exact<{
  input: LoginInput;
}>;


export type LoginMutation = {
  __typename: 'Mutation',
  login: {
    __typename: 'LoginFailure',
    failureReason: LoginFailureReason
  } | {
    __typename: 'LoginSuccess',
    account: {
      __typename: 'Account',
      id: string,
      email: string,
      stripeCustomerId?: string | null
    }
  }
};

export type PlanOutingMutationVariables = Exact<{
  input: PlanOutingInput;
}>;


export type PlanOutingMutation = {
  __typename: 'Mutation',
  planOuting: {
    __typename: 'PlanOutingFailure',
    failureReason: PlanOutingFailureReason
  } | {
    __typename: 'PlanOutingSuccess',
    outing: {
      __typename: 'Outing',
      id: string,
      startTime: string,
      headcount: number,
      survey?: {
        __typename: 'Survey',
        id: string,
        budget: OutingBudget,
        headcount: number,
        startTime: string,
        searchRegions: Array<{
          __typename: 'SearchRegion',
          id: string,
          name: string
        }>
      } | null,
      searchRegions: Array<{
        __typename: 'SearchRegion',
        id: string,
        name: string
      }>,
      costBreakdown: {
        __typename: 'CostBreakdown',
        baseCostCents: number,
        feeCents: number,
        taxCents: number,
        totalCostCents: number
      },
      activityPlan?: {
        __typename: 'ActivityPlan',
        startTime: string,
        headcount: number,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        },
        activity: {
          __typename: 'Activity',
          sourceId: string,
          source: ActivitySource,
          isBookable: boolean,
          name: string,
          description?: string | null,
          websiteUri?: string | null,
          doorTips?: string | null,
          insiderTips?: string | null,
          parkingTips?: string | null,
          primaryTypeName?: string | null,
          categoryGroup?: {
            __typename: 'ActivityCategoryGroup',
            id: string,
            name: string,
            activityCategories: Array<{
              __typename: 'ActivityCategory',
              id: string,
              name: string,
              isDefault: boolean
            }>
          } | null,
          ticketInfo?: {
            __typename: 'TicketInfo',
            name?: string | null,
            notes?: string | null,
            costBreakdown: {
              __typename: 'CostBreakdown',
              baseCostCents: number,
              feeCents: number,
              taxCents: number,
              totalCostCents: number
            }
          } | null,
          venue: {
            __typename: 'ActivityVenue',
            name: string,
            location: {
              __typename: 'Location',
              directionsUri?: string | null,
              coordinates: {
                __typename: 'GeoPoint',
                lat: number,
                lon: number
              },
              address: {
                __typename: 'Address',
                address1?: string | null,
                address2?: string | null,
                city?: string | null,
                state?: string | null,
                zipCode?: string | null,
                country?: string | null,
                formattedMultiline: string,
                formattedSingleline: string
              },
              searchRegion: {
                __typename: 'SearchRegion',
                id: string,
                name: string
              }
            }
          },
          photos: {
            __typename: 'Photos',
            coverPhoto?: {
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            } | null,
            supplementalPhotos: Array<{
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            }>
          }
        }
      } | null,
      reservation?: {
        __typename: 'Reservation',
        arrivalTime: string,
        headcount: number,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        },
        restaurant: {
          __typename: 'Restaurant',
          sourceId: string,
          source: RestaurantSource,
          name: string,
          reservable: boolean,
          rating: number,
          primaryTypeName: string,
          websiteUri?: string | null,
          description: string,
          parkingTips?: string | null,
          customerFavorites?: string | null,
          location: {
            __typename: 'Location',
            directionsUri?: string | null,
            coordinates: {
              __typename: 'GeoPoint',
              lat: number,
              lon: number
            },
            address: {
              __typename: 'Address',
              address1?: string | null,
              address2?: string | null,
              city?: string | null,
              state?: string | null,
              zipCode?: string | null,
              country?: string | null,
              formattedMultiline: string,
              formattedSingleline: string
            },
            searchRegion: {
              __typename: 'SearchRegion',
              id: string,
              name: string
            }
          },
          photos: {
            __typename: 'Photos',
            coverPhoto?: {
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            } | null,
            supplementalPhotos: Array<{
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            }>
          }
        }
      } | null,
      travel?: {
        __typename: 'TravelInfo',
        durationMinutes: number
      } | null
    }
  }
};

export type SubmitReserverDetailsMutationVariables = Exact<{
  input: SubmitReserverDetailsInput;
}>;


export type SubmitReserverDetailsMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    submitReserverDetails: {
      __typename: 'SubmitReserverDetailsFailure',
      failureReason: SubmitReserverDetailsFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'SubmitReserverDetailsSuccess',
      reserverDetails: {
        __typename: 'ReserverDetails',
        id: string,
        firstName: string,
        lastName: string,
        phoneNumber: string
      }
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type UpdateAccountMutationVariables = Exact<{
  input: UpdateAccountInput;
}>;


export type UpdateAccountMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    updateAccount: {
      __typename: 'UpdateAccountFailure',
      failureReason: UpdateAccountFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'UpdateAccountSuccess',
      account: {
        __typename: 'Account',
        id: string,
        email: string,
        stripeCustomerId?: string | null
      }
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type UpdateOutingPreferencesMutationVariables = Exact<{
  input: UpdateOutingPreferencesInput;
}>;


export type UpdateOutingPreferencesMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    updatePreferences: {
      __typename: 'UpdateOutingPreferencesFailure',
      failureReason: UpdateOutingPreferencesFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'UpdateOutingPreferencesSuccess',
      outingPreferences: {
        __typename: 'OutingPreferences',
        restaurantCategories?: Array<{
          __typename: 'RestaurantCategory',
          id: string,
          name: string,
          isDefault: boolean
        }> | null,
        activityCategories?: Array<{
          __typename: 'ActivityCategory',
          id: string,
          name: string,
          isDefault: boolean
        }> | null
      }
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type UpdateReserverDetailsMutationVariables = Exact<{
  input: UpdateReserverDetailsInput;
}>;


export type UpdateReserverDetailsMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    updateReserverDetails: {
      __typename: 'UpdateReserverDetailsFailure',
      failureReason: UpdateReserverDetailsFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'UpdateReserverDetailsSuccess',
      reserverDetails: {
        __typename: 'ReserverDetails',
        id: string,
        firstName: string,
        lastName: string,
        phoneNumber: string
      }
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type UpdateReserverDetailsAccountMutationVariables = Exact<{
  accountInput: UpdateAccountInput;
  reserverInput: UpdateReserverDetailsInput;
}>;


export type UpdateReserverDetailsAccountMutation = {
  __typename: 'Mutation',
  viewer: {
    __typename: 'AuthenticatedViewerMutations',
    updateAccount: {
      __typename: 'UpdateAccountFailure',
      failureReason: UpdateAccountFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'UpdateAccountSuccess',
      account: {
        __typename: 'Account',
        id: string,
        email: string,
        stripeCustomerId?: string | null
      }
    },
    updateReserverDetails: {
      __typename: 'UpdateReserverDetailsFailure',
      failureReason: UpdateReserverDetailsFailureReason,
      validationErrors?: Array<{
        __typename: 'ValidationError',
        field: string
      }> | null
    } | {
      __typename: 'UpdateReserverDetailsSuccess',
      reserverDetails: {
        __typename: 'ReserverDetails',
        id: string,
        firstName: string,
        lastName: string,
        phoneNumber: string
      }
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type BillingPortalUrlQueryVariables = Exact<{ [key: string]: never; }>;


export type BillingPortalUrlQuery = {
  __typename: 'Query',
  viewer: {
    __typename: 'AuthenticatedViewerQueries',
    billingPortalUrl: string
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type BookedOutingsQueryVariables = Exact<{ [key: string]: never; }>;


export type BookedOutingsQuery = {
  __typename: 'Query',
  viewer: {
    __typename: 'AuthenticatedViewerQueries',
    bookedOutings: Array<{
      __typename: 'BookingDetailsPeek',
      id: string,
      activityStartTime?: string | null,
      restaurantArrivalTime?: string | null,
      activityName?: string | null,
      restaurantName?: string | null,
      photoUri?: string | null,
      state: BookingState
    }>
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type BookingDetailsQueryVariables = Exact<{
  input: GetBookingDetailsQueryInput;
}>;


export type BookingDetailsQuery = {
  __typename: 'Query',
  viewer: {
    __typename: 'AuthenticatedViewerQueries',
    bookedOutingDetails?: {
      __typename: 'BookingDetails',
      id: string,
      startTime: string,
      headcount: number,
      survey?: {
        __typename: 'Survey',
        id: string,
        budget: OutingBudget,
        headcount: number,
        startTime: string,
        searchRegions: Array<{
          __typename: 'SearchRegion',
          id: string,
          name: string
        }>
      } | null,
      searchRegions: Array<{
        __typename: 'SearchRegion',
        id: string,
        name: string
      }>,
      costBreakdown: {
        __typename: 'CostBreakdown',
        baseCostCents: number,
        feeCents: number,
        taxCents: number,
        totalCostCents: number
      },
      activityPlan?: {
        __typename: 'ActivityPlan',
        startTime: string,
        headcount: number,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        },
        activity: {
          __typename: 'Activity',
          sourceId: string,
          source: ActivitySource,
          isBookable: boolean,
          name: string,
          description?: string | null,
          websiteUri?: string | null,
          doorTips?: string | null,
          insiderTips?: string | null,
          parkingTips?: string | null,
          primaryTypeName?: string | null,
          categoryGroup?: {
            __typename: 'ActivityCategoryGroup',
            id: string,
            name: string,
            activityCategories: Array<{
              __typename: 'ActivityCategory',
              id: string,
              name: string,
              isDefault: boolean
            }>
          } | null,
          ticketInfo?: {
            __typename: 'TicketInfo',
            name?: string | null,
            notes?: string | null,
            costBreakdown: {
              __typename: 'CostBreakdown',
              baseCostCents: number,
              feeCents: number,
              taxCents: number,
              totalCostCents: number
            }
          } | null,
          venue: {
            __typename: 'ActivityVenue',
            name: string,
            location: {
              __typename: 'Location',
              directionsUri?: string | null,
              coordinates: {
                __typename: 'GeoPoint',
                lat: number,
                lon: number
              },
              address: {
                __typename: 'Address',
                address1?: string | null,
                address2?: string | null,
                city?: string | null,
                state?: string | null,
                zipCode?: string | null,
                country?: string | null,
                formattedMultiline: string,
                formattedSingleline: string
              },
              searchRegion: {
                __typename: 'SearchRegion',
                id: string,
                name: string
              }
            }
          },
          photos: {
            __typename: 'Photos',
            coverPhoto?: {
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            } | null,
            supplementalPhotos: Array<{
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            }>
          }
        }
      } | null,
      reservation?: {
        __typename: 'Reservation',
        arrivalTime: string,
        headcount: number,
        costBreakdown: {
          __typename: 'CostBreakdown',
          baseCostCents: number,
          feeCents: number,
          taxCents: number,
          totalCostCents: number
        },
        restaurant: {
          __typename: 'Restaurant',
          sourceId: string,
          source: RestaurantSource,
          name: string,
          reservable: boolean,
          rating: number,
          primaryTypeName: string,
          websiteUri?: string | null,
          description: string,
          parkingTips?: string | null,
          customerFavorites?: string | null,
          location: {
            __typename: 'Location',
            directionsUri?: string | null,
            coordinates: {
              __typename: 'GeoPoint',
              lat: number,
              lon: number
            },
            address: {
              __typename: 'Address',
              address1?: string | null,
              address2?: string | null,
              city?: string | null,
              state?: string | null,
              zipCode?: string | null,
              country?: string | null,
              formattedMultiline: string,
              formattedSingleline: string
            },
            searchRegion: {
              __typename: 'SearchRegion',
              id: string,
              name: string
            }
          },
          photos: {
            __typename: 'Photos',
            coverPhoto?: {
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            } | null,
            supplementalPhotos: Array<{
              __typename: 'Photo',
              id: string,
              src: string,
              alt?: string | null,
              attributions: Array<string>
            }>
          }
        }
      } | null,
      travel?: {
        __typename: 'TravelInfo',
        durationMinutes: number
      } | null
    } | null
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type OneClickBookingCriteriaQueryVariables = Exact<{ [key: string]: never; }>;


export type OneClickBookingCriteriaQuery = {
  __typename: 'Query',
  viewer: {
    __typename: 'AuthenticatedViewerQueries',
    reserverDetails: Array<{
      __typename: 'ReserverDetails',
      id: string,
      firstName: string,
      lastName: string,
      phoneNumber: string
    }>,
    paymentMethods: Array<{
      __typename: 'PaymentMethod',
      id: string,
      card?: {
        __typename: 'PaymentCard',
        brand: string,
        last4: string,
        expMonth: number,
        expYear: number
      } | null
    }>
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type OutingQueryVariables = Exact<{
  input: OutingInput;
}>;


export type OutingQuery = {
  __typename: 'Query',
  outing?: {
    __typename: 'Outing',
    id: string,
    startTime: string,
    headcount: number,
    survey?: {
      __typename: 'Survey',
      id: string,
      budget: OutingBudget,
      headcount: number,
      startTime: string,
      searchRegions: Array<{
        __typename: 'SearchRegion',
        id: string,
        name: string
      }>
    } | null,
    searchRegions: Array<{
      __typename: 'SearchRegion',
      id: string,
      name: string
    }>,
    costBreakdown: {
      __typename: 'CostBreakdown',
      baseCostCents: number,
      feeCents: number,
      taxCents: number,
      totalCostCents: number
    },
    activityPlan?: {
      __typename: 'ActivityPlan',
      startTime: string,
      headcount: number,
      costBreakdown: {
        __typename: 'CostBreakdown',
        baseCostCents: number,
        feeCents: number,
        taxCents: number,
        totalCostCents: number
      },
      activity: {
        __typename: 'Activity',
        sourceId: string,
        source: ActivitySource,
        isBookable: boolean,
        name: string,
        description?: string | null,
        websiteUri?: string | null,
        doorTips?: string | null,
        insiderTips?: string | null,
        parkingTips?: string | null,
        primaryTypeName?: string | null,
        categoryGroup?: {
          __typename: 'ActivityCategoryGroup',
          id: string,
          name: string,
          activityCategories: Array<{
            __typename: 'ActivityCategory',
            id: string,
            name: string,
            isDefault: boolean
          }>
        } | null,
        ticketInfo?: {
          __typename: 'TicketInfo',
          name?: string | null,
          notes?: string | null,
          costBreakdown: {
            __typename: 'CostBreakdown',
            baseCostCents: number,
            feeCents: number,
            taxCents: number,
            totalCostCents: number
          }
        } | null,
        venue: {
          __typename: 'ActivityVenue',
          name: string,
          location: {
            __typename: 'Location',
            directionsUri?: string | null,
            coordinates: {
              __typename: 'GeoPoint',
              lat: number,
              lon: number
            },
            address: {
              __typename: 'Address',
              address1?: string | null,
              address2?: string | null,
              city?: string | null,
              state?: string | null,
              zipCode?: string | null,
              country?: string | null,
              formattedMultiline: string,
              formattedSingleline: string
            },
            searchRegion: {
              __typename: 'SearchRegion',
              id: string,
              name: string
            }
          }
        },
        photos: {
          __typename: 'Photos',
          coverPhoto?: {
            __typename: 'Photo',
            id: string,
            src: string,
            alt?: string | null,
            attributions: Array<string>
          } | null,
          supplementalPhotos: Array<{
            __typename: 'Photo',
            id: string,
            src: string,
            alt?: string | null,
            attributions: Array<string>
          }>
        }
      }
    } | null,
    reservation?: {
      __typename: 'Reservation',
      arrivalTime: string,
      headcount: number,
      costBreakdown: {
        __typename: 'CostBreakdown',
        baseCostCents: number,
        feeCents: number,
        taxCents: number,
        totalCostCents: number
      },
      restaurant: {
        __typename: 'Restaurant',
        sourceId: string,
        source: RestaurantSource,
        name: string,
        reservable: boolean,
        rating: number,
        primaryTypeName: string,
        websiteUri?: string | null,
        description: string,
        parkingTips?: string | null,
        customerFavorites?: string | null,
        location: {
          __typename: 'Location',
          directionsUri?: string | null,
          coordinates: {
            __typename: 'GeoPoint',
            lat: number,
            lon: number
          },
          address: {
            __typename: 'Address',
            address1?: string | null,
            address2?: string | null,
            city?: string | null,
            state?: string | null,
            zipCode?: string | null,
            country?: string | null,
            formattedMultiline: string,
            formattedSingleline: string
          },
          searchRegion: {
            __typename: 'SearchRegion',
            id: string,
            name: string
          }
        },
        photos: {
          __typename: 'Photos',
          coverPhoto?: {
            __typename: 'Photo',
            id: string,
            src: string,
            alt?: string | null,
            attributions: Array<string>
          } | null,
          supplementalPhotos: Array<{
            __typename: 'Photo',
            id: string,
            src: string,
            alt?: string | null,
            attributions: Array<string>
          }>
        }
      }
    } | null,
    travel?: {
      __typename: 'TravelInfo',
      durationMinutes: number
    } | null
  } | null
};

export type OutingPreferencesQueryVariables = Exact<{ [key: string]: never; }>;


export type OutingPreferencesQuery = {
  __typename: 'Query',
  activityCategoryGroups: Array<{
    __typename: 'ActivityCategoryGroup',
    id: string,
    name: string,
    activityCategories: Array<{
      __typename: 'ActivityCategory',
      id: string,
      name: string,
      isDefault: boolean
    }>
  }>,
  restaurantCategories: Array<{
    __typename: 'RestaurantCategory',
    id: string,
    name: string,
    isDefault: boolean
  }>,
  viewer: {
    __typename: 'AuthenticatedViewerQueries',
    outingPreferences: {
      __typename: 'OutingPreferences',
      restaurantCategories?: Array<{
        __typename: 'RestaurantCategory',
        id: string,
        name: string,
        isDefault: boolean
      }> | null,
      activityCategories?: Array<{
        __typename: 'ActivityCategory',
        id: string,
        name: string,
        isDefault: boolean
      }> | null
    }
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type ReserverDetailsQueryVariables = Exact<{ [key: string]: never; }>;


export type ReserverDetailsQuery = {
  __typename: 'Query',
  viewer: {
    __typename: 'AuthenticatedViewerQueries',
    reserverDetails: Array<{
      __typename: 'ReserverDetails',
      id: string,
      firstName: string,
      lastName: string,
      phoneNumber: string
    }>
  } | {
    __typename: 'UnauthenticatedViewer',
    authFailureReason: AuthenticationFailureReason
  }
};

export type SearchRegionsQueryVariables = Exact<{ [key: string]: never; }>;


export type SearchRegionsQuery = {
  __typename: 'Query',
  searchRegions: Array<{
    __typename: 'SearchRegion',
    id: string,
    name: string
  }>
};

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
export const AccountFieldsFragmentDoc = new TypedDocumentString(`
    fragment AccountFields on Account {
  __typename
  id
  email
  stripeCustomerId
}
    `, {"fragmentName":"AccountFields"}) as unknown as TypedDocumentString<AccountFieldsFragment, unknown>;
export const ReserverDetailsFieldsFragmentDoc = new TypedDocumentString(`
    fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}
    `, {"fragmentName":"ReserverDetailsFields"}) as unknown as TypedDocumentString<ReserverDetailsFieldsFragment, unknown>;
export const BookingFieldsFragmentDoc = new TypedDocumentString(`
    fragment BookingFields on Booking {
  __typename
  id
  state
  reserverDetails {
    __typename
    ...ReserverDetailsFields
  }
}
    fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`, {"fragmentName":"BookingFields"}) as unknown as TypedDocumentString<BookingFieldsFragment, unknown>;
export const BookingDetailsPeekFieldsFragmentDoc = new TypedDocumentString(`
    fragment BookingDetailsPeekFields on BookingDetailsPeek {
  __typename
  id
  activityStartTime
  restaurantArrivalTime
  activityName
  restaurantName
  photoUri
  state
}
    `, {"fragmentName":"BookingDetailsPeekFields"}) as unknown as TypedDocumentString<BookingDetailsPeekFieldsFragment, unknown>;
export const ActivityCategoryFieldsFragmentDoc = new TypedDocumentString(`
    fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
    `, {"fragmentName":"ActivityCategoryFields"}) as unknown as TypedDocumentString<ActivityCategoryFieldsFragment, unknown>;
export const ActivityCategoryGroupFieldsFragmentDoc = new TypedDocumentString(`
    fragment ActivityCategoryGroupFields on ActivityCategoryGroup {
  __typename
  id
  name
  activityCategories {
    __typename
    ...ActivityCategoryFields
  }
}
    fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}`, {"fragmentName":"ActivityCategoryGroupFields"}) as unknown as TypedDocumentString<ActivityCategoryGroupFieldsFragment, unknown>;
export const CustomerSessionFieldsFragmentDoc = new TypedDocumentString(`
    fragment CustomerSessionFields on CustomerSession {
  __typename
  clientSecret
}
    `, {"fragmentName":"CustomerSessionFields"}) as unknown as TypedDocumentString<CustomerSessionFieldsFragment, unknown>;
export const SearchRegionFieldsFragmentDoc = new TypedDocumentString(`
    fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}
    `, {"fragmentName":"SearchRegionFields"}) as unknown as TypedDocumentString<SearchRegionFieldsFragment, unknown>;
export const SurveyFieldsFragmentDoc = new TypedDocumentString(`
    fragment SurveyFields on Survey {
  __typename
  id
  budget
  headcount
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  startTime
}
    fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}`, {"fragmentName":"SurveyFields"}) as unknown as TypedDocumentString<SurveyFieldsFragment, unknown>;
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
    ...SearchRegionFields
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
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
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
export const PhotosFieldsFragmentDoc = new TypedDocumentString(`
    fragment PhotosFields on Photos {
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
    fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}`, {"fragmentName":"PhotosFields"}) as unknown as TypedDocumentString<PhotosFieldsFragment, unknown>;
export const ActivityFieldsFragmentDoc = new TypedDocumentString(`
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
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
    ...SearchRegionFields
  }
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}`, {"fragmentName":"ActivityFields"}) as unknown as TypedDocumentString<ActivityFieldsFragment, unknown>;
export const ActivityPlanFieldsFragmentDoc = new TypedDocumentString(`
    fragment ActivityPlanFields on ActivityPlan {
  __typename
  startTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    ...ActivityFields
  }
}
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
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
    ...SearchRegionFields
  }
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}`, {"fragmentName":"ActivityPlanFields"}) as unknown as TypedDocumentString<ActivityPlanFieldsFragment, unknown>;
export const ReservationFieldsFragmentDoc = new TypedDocumentString(`
    fragment ReservationFields on Reservation {
  __typename
  arrivalTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
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
    ...SearchRegionFields
  }
}
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}`, {"fragmentName":"ReservationFields"}) as unknown as TypedDocumentString<ReservationFieldsFragment, unknown>;
export const ItineraryFieldsFragmentDoc = new TypedDocumentString(`
    fragment ItineraryFields on Itinerary {
  __typename
  id
  startTime
  headcount
  survey {
    __typename
    ...SurveyFields
  }
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activityPlan {
    __typename
    ...ActivityPlanFields
  }
  reservation {
    __typename
    ...ReservationFields
  }
}
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
  }
}
fragment ActivityPlanFields on ActivityPlan {
  __typename
  startTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    ...ActivityFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
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
    ...SearchRegionFields
  }
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment ReservationFields on Reservation {
  __typename
  arrivalTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
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
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}
fragment SurveyFields on Survey {
  __typename
  id
  budget
  headcount
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  startTime
}`, {"fragmentName":"ItineraryFields"}) as unknown as TypedDocumentString<ItineraryFieldsFragment, unknown>;
export const TravelFieldsFragmentDoc = new TypedDocumentString(`
    fragment TravelFields on Itinerary {
  __typename
  travel {
    __typename
    durationMinutes
  }
}
    `, {"fragmentName":"TravelFields"}) as unknown as TypedDocumentString<TravelFieldsFragment, unknown>;
export const RestaurantCategoryFieldsFragmentDoc = new TypedDocumentString(`
    fragment RestaurantCategoryFields on RestaurantCategory {
  __typename
  id
  name
  isDefault
}
    `, {"fragmentName":"RestaurantCategoryFields"}) as unknown as TypedDocumentString<RestaurantCategoryFieldsFragment, unknown>;
export const OutingPreferencesFieldsFragmentDoc = new TypedDocumentString(`
    fragment OutingPreferencesFields on OutingPreferences {
  __typename
  restaurantCategories {
    __typename
    ...RestaurantCategoryFields
  }
  activityCategories {
    __typename
    ...ActivityCategoryFields
  }
}
    fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment RestaurantCategoryFields on RestaurantCategory {
  __typename
  id
  name
  isDefault
}`, {"fragmentName":"OutingPreferencesFields"}) as unknown as TypedDocumentString<OutingPreferencesFieldsFragment, unknown>;
export const PaymentIntentFieldsFragmentDoc = new TypedDocumentString(`
    fragment PaymentIntentFields on PaymentIntent {
  __typename
  id
  clientSecret
}
    `, {"fragmentName":"PaymentIntentFields"}) as unknown as TypedDocumentString<PaymentIntentFieldsFragment, unknown>;
export const PaymentMethodFieldsFragmentDoc = new TypedDocumentString(`
    fragment PaymentMethodFields on PaymentMethod {
  __typename
  id
  card {
    __typename
    brand
    last4
    expMonth
    expYear
  }
}
    `, {"fragmentName":"PaymentMethodFields"}) as unknown as TypedDocumentString<PaymentMethodFieldsFragment, unknown>;
export const ConfirmBookingDocument = new TypedDocumentString(`
    mutation ConfirmBooking($input: ConfirmBookingInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      confirmBooking(input: $input) {
        __typename
        ... on ConfirmBookingSuccess {
          __typename
          booking {
            __typename
            ...BookingFields
          }
        }
        ... on ConfirmBookingFailure {
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
    ...ReserverDetailsFields
  }
}
fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`) as unknown as TypedDocumentString<ConfirmBookingMutation, ConfirmBookingMutationVariables>;
export const CreateAccountDocument = new TypedDocumentString(`
    mutation CreateAccount($input: CreateAccountInput!) {
  __typename
  createAccount(input: $input) {
    __typename
    ... on CreateAccountSuccess {
      __typename
      account {
        __typename
        ...AccountFields
      }
    }
    ... on CreateAccountFailure {
      __typename
      failureReason
      validationErrors {
        __typename
        field
      }
    }
  }
}
    fragment AccountFields on Account {
  __typename
  id
  email
  stripeCustomerId
}`) as unknown as TypedDocumentString<CreateAccountMutation, CreateAccountMutationVariables>;
export const InitiateBookingDocument = new TypedDocumentString(`
    mutation InitiateBooking($input: InitiateBookingInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      initiateBooking(input: $input) {
        __typename
        ... on InitiateBookingSuccess {
          __typename
          booking {
            __typename
            ...ItineraryFields
          }
          paymentIntent {
            __typename
            ...PaymentIntentFields
          }
          customerSession {
            __typename
            ...CustomerSessionFields
          }
        }
        ... on InitiateBookingFailure {
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
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
  }
}
fragment ActivityPlanFields on ActivityPlan {
  __typename
  startTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    ...ActivityFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
fragment CustomerSessionFields on CustomerSession {
  __typename
  clientSecret
}
fragment ItineraryFields on Itinerary {
  __typename
  id
  startTime
  headcount
  survey {
    __typename
    ...SurveyFields
  }
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activityPlan {
    __typename
    ...ActivityPlanFields
  }
  reservation {
    __typename
    ...ReservationFields
  }
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
    ...SearchRegionFields
  }
}
fragment PaymentIntentFields on PaymentIntent {
  __typename
  id
  clientSecret
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment ReservationFields on Reservation {
  __typename
  arrivalTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
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
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}
fragment SurveyFields on Survey {
  __typename
  id
  budget
  headcount
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  startTime
}`) as unknown as TypedDocumentString<InitiateBookingMutation, InitiateBookingMutationVariables>;
export const LoginDocument = new TypedDocumentString(`
    mutation Login($input: LoginInput!) {
  __typename
  login(input: $input) {
    __typename
    ... on LoginSuccess {
      __typename
      account {
        __typename
        ...AccountFields
      }
    }
    ... on LoginFailure {
      __typename
      failureReason
    }
  }
}
    fragment AccountFields on Account {
  __typename
  id
  email
  stripeCustomerId
}`) as unknown as TypedDocumentString<LoginMutation, LoginMutationVariables>;
export const PlanOutingDocument = new TypedDocumentString(`
    mutation PlanOuting($input: PlanOutingInput!) {
  __typename
  planOuting(input: $input) {
    __typename
    ... on PlanOutingSuccess {
      __typename
      outing {
        __typename
        ...ItineraryFields
        ...TravelFields
      }
    }
    ... on PlanOutingFailure {
      __typename
      failureReason
    }
  }
}
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
  }
}
fragment ActivityPlanFields on ActivityPlan {
  __typename
  startTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    ...ActivityFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
fragment ItineraryFields on Itinerary {
  __typename
  id
  startTime
  headcount
  survey {
    __typename
    ...SurveyFields
  }
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activityPlan {
    __typename
    ...ActivityPlanFields
  }
  reservation {
    __typename
    ...ReservationFields
  }
}
fragment TravelFields on Itinerary {
  __typename
  travel {
    __typename
    durationMinutes
  }
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
    ...SearchRegionFields
  }
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment ReservationFields on Reservation {
  __typename
  arrivalTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
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
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}
fragment SurveyFields on Survey {
  __typename
  id
  budget
  headcount
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  startTime
}`) as unknown as TypedDocumentString<PlanOutingMutation, PlanOutingMutationVariables>;
export const SubmitReserverDetailsDocument = new TypedDocumentString(`
    mutation SubmitReserverDetails($input: SubmitReserverDetailsInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      submitReserverDetails(input: $input) {
        __typename
        ... on SubmitReserverDetailsSuccess {
          __typename
          reserverDetails {
            __typename
            ...ReserverDetailsFields
          }
        }
        ... on SubmitReserverDetailsFailure {
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
    fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`) as unknown as TypedDocumentString<SubmitReserverDetailsMutation, SubmitReserverDetailsMutationVariables>;
export const UpdateAccountDocument = new TypedDocumentString(`
    mutation UpdateAccount($input: UpdateAccountInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      updateAccount(input: $input) {
        __typename
        ... on UpdateAccountSuccess {
          __typename
          account {
            __typename
            ...AccountFields
          }
        }
        ... on UpdateAccountFailure {
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
    fragment AccountFields on Account {
  __typename
  id
  email
  stripeCustomerId
}`) as unknown as TypedDocumentString<UpdateAccountMutation, UpdateAccountMutationVariables>;
export const UpdateOutingPreferencesDocument = new TypedDocumentString(`
    mutation UpdateOutingPreferences($input: UpdateOutingPreferencesInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      updatePreferences(input: $input) {
        __typename
        ... on UpdateOutingPreferencesSuccess {
          __typename
          outingPreferences {
            __typename
            ...OutingPreferencesFields
          }
        }
        ... on UpdateOutingPreferencesFailure {
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
    fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment RestaurantCategoryFields on RestaurantCategory {
  __typename
  id
  name
  isDefault
}
fragment OutingPreferencesFields on OutingPreferences {
  __typename
  restaurantCategories {
    __typename
    ...RestaurantCategoryFields
  }
  activityCategories {
    __typename
    ...ActivityCategoryFields
  }
}`) as unknown as TypedDocumentString<UpdateOutingPreferencesMutation, UpdateOutingPreferencesMutationVariables>;
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
            ...ReserverDetailsFields
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
    fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`) as unknown as TypedDocumentString<UpdateReserverDetailsMutation, UpdateReserverDetailsMutationVariables>;
export const UpdateReserverDetailsAccountDocument = new TypedDocumentString(`
    mutation UpdateReserverDetailsAccount($accountInput: UpdateAccountInput!, $reserverInput: UpdateReserverDetailsInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerMutations {
      __typename
      updateAccount(input: $accountInput) {
        __typename
        ... on UpdateAccountSuccess {
          __typename
          account {
            __typename
            ...AccountFields
          }
        }
        ... on UpdateAccountFailure {
          __typename
          failureReason
          validationErrors {
            __typename
            field
          }
        }
      }
      updateReserverDetails(input: $reserverInput) {
        __typename
        ... on UpdateReserverDetailsSuccess {
          __typename
          reserverDetails {
            __typename
            ...ReserverDetailsFields
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
    fragment AccountFields on Account {
  __typename
  id
  email
  stripeCustomerId
}
fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`) as unknown as TypedDocumentString<UpdateReserverDetailsAccountMutation, UpdateReserverDetailsAccountMutationVariables>;
export const BillingPortalUrlDocument = new TypedDocumentString(`
    query BillingPortalUrl {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      billingPortalUrl
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    `) as unknown as TypedDocumentString<BillingPortalUrlQuery, BillingPortalUrlQueryVariables>;
export const BookedOutingsDocument = new TypedDocumentString(`
    query BookedOutings {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      bookedOutings {
        __typename
        ...BookingDetailsPeekFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment BookingDetailsPeekFields on BookingDetailsPeek {
  __typename
  id
  activityStartTime
  restaurantArrivalTime
  activityName
  restaurantName
  photoUri
  state
}`) as unknown as TypedDocumentString<BookedOutingsQuery, BookedOutingsQueryVariables>;
export const BookingDetailsDocument = new TypedDocumentString(`
    query BookingDetails($input: GetBookingDetailsQueryInput!) {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      bookedOutingDetails(input: $input) {
        __typename
        ...ItineraryFields
        ...TravelFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
  }
}
fragment ActivityPlanFields on ActivityPlan {
  __typename
  startTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    ...ActivityFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
fragment ItineraryFields on Itinerary {
  __typename
  id
  startTime
  headcount
  survey {
    __typename
    ...SurveyFields
  }
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activityPlan {
    __typename
    ...ActivityPlanFields
  }
  reservation {
    __typename
    ...ReservationFields
  }
}
fragment TravelFields on Itinerary {
  __typename
  travel {
    __typename
    durationMinutes
  }
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
    ...SearchRegionFields
  }
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment ReservationFields on Reservation {
  __typename
  arrivalTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
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
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}
fragment SurveyFields on Survey {
  __typename
  id
  budget
  headcount
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  startTime
}`) as unknown as TypedDocumentString<BookingDetailsQuery, BookingDetailsQueryVariables>;
export const OneClickBookingCriteriaDocument = new TypedDocumentString(`
    query OneClickBookingCriteria {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      reserverDetails {
        __typename
        ...ReserverDetailsFields
      }
      paymentMethods {
        __typename
        ...PaymentMethodFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment PaymentMethodFields on PaymentMethod {
  __typename
  id
  card {
    __typename
    brand
    last4
    expMonth
    expYear
  }
}
fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`) as unknown as TypedDocumentString<OneClickBookingCriteriaQuery, OneClickBookingCriteriaQueryVariables>;
export const OutingDocument = new TypedDocumentString(`
    query Outing($input: OutingInput!) {
  __typename
  outing(input: $input) {
    __typename
    ...ItineraryFields
    ...TravelFields
  }
}
    fragment ActivityFields on Activity {
  __typename
  categoryGroup {
    __typename
    id
    name
    activityCategories {
      __typename
      ...ActivityCategoryFields
    }
  }
  sourceId
  source
  isBookable
  name
  description
  websiteUri
  doorTips
  insiderTips
  parkingTips
  primaryTypeName
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
    ...PhotosFields
  }
}
fragment ActivityPlanFields on ActivityPlan {
  __typename
  startTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activity {
    __typename
    ...ActivityFields
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
fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment CostBreakdownFields on CostBreakdown {
  __typename
  baseCostCents
  feeCents
  taxCents
  totalCostCents
}
fragment ItineraryFields on Itinerary {
  __typename
  id
  startTime
  headcount
  survey {
    __typename
    ...SurveyFields
  }
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  costBreakdown {
    __typename
    ...CostBreakdownFields
  }
  activityPlan {
    __typename
    ...ActivityPlanFields
  }
  reservation {
    __typename
    ...ReservationFields
  }
}
fragment TravelFields on Itinerary {
  __typename
  travel {
    __typename
    durationMinutes
  }
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
    ...SearchRegionFields
  }
}
fragment PhotosFields on Photos {
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
fragment PhotoFields on Photo {
  __typename
  id
  src
  alt
  attributions
}
fragment ReservationFields on Reservation {
  __typename
  arrivalTime
  headcount
  costBreakdown {
    __typename
    ...CostBreakdownFields
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
fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}
fragment SurveyFields on Survey {
  __typename
  id
  budget
  headcount
  searchRegions {
    __typename
    ...SearchRegionFields
  }
  startTime
}`) as unknown as TypedDocumentString<OutingQuery, OutingQueryVariables>;
export const OutingPreferencesDocument = new TypedDocumentString(`
    query OutingPreferences {
  __typename
  activityCategoryGroups {
    __typename
    ...ActivityCategoryGroupFields
  }
  restaurantCategories {
    __typename
    ...RestaurantCategoryFields
  }
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      outingPreferences {
        __typename
        ...OutingPreferencesFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment ActivityCategoryFields on ActivityCategory {
  __typename
  id
  name
  isDefault
}
fragment ActivityCategoryGroupFields on ActivityCategoryGroup {
  __typename
  id
  name
  activityCategories {
    __typename
    ...ActivityCategoryFields
  }
}
fragment RestaurantCategoryFields on RestaurantCategory {
  __typename
  id
  name
  isDefault
}
fragment OutingPreferencesFields on OutingPreferences {
  __typename
  restaurantCategories {
    __typename
    ...RestaurantCategoryFields
  }
  activityCategories {
    __typename
    ...ActivityCategoryFields
  }
}`) as unknown as TypedDocumentString<OutingPreferencesQuery, OutingPreferencesQueryVariables>;
export const ReserverDetailsDocument = new TypedDocumentString(`
    query ReserverDetails {
  __typename
  viewer {
    __typename
    ... on AuthenticatedViewerQueries {
      __typename
      reserverDetails {
        __typename
        ...ReserverDetailsFields
      }
    }
    ... on UnauthenticatedViewer {
      __typename
      authFailureReason
    }
  }
}
    fragment ReserverDetailsFields on ReserverDetails {
  __typename
  id
  firstName
  lastName
  phoneNumber
}`) as unknown as TypedDocumentString<ReserverDetailsQuery, ReserverDetailsQueryVariables>;
export const SearchRegionsDocument = new TypedDocumentString(`
    query SearchRegions {
  __typename
  searchRegions {
    __typename
    ...SearchRegionFields
  }
}
    fragment SearchRegionFields on SearchRegion {
  __typename
  id
  name
}`) as unknown as TypedDocumentString<SearchRegionsQuery, SearchRegionsQueryVariables>;