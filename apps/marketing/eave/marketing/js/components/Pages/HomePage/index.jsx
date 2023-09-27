import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import useUser from "../../../hooks/useUser.js";
import DocumentationBanner from "../../Banners/DocumentationBanner/index.jsx";
import IntegrationsBanner from "../../Banners/IntegrationsBanner/index.jsx";
import PrivacyBanner from "../../Banners/PrivacyBanner/index.jsx";
import SlackBanner from "../../Banners/SlackBanner/index.jsx";
import Hero from "../../Hero/index.jsx";
import Page from "../Page/index.jsx";

const copy = {
  hero: {
    title: "The Smartest Tool for your Engineering Documentation",
    subtitle:
      "Eave uses artificial intelligence to instantly create, maintain and locate documentation for your team's product development workflows. Instantly create documentation in Confluence based on information from your team's GitHub, Slack and Jira instances.",
    cta: "Start for Free",
  },
  integrations: {
    title: "Connect Data Sources",
    subtitle:
      "Seamlessly integrate Eave with your existing business tools such as messenger apps, email clients, or existing documentation platforms.",
  },
  slack: {
    titles: ["Treat Eave like a Team Member", "Sit back, and Let Eave Write"],
    subtitles: [
      "Once Eave is integrated with your tools, call on Eave as you would with any team member. Eave uses natural language processing to respond to requests and questions.",
      "Eave uses AI to intelligently parse important information from text and code in order to write cohesive documentation - whether creating new documents or updating existing ones.",
    ],
  },
  documentation: {
    title: "Confluence Documentation",
    subtitle:
      "Eave utilizes information from your integrated apps to create and maintain documentation in Confluence. Eave will also update these pages based on evolving conversations and code - so you can rest easy knowing that your documentation is up to date.",
  },
  privacy: {
    title: "Your information is protected.",
    subtitle:
      "We care about your privacy and uphold the highest level of data integrity. All information collected is solely for the purpose of streamlining documentation processes for your business (and only yours). Your data will never be shared or sold. That’s a promise.",
  },
};

const HomePage = () => {
  const { user } = useUser();
  const navigate = useNavigate();

  const { isAuthenticated } = user;
  const { hero, integrations, slack, documentation, privacy } = copy;

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated]);

  return (
    <Page>
      <main>
        <Hero title={hero.title} subtitle={hero.subtitle} cta={hero.cta} />
        <IntegrationsBanner
          title={integrations.title}
          subtitle={integrations.subtitle}
        />
        <SlackBanner titles={slack.titles} subtitles={slack.subtitles} />
        <DocumentationBanner
          title={documentation.title}
          subtitle={documentation.subtitle}
        />
        <PrivacyBanner title={privacy.title} subtitle={privacy.subtitle} />
      </main>
    </Page>
  );
};

export default HomePage;
