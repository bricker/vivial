import React from "react";

export default function withTitle(WrappedComponent) {
  return function ComponentWithTitle(props = {}) {
    const { pageTitle = "Eave, for your information." } = props;
    document.title = pageTitle;

    /* eslint-disable-next-line react/jsx-props-no-spreading */
    return <WrappedComponent {...props} />;
  };
}
