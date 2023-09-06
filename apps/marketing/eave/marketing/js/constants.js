import { imageUrl } from './util/asset-helpers.js';

export const FEEDBACK_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSfkmCRGUy4IRG-jRwviYNiOk9oNIfRDBjc0CogtDpYGfsOktQ/viewform?usp=sf_link';

export const HEADER = {
  mobile: {
    height: 66,
    heightPx: '66px',
  },
  desktop: {
    height: 110,
    heightPx: '110px',
  },
};

export const FOOTER = {
  mobile: {
    height: 81,
    heightPx: '81px',
  },
  desktop: {
    height: 78,
    heightPx: '78px',
  },
};

export const AFFILIATE_LOGOS = {
  amazon: {
    src: imageUrl('amazon-logo-3x.png'),
    alt: 'Amazon logo',
  },
  paypal: {
    src: imageUrl('paypal-logo-3x.png'),
    alt: 'PayPal logo',
  },
  disney: {
    src: imageUrl('disney-logo-3x.png'),
    alt: 'Disney logo',
  },
  honey: {
    src: imageUrl('honey-logo-3x.png'),
    alt: 'Honey logo',
  },
};

export const INTEGRATION_LOGOS = {
  slack: {
    src: imageUrl('slack-logo-3x.png'),
    alt: 'Slack logo',
  },
  github: {
    src: imageUrl('github-logo-3x.png'),
    alt: 'Github logo',
  },
  githubInline: {
    src: imageUrl('github-logo-inline.png'),
    alt: 'Github logo',
  },
  gmail: {
    src: imageUrl('gmail-logo-3x.png'),
    alt: 'Gmail logo',
  },
  outlook: {
    src: imageUrl('outlook-logo-3x.png'),
    alt: 'Microsoft Outlook logo',
  },
  notion: {
    src: imageUrl('notion-logo-3x.png'),
    alt: 'Notion logo',
  },
  figma: {
    src: imageUrl('figma-logo-3x.png'),
    alt: 'Figma logo',
  },
  teams: {
    src: imageUrl('teams-logo-3x.png'),
    alt: 'Microsoft Teams logo',
  },
  jira: {
    src: imageUrl('jira-logo-3x.png'),
    alt: 'JIRA logo',
  },
  confluence: {
    src: imageUrl('confluence-logo-3x.png'),
    alt: 'Confluence logo',
  },
  drive: {
    src: imageUrl('google-drive-logo-3x.png'),
    alt: 'Google Drive logo',
  },
  sharepoint: {
    src: imageUrl('sharepoint-logo-3x.png'),
    alt: 'Microsoft Sharepoint logo',
  },
};

export const AUTH_MODAL_STATE = {
  LOGIN: 'login',
  SIGNUP: 'signup',
};
