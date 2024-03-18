// @ts-check
import React from "react";

const MetabaseEmbeddedDashboard = ({
  className,
  /** @type {string} */ dashRoute = undefined,
}) => {
  // TODO: dont hardcode uri domain (will we need to add website app as middleman?)
  let srcRoute = "http://api.eave.run:8080/oauth/metabase";
  if (dashRoute) {
    srcRoute += `?return_to=${dashRoute}`;
  }
  return <iframe src={srcRoute} className={className}></iframe>;
};

export default MetabaseEmbeddedDashboard;
