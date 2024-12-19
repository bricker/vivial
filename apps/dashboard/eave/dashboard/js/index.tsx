import { datadogRum } from "@datadog/browser-rum";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { myWindow } from "./types/window";

if (myWindow.app.monitoringEnabled && myWindow.app.datadogApplicationId && myWindow.app.datadogClientToken) {
  datadogRum.init({
    applicationId: myWindow.app.datadogApplicationId,
    clientToken: myWindow.app.datadogClientToken,
    site: "us5.datadoghq.com",
    service: "vivial-web",
    env: myWindow.app.appEnv,
    version: myWindow.app.version,
    sessionSampleRate: 100,
    sessionReplaySampleRate: 20,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: "mask-user-input",
  });
}

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(<App />);
