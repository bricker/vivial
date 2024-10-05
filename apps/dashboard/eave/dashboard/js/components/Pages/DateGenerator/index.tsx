import { AppContext } from "$eave-dashboard/js/context/Provider";
import { textStyles, uiStyles } from "$eave-dashboard/js/theme";
import { CircularProgress } from "@mui/material";
import classNames from "classnames";
import React, { useContext } from "react";
import Survey from "../../Survey/index.js";

const DateGenerator = () => {
  const { classes: ui } = uiStyles();
  const { classes: text } = textStyles();

  const { surveyNetworkStateCtx } = useContext(AppContext);
  const [networkState] = surveyNetworkStateCtx!;

  if (networkState.dateIsLoading) {
    // date is being planned
    return (
          <CircularProgress color="secondary" />
    );
  } else if (networkState.dateIsErroring) {
    return (
      <div className={classNames(ui.loadingContainer, text.header, text.error)}>
        ERROR while planning your date
      </div>
    );
  } else if (networkState.dateNotRequested) {
    return <Survey />
  } else {
    // show date data
    return <div>TODO: Heres your date: mcdonalds parking lot</div>
  }
};

export default DateGenerator;
