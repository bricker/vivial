import mixpanel from "mixpanel-browser";
import { myWindow } from "../types/window";

export function initMixpanel() {
  mixpanel.init(myWindow.mixpanelToken, {
    debug: false,
    record_sessions_percent: 100,
  });
}

// Middleware to add Mixpanel's session recording properties to Segment events
void analytics.addSourceMiddleware(({ payload, next, integrations }) => {
  if (!window.mixpanel) {
    next(payload);
    return;
  }

  switch (payload.obj.type) {
    case "track":
    case "page": {
      const segmentDeviceId = payload.obj.anonymousId;
      // -------------------------------------------
      // Comment out one of the below mixpanel.register methods depending on your ID Management Version
      // Original ID Merge
      mixpanel.register({ $device_id: segmentDeviceId, distinct_id : segmentDeviceId });
      // Simplified ID Merge
      mixpanel.register({ $device_id: segmentDeviceId, distinct_id : "$device:"+segmentDeviceId });
      // -------------------------------------------
      const sessionReplayProperties = mixpanel.get_session_recording_properties();
      payload.obj.properties = {
        ...payload.obj.properties,
        ...sessionReplayProperties
      };
      break;
    }
    case "identify": {
			const userId = payload.obj.userId;
			mixpanel.identify(userId);
      break;
    }
    default: {
      break;
    }
  }

	next(payload);
});