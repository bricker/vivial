export const requestOrigin = "web_app";

export type GlobalWindow = Window &
  typeof globalThis & {
    app: {
      apiBase?: string;
      appEnv?: string;
      assetBase?: string;
    };
    analytics?: any;
  };

// The additional properties are set in the template header, so we know they exist.
export const myWindow: GlobalWindow = window as GlobalWindow;
export const isProdMode = myWindow.app.appEnv === "production";

/** Helper type to union w/ response data types */
export type NetworkState = {
  loading: boolean;
  error?: Error;
};
