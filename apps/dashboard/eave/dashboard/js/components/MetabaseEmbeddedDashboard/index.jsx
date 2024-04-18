// @ts-check
import React from "react";

const MetabaseEmbeddedDashboard = ({
  className,
  /** @type {string} */ dashRoute = undefined,
}) => {
  // route to web backend to add auth headers etc before redirecting to core api
  // https://www.metabase.com/docs/latest/embedding/interactive-embedding#showing-or-hiding-metabase-ui-components
  let srcRoute = "/embed/metabase";
  if (dashRoute) {
    srcRoute += `?return_to=${dashRoute}`;
  }
  return <iframe src={srcRoute} className={className}></iframe>;
};

export default MetabaseEmbeddedDashboard;
