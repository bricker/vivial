export type GlobalWindow = Window &
  typeof globalThis & {
    app: {
      apiBase?: string;
      appEnv?: string;
      assetBase?: string;
      segmentWriteKey?: string;
      analyticsEnabled?: boolean;
      stripePublishableKey?: string;
    };
  };

// The additional properties are set in the template header, so we know they exist.
export const myWindow: GlobalWindow = window as GlobalWindow;
