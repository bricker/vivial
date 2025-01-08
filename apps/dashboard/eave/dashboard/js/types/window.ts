export type GlobalWindow = Window &
  typeof globalThis & {
    app: {
      apiBase?: string;
      appEnv?: "test" | "development" | "staging" | "production";
      version?: string;
      assetBase?: string;
      segmentWriteKey?: string;
      mixpanelToken?: string;
      analyticsEnabled?: boolean;
      monitoringEnabled?: boolean;
      stripePublishableKey?: string;
      stripeCustomerPortalUrl: string;
      datadogApplicationId?: string;
      datadogClientToken?: string;
    };
  };

// The additional properties are set in the template header, so we know they exist.
export const myWindow: GlobalWindow = window as GlobalWindow;
