import React from 'react';
import withTitle from '../../hoc/withTitle';
import Hero from '../../Hero';
import DocumentationBanner from '../../Banners/DocumentationBanner';
import IntegrationsBanner from '../../Banners/IntegrationsBanner';
import SlackBanner from '../../Banners/SlackBanner';
import PrivacyBanner from '../../Banners/PrivacyBanner';
import Page from '../Page';

const copy = {
  hero: {
    title: 'The Smartest Tool for all of your Documentation Needs',
    subtitle: 'Eave uses state of the art AI technology to instantly create, update and organize your business’s documentation. Save time, reduce overhead, and preserve the integrity of your documentation. Eave, for your information.',
    cta: 'Start for Free',
  },
  integrations: {
    title: 'Connect Data Sources',
    subtitle: 'Seamlessly integrate Eave with your existing business tools such as messenger apps, email clients, or existing documentation platforms.',
  },
  slack: {
    titles: [
      'Treat Eave like a Team Member',
      'Sit back, and Let Eave Write',
    ],
    subtitles: [
      'Once Eave is integrated with your tools, call on Eave as you would with any coworker. Eave uses natural language processing to respond to requests and questions.',
      'Eave uses AI to intelligently parse important information from text and images in order to write cohesive documentation - whether creating new documents or updating existing ones.',
    ],
  },
  documentation: {
    title: 'Documentation Organization',
    subtitle: 'Eave will output and organize your documentation in the service of your choice (such as Google Drive or Sharepoint). Or try Eave’s custom state-of-the-art document management cloud based service.',
  },
  privacy: {
    title: 'Your information is protected. Period.',
    subtitle: 'We care about your privacy and uphold the highest level of data integrity. All information collected is solely for the purpose of streamlining documentation processes for your business (and only yours). Your data will never be shared or sold. That’s a promise.',
  },
};

class HomePage extends React.Component {
  render() {
    const { hero, integrations, slack, documentation, privacy } = copy;
    return (
      <Page>
        <main>
          <Hero
            title={hero.title}
            subtitle={hero.subtitle}
            cta={hero.cta}
          />
          <IntegrationsBanner
            title={integrations.title}
            subtitle={integrations.subtitle}
          />
          <SlackBanner
            titles={slack.titles}
            subtitles={slack.subtitles}
          />
          <DocumentationBanner
            title={documentation.title}
            subtitle={documentation.subtitle}
          />
          <PrivacyBanner
            title={privacy.title}
            subtitle={privacy.subtitle}
          />
        </main>
      </Page>
    );
  }
}

export default withTitle(HomePage);
