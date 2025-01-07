import {
  ActivitySource,
  type ActivityFieldsFragment,
  type ItineraryFieldsFragment,
  type PhotosFieldsFragment,
} from "$eave-dashboard/js/graphql/generated/graphql";

export function getImgUrls(photos: PhotosFieldsFragment): string[] {
  let imgUrls: string[] = [];
  if (!photos) {
    return imgUrls;
  }
  if (photos.coverPhoto) {
    imgUrls.push(photos.coverPhoto.src);
  }
  imgUrls = imgUrls.concat(photos.supplementalPhotos.map((p) => p.src));
  return imgUrls;
}

export function getTicketInfo(itinerary: ItineraryFieldsFragment): string {
  const activity = itinerary.activityPlan?.activity;
  if (activity) {
    if (activity.source === ActivitySource.Eventbrite) {
      if (itinerary.headcount === 1) {
        return `${itinerary.headcount} Ticket`;
      }
      return `${itinerary.headcount} Tickets`;
    }
    if (activity.source === ActivitySource.GooglePlaces) {
      const primaryTypeName = activity.primaryTypeName?.toLocaleLowerCase();
      if (primaryTypeName?.includes("bar")) {
        return "Drinks";
      }
      if (primaryTypeName?.includes("ice cream")) {
        return "Dessert";
      }
    }
  }
  return "Activity";
}

export function getActivityCategoryInfo(activity: ActivityFieldsFragment): string {
  if (activity.primaryTypeName) {
    return activity.primaryTypeName;
  }
  if (activity.categoryGroup?.name) {
    return activity.categoryGroup.name;
  }
  return "";
}

export function getActivityVenueName(activity: ActivityFieldsFragment): string {
  if (activity.source !== ActivitySource.GooglePlaces) {
    return activity.venue.name;
  }
  return "";
}
