import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import useUser from "../../../hooks/useUser.js";
import ProductivityBanner from "../../Banners/ProductivityBanner/index.jsx";
import GitHubFeaturesBanner from "../../Banners/GitHubFeaturesBanner/index.jsx";
import PrivacyBanner from "../../Banners/PrivacyBanner/index.jsx";
import Hero from "../../Hero/index.jsx";
import Page from "../Page/index.jsx";

const copy = {
  hero: {
    title: "Automate your Engineering Documentation",
    subtitle: "Eave ensures your technical documentation is accurate and up to date. Stop wasting time manually maintaining your documentation and spend more time building.",
    cta: "Start for Free",
  },
  githubFeatures : {
    title: "One Integration for Automation",
  },
  productivity: {
    title: "Unlock a New Level of Productivity",
  },
  privacy: {
    title: "Your information is protected.",
    subtitle: "We care about your privacy and uphold the highest level of data integrity. All information collected is solely for the purpose of streamlining documentation processes for your business (and only yours). Your data will never be shared or sold. That’s a promise.",
  },
};

const HomePage = () => {
  const { user } = useUser();
  const navigate = useNavigate();

  const { isAuthenticated } = user;
  const { hero, githubFeatures, productivity, privacy } = copy;

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated]);

  return (
    <Page>
      <main>
        <Hero title={hero.title} subtitle={hero.subtitle} cta={hero.cta} />
        <GitHubFeaturesBanner title={githubFeatures.title} />
        <ProductivityBanner title={productivity.title} />
        <PrivacyBanner title={privacy.title} subtitle={privacy.subtitle} />
      </main>
    </Page>
  );
};

export default HomePage;
