import React from 'react';
import { makeStyles } from '@material-ui/styles';
import { Typography } from '@material-ui/core';
import useTeam from '../../hooks/useTeam';
import { FEATURES, FEATURE_STATES } from '../../constants';
import FeatureCard from '../FeatureCard/index.jsx';

const makeClasses = makeStyles((theme) => ({
  container: {
    padding: '0 25px',
    marginBottom: 80,
    [theme.breakpoints.up('md')]: {
      padding: '0 128px',
    }
  },
  title: {
    color: theme.palette.secondary.main,
    fontSize: 32,
    fontWeight: 400,
    marginBottom: 32,
    [theme.breakpoints.up('md')]: {
      fontSize: 36,
    }
  },
  featureCard: {
    marginBottom: 42,
    '&:last-of-type': {
      marginBottom: 0,
    },
    [theme.breakpoints.up('md')]: {
      margin: '0 42px 0 0',
      '&:last-of-type': {
        marginRight: 0,
      },
    }
  },
}));

const ExploreFeatures = ({ onInlineDocsClick }) => {
  const classes = makeClasses();
  const { team } = useTeam();
  const showInlineDocsCard = team.featureStates[FEATURES.INLINE_CODE_DOCS] === FEATURE_STATES.DISABLED;

  return (
    <section className={classes.container}>
      <Typography className={classes.title} variant="h2">
        Explore Features
      </Typography>
      <div className={classes.featureCards}>
        {showInlineDocsCard && (
          <FeatureCard
            className={classes.featureCard}
            onClick={onInlineDocsClick}
            title="Inline Code Documentation"
            description="Enable Eave to automatically summarize files and add inline documentation that updates with each code change."
          />
        )}
        <FeatureCard
          className={classes.featureCard}
          title="Architecture Diagrams"
          description="Ensure your system documentation is always accurate. Automatically create and maintain your architecture diagrams."
          comingSoon
        />
      </div>
    </section>
  );
}

export default ExploreFeatures;
