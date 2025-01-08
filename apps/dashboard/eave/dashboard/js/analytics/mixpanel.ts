import mixpanel from "mixpanel-browser";
import { myWindow } from "../types/window";
import { analytics } from "./segment";

export function initMixpanelSessionRecording() {
  if (!myWindow.app.analyticsEnabled) {
    return;
  }

  if (!myWindow.app.mixpanelToken) {
    console.warn("Mixpanel token missing");
    return;
  }

  mixpanel.init(myWindow.app.mixpanelToken, {
    debug: myWindow.app.appEnv === "development",
    record_sessions_percent: 100,
  });

  // Middleware to add Mixpanel's session recording properties to Segment events
  analytics
    .addSourceMiddleware(({ payload, next, integrations }) => {
      switch (payload.obj.type) {
        case "track":
        case "page": {
          const segmentDeviceId = payload.obj.anonymousId;
          // -------------------------------------------
          // Comment out one of the below mixpanel.register methods depending on your ID Management Version
          // Original ID Merge
          // mixpanel.register({ $device_id: segmentDeviceId, distinct_id : segmentDeviceId });
          // Simplified ID Merge
          mixpanel.register({ $device_id: segmentDeviceId, distinct_id: "$device:" + segmentDeviceId });
          // -------------------------------------------
          const sessionReplayProperties = mixpanel.get_session_recording_properties();
          payload.obj.properties = {
            ...payload.obj.properties,
            ...sessionReplayProperties,
          };
          break;
        }
        case "identify": {
          const userId = payload.obj.userId ? payload.obj.userId.toString() : undefined;
          mixpanel.identify(userId);
          break;
        }
        default: {
          break;
        }
      }

      next(payload);
    })
    // .then(() => {
    //   mixpanel.start_session_recording();
    // })
    .catch((e) => console.error(e));
}
