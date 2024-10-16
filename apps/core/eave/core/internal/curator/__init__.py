# IN PRROGRESS


# TODO
# Set up base "Experience Curator" class
# Set up hardcoded survey data.
# Set up hardcoded user preferences data.
# Set up hardcoded partner preferences data.
# Set up Yelp Fusion API client.
# Set up Ticketmaster Discovery API client.
# Implement experience curator algorithm.

# STEP 1: COMBINE INTERESTS
# ---------------------------
# Get the survey data.
# Get budget mappings for events.
# Get the user preferences.
# Get the partner preferences.
# Get shared preferences.
    # Preference intersection.
    # Preference union - intersection.
    # Order by intersection then the rest.
# Get consolidated date constraints (used throughout algo).


# STEP 2: GET THE THING TO DO
# ---------------------------
# segments = randomly shuffle Ticketmaster segments.
# For segment in segments:
    # genres = randomly shuffle genres

    # For genre in genres:
        # Hit /discovery/v2/events 
            # geoPoint
            # radius
            # city (if no geoPoint and radius)
            # startDateTime 
            # countryCode
            # stateCode
            # segmentId
            # genreId

        # For event in events:
            # If event is within the date constraints:
                # stop searching through segments / genres.










# Add rate limit fallbacks for Ticketmaster API
# Add rate limit fallbacks for Yelp API
# Outstanding TODOs.
# Experience Curator documentation.




from eave.stdlib.yelp_api.fusion import YelpFusionAPIClient

yelp_client = YelpFusionAPIClient(key)

# note async so need to await


# Fetch from Yelp API 

# Fetch from Ticketmaster API

