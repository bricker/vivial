import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";

import useTeam from "../../hooks/useTeam";
import FeatureSettingCard from "../FeatureSettingCard/index.jsx";

const makeClasses = makeStyles((theme) => ({
  container: {
    padding: "0 25px",
    marginBottom: 80,
    [theme.breakpoints.up("md")]: {
      padding: "0 128px",
    },
  },
  title: {
    color: theme.palette.primary.main,
    fontSize: 32,
    fontWeight: 400,
    marginBottom: 22,
    [theme.breakpoints.up("md")]: {
      fontSize: 36,
      marginBottom: 28,
    },
  },
  settingCard: {
    marginBottom: 20,
    "&:last-of-type": {
      marginBottom: 0,
    },
    [theme.breakpoints.up("md")]: {
      margin: "0 40px 0 0",
      "&:last-of-type": {
        marginRight: 0,
      },
    },
  },
}));

const FeatureSettings = ({ onAPIDocsClick, onInlineDocsClick }) => {
  const classes = makeClasses();
  const { team } = useTeam();
  return (
    <section className={classes.container}>
      <Typography className={classes.title} variant="h2">
        Feature Settings
      </Typography>
      <div className={classes.settingBtns}>
        {team.apiDocsEnabled && (
          <FeatureSettingCard
            className={classes.settingCard}
            onClick={onAPIDocsClick}
          >
            API Documentation
          </FeatureSettingCard>
        )}
        {team.inlineCodeDocsEnabled && (
          <FeatureSettingCard
            className={classes.settingCard}
            onClick={onInlineDocsClick}
          >
            Inline Code Documentation
          </FeatureSettingCard>
        )}
      </div>
    </section>
  );
};

export default FeatureSettings;
