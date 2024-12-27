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
  /** Date with time (isoformat) */
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

export type AdminBookingInfo = {
  __typename?: 'AdminBookingInfo';
  accounts: Array<Account>;
  activityBookingLink?: Maybe<Scalars['String']['output']>;
  activityName?: Maybe<Scalars['String']['output']>;
  activitySource?: Maybe<ActivitySource>;
  activitySourceId?: Maybe<Scalars['String']['output']>;
  activityStartTime?: Maybe<Scalars['DateTime']['output']>;
  id: Scalars['UUID']['output'];
  reserverDetails?: Maybe<ReserverDetails>;
  restaurantArrivalTime?: Maybe<Scalars['DateTime']['output']>;
  restaurantBookingLink?: Maybe<Scalars['String']['output']>;
  restaurantName?: Maybe<Scalars['String']['output']>;
  restaurantSource?: Maybe<RestaurantSource>;
  restaurantSourceId?: Maybe<Scalars['String']['output']>;
  state: BookingState;
  stripePaymentId?: Maybe<Scalars['String']['output']>;
  survey?: Maybe<Survey>;
};

export type AdminUpdateBookingFailure = {
  __typename?: 'AdminUpdateBookingFailure';
  failureReason: AdminUpdateBookingFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum AdminUpdateBookingFailureReason {
  ActivitySourceNotFound = 'ACTIVITY_SOURCE_NOT_FOUND',
  BookingNotFound = 'BOOKING_NOT_FOUND',
  RestaurantSourceNotFound = 'RESTAURANT_SOURCE_NOT_FOUND',
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type AdminUpdateBookingInput = {
  activityHeadcount?: InputMaybe<Scalars['Int']['input']>;
  activitySource?: InputMaybe<ActivitySource>;
  activitySourceId?: InputMaybe<Scalars['String']['input']>;
  activityStartTimeUtc?: InputMaybe<Scalars['DateTime']['input']>;
  bookingId: Scalars['UUID']['input'];
  restaurantHeadcount?: InputMaybe<Scalars['Int']['input']>;
  restaurantSource?: InputMaybe<RestaurantSource>;
  restaurantSourceId?: InputMaybe<Scalars['String']['input']>;
  restaurantStartTimeUtc?: InputMaybe<Scalars['DateTime']['input']>;
  state?: InputMaybe<BookingState>;
};

export type AdminUpdateBookingResult = AdminUpdateBookingFailure | AdminUpdateBookingSuccess;

export type AdminUpdateBookingSuccess = {
  __typename?: 'AdminUpdateBookingSuccess';
  booking: Booking;
};

export type AdminUpdateReserverDetailsFailure = {
  __typename?: 'AdminUpdateReserverDetailsFailure';
  failureReason: AdminUpdateReserverDetailsFailureReason;
  validationErrors?: Maybe<Array<ValidationError>>;
};

export enum AdminUpdateReserverDetailsFailureReason {
  ReserverDetailsNotFound = 'RESERVER_DETAILS_NOT_FOUND',
  ValidationErrors = 'VALIDATION_ERRORS'
}

export type AdminUpdateReserverDetailsInput = {
  firstName: Scalars['String']['input'];
  id: Scalars['UUID']['input'];
  lastName: Scalars['String']['input'];
  phoneNumber: Scalars['String']['input'];
};

export type AdminUpdateReserverDetailsResult = AdminUpdateReserverDetailsFailure | AdminUpdateReserverDetailsSuccess;

export type AdminUpdateReserverDetailsSuccess = {
  __typename?: 'AdminUpdateReserverDetailsSuccess';
  reserverDetails: ReserverDetails;
};

export type Booking = {
  __typename?: 'Booking';
  id: Scalars['UUID']['output'];
  reserverDetails?: Maybe<ReserverDetails>;
  state: BookingState;
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

export type CostBreakdown = {
  __typename?: 'CostBreakdown';
  baseCostCents: Scalars['Int']['output'];
  feeCents: Scalars['Int']['output'];
  taxCents: Scalars['Int']['output'];
  totalCostCents: Scalars['Int']['output'];
};

export type GeoPoint = {
  __typename?: 'GeoPoint';
  lat: Scalars['Float']['output'];
  lon: Scalars['Float']['output'];
};

export type Location = {
  __typename?: 'Location';
  address: Address;
  coordinates: GeoPoint;
  directionsUri?: Maybe<Scalars['String']['output']>;
  searchRegion: SearchRegion;
};

export type Mutation = {
  __typename?: 'Mutation';
  adminUpdateBooking: AdminUpdateBookingResult;
  adminUpdateReserverDetails: AdminUpdateReserverDetailsResult;
};


export type MutationAdminUpdateBookingArgs = {
  input: AdminUpdateBookingInput;
};


export type MutationAdminUpdateReserverDetailsArgs = {
  input: AdminUpdateReserverDetailsInput;
};

export enum OutingBudget {
  Expensive = 'EXPENSIVE',
  Free = 'FREE',
  Inexpensive = 'INEXPENSIVE',
  Moderate = 'MODERATE',
  VeryExpensive = 'VERY_EXPENSIVE'
}

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

export type Query = {
  __typename?: 'Query';
  adminBooking?: Maybe<AdminBookingInfo>;
  adminBookingActivityDetail?: Maybe<Activity>;
  adminBookingRestaurantDetail?: Maybe<Restaurant>;
  adminBookings: Array<BookingDetailsPeek>;
  adminReserverDetails?: Maybe<ReserverDetails>;
};


export type QueryAdminBookingArgs = {
  bookingId: Scalars['UUID']['input'];
};


export type QueryAdminBookingActivityDetailArgs = {
  bookingId: Scalars['UUID']['input'];
};


export type QueryAdminBookingRestaurantDetailArgs = {
  bookingId: Scalars['UUID']['input'];
};


export type QueryAdminBookingsArgs = {
  accountId: Scalars['UUID']['input'];
};


export type QueryAdminReserverDetailsArgs = {
  reserverDetailsId: Scalars['UUID']['input'];
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

export enum RestaurantSource {
  GooglePlaces = 'GOOGLE_PLACES'
}

export type SearchRegion = {
  __typename?: 'SearchRegion';
  id: Scalars['UUID']['output'];
  name: Scalars['String']['output'];
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

export type ValidationError = {
  __typename?: 'ValidationError';
  field: Scalars['String']['output'];
  subject: Scalars['String']['output'];
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

export type CostBreakdownFieldsFragment = {
  __typename: 'CostBreakdown',
  baseCostCents: number,
  feeCents: number,
  taxCents: number,
  totalCostCents: number
};

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

export type PhotoFieldsFragment = {
  __typename: 'Photo',
  id: string,
  src: string,
  alt?: string | null,
  attributions: Array<string>
};

export type UpdateBookingMutationVariables = Exact<{
  input: AdminUpdateBookingInput;
}>;


export type UpdateBookingMutation = {
  __typename: 'Mutation',
  adminUpdateBooking: {
    __typename: 'AdminUpdateBookingFailure',
    failureReason: AdminUpdateBookingFailureReason,
    validationErrors?: Array<{
      __typename: 'ValidationError',
      field: string
    }> | null
  } | {
    __typename: 'AdminUpdateBookingSuccess',
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
};

export type UpdateReserverDetailsMutationVariables = Exact<{
  input: AdminUpdateReserverDetailsInput;
}>;


export type UpdateReserverDetailsMutation = {
  __typename: 'Mutation',
  adminUpdateReserverDetails: {
    __typename: 'AdminUpdateReserverDetailsFailure',
    failureReason: AdminUpdateReserverDetailsFailureReason,
    validationErrors?: Array<{
      __typename: 'ValidationError',
      field: string
    }> | null
  } | {
    __typename: 'AdminUpdateReserverDetailsSuccess',
    reserverDetails: {
      __typename: 'ReserverDetails',
      id: string,
      firstName: string,
      lastName: string,
      phoneNumber: string
    }
  }
};

export type AdminBookingInfoQueryVariables = Exact<{
  bookingId: Scalars['UUID']['input'];
}>;


export type AdminBookingInfoQuery = {
  __typename: 'Query',
  adminBooking?: {
    __typename: 'AdminBookingInfo',
    id: string,
    activityStartTime?: string | null,
    activityName?: string | null,
    activityBookingLink?: string | null,
    activitySource?: ActivitySource | null,
    activitySourceId?: string | null,
    restaurantArrivalTime?: string | null,
    restaurantName?: string | null,
    restaurantBookingLink?: string | null,
    restaurantSource?: RestaurantSource | null,
    restaurantSourceId?: string | null,
    state: BookingState,
    stripePaymentId?: string | null,
    accounts: Array<{
      __typename: 'Account',
      id: string,
      email: string
    }>,
    reserverDetails?: {
      __typename: 'ReserverDetails',
      id: string,
      firstName: string,
      lastName: string,
      phoneNumber: string
    } | null,
    survey?: {
      __typename: 'Survey',
      id: string,
      headcount: number,
      budget: OutingBudget,
      startTime: string,
      searchRegions: Array<{
        __typename: 'SearchRegion',
        id: string,
        name: string
      }>
    } | null
  } | null,
  adminBookingActivityDetail?: {
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
  } | null,
  adminBookingRestaurantDetail?: {
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
  } | null
};

export type ListBookedOutingsQueryVariables = Exact<{
  accountId: Scalars['UUID']['input'];
}>;


export type ListBookedOutingsQuery = {
  __typename: 'Query',
  adminBookings: Array<{
    __typename: 'BookingDetailsPeek',
    id: string,
    activityStartTime?: string | null,
    restaurantArrivalTime?: string | null,
    activityName?: string | null,
    restaurantName?: string | null,
    photoUri?: string | null,
    state: BookingState
  }>
};

export type ReserverDetailsQueryVariables = Exact<{
  reserverDetailsId: Scalars['UUID']['input'];
}>;


export type ReserverDetailsQuery = {
  __typename: 'Query',
  adminReserverDetails?: {
    __typename: 'ReserverDetails',
    id: string,
    firstName: string,
    lastName: string,
    phoneNumber: string
  } | null
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
export const UpdateBookingDocument = new TypedDocumentString(`
    mutation UpdateBooking($input: AdminUpdateBookingInput!) {
  __typename
  adminUpdateBooking(input: $input) {
    __typename
    ... on AdminUpdateBookingSuccess {
      __typename
      booking {
        __typename
        ...BookingFields
      }
    }
    ... on AdminUpdateBookingFailure {
      __typename
      failureReason
      validationErrors {
        __typename
        field
      }
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
    mutation UpdateReserverDetails($input: AdminUpdateReserverDetailsInput!) {
  __typename
  adminUpdateReserverDetails(input: $input) {
    __typename
    ... on AdminUpdateReserverDetailsSuccess {
      __typename
      reserverDetails {
        __typename
        id
        firstName
        lastName
        phoneNumber
      }
    }
    ... on AdminUpdateReserverDetailsFailure {
      __typename
      failureReason
      validationErrors {
        __typename
        field
      }
    }
  }
}
    `) as unknown as TypedDocumentString<UpdateReserverDetailsMutation, UpdateReserverDetailsMutationVariables>;
export const AdminBookingInfoDocument = new TypedDocumentString(`
    query AdminBookingInfo($bookingId: UUID!) {
  __typename
  adminBooking(bookingId: $bookingId) {
    __typename
    id
    accounts {
      __typename
      id
      email
    }
    activityStartTime
    activityName
    activityBookingLink
    activitySource
    activitySourceId
    restaurantArrivalTime
    restaurantName
    restaurantBookingLink
    restaurantSource
    restaurantSourceId
    state
    reserverDetails {
      __typename
      id
      firstName
      lastName
      phoneNumber
    }
    stripePaymentId
    survey {
      __typename
      id
      headcount
      budget
      startTime
      searchRegions {
        __typename
        id
        name
      }
    }
  }
  adminBookingActivityDetail(bookingId: $bookingId) {
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
    isBookable
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
  adminBookingRestaurantDetail(bookingId: $bookingId) {
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
}`) as unknown as TypedDocumentString<AdminBookingInfoQuery, AdminBookingInfoQueryVariables>;
export const ListBookedOutingsDocument = new TypedDocumentString(`
    query ListBookedOutings($accountId: UUID!) {
  __typename
  adminBookings(accountId: $accountId) {
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
    `) as unknown as TypedDocumentString<ListBookedOutingsQuery, ListBookedOutingsQueryVariables>;
export const ReserverDetailsDocument = new TypedDocumentString(`
    query ReserverDetails($reserverDetailsId: UUID!) {
  __typename
  adminReserverDetails(reserverDetailsId: $reserverDetailsId) {
    __typename
    id
    firstName
    lastName
    phoneNumber
  }
}
    `) as unknown as TypedDocumentString<ReserverDetailsQuery, ReserverDetailsQueryVariables>;