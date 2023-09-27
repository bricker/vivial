import { imageUrl } from "./util/asset-util.js";

export const FEATURES = {
  API_DOCS: "api_documentation_state",
  INLINE_CODE_DOCS: "inline_code_documentation_state",
  ARCHITECTURE_DOCS: "architecture_documentation_state",
};

export const FEATURE_STATES = {
  ENABLED: "enabled",
  DISABLED: "disabled",
  PAUSED: "paused",
};

export const FEATURE_MODAL = {
  ID: "feature-modal",
  TYPES: {
    API_DOCS: "api-documentation",
    INLINE_CODE_DOCS: "inline-code-documentation",
    ARCHITECTURE_DOCS: "architecture-documentation",
  }
}

export const FEEDBACK_URL = "https://forms.gle/3v5Xdz7kPya5UW9U6";

export const AFFILIATE_LOGOS = {
  amazon: {
    src: imageUrl("amazon-logo-3x.png"),
    alt: "Amazon logo",
  },
  paypal: {
    src: imageUrl("paypal-logo-3x.png"),
    alt: "PayPal logo",
  },
  disney: {
    src: imageUrl("disney-logo-3x.png"),
    alt: "Disney logo",
  },
  honey: {
    src: imageUrl("honey-logo-3x.png"),
    alt: "Honey logo",
  },
};

export const INTEGRATION_LOGOS = {
  slack: {
    src: imageUrl("slack-logo-3x.png"),
    alt: "Slack logo",
  },
  github: {
    src: imageUrl("github-logo-3x.png"),
    alt: "Github logo",
  },
  githubInline: {
    src: imageUrl("github-logo-inline.png"),
    alt: "Github logo",
  },
  gmail: {
    src: imageUrl("gmail-logo-3x.png"),
    alt: "Gmail logo",
  },
  outlook: {
    src: imageUrl("outlook-logo-3x.png"),
    alt: "Microsoft Outlook logo",
  },
  notion: {
    src: imageUrl("notion-logo-3x.png"),
    alt: "Notion logo",
  },
  figma: {
    src: imageUrl("figma-logo-3x.png"),
    alt: "Figma logo",
  },
  teams: {
    src: imageUrl("teams-logo-3x.png"),
    alt: "Microsoft Teams logo",
  },
  jira: {
    src: imageUrl("jira-logo-3x.png"),
    alt: "JIRA logo",
  },
  confluence: {
    src: imageUrl("confluence-logo-3x.png"),
    alt: "Confluence logo",
  },
  drive: {
    src: imageUrl("google-drive-logo-3x.png"),
    alt: "Google Drive logo",
  },
  sharepoint: {
    src: imageUrl("sharepoint-logo-3x.png"),
    alt: "Microsoft Sharepoint logo",
  },
};

export const AUTH_MODAL_STATE = {
  LOGIN: "login",
  SIGNUP: "signup",
};
