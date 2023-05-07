import React from 'react';
import { makeStyles } from '@material-ui/styles';

import Copy from '../../Copy/index.jsx';
import { imageUrl } from '../../../asset-helpers.js';

const makeClasses = makeStyles((theme) => ({
  section: {
    backgroundColor: theme.palette.background.dark,
    padding: '54px 40px 0',
    [theme.breakpoints.up('sm')]: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    [theme.breakpoints.up('md')]: {
      padding: '82px 164px',
    },
    [theme.breakpoints.up('lg')]: {
      flexDirection: 'row',
    },
  },
  copy: {
    marginBottom: 37,
    [theme.breakpoints.up('lg')]: {
      width: 457,
      minWidth: 457,
      marginBottom: 0,
      marginRight: 68,
    },
  },
  // imgWrapper: {
  //   maxWidth: '100%',
  // },
  img: {
    maxWidth: '100%',
    marginBottom: '-5px',
    [theme.breakpoints.up('md')]: {
      // maxWidth: 633,
      marginBottom: 0,
    },
  },

}));

const DocumentationBanner = ({ title, subtitle }) => {
  const classes = makeClasses();

  return (
    <section id="eave-integrations-banner" className={classes.section}>
      <div className={classes.copy}>
        <Copy variant="h2">
          {title}
        </Copy>
        <Copy variant="pSmall">
          {subtitle}
        </Copy>
      </div>
      <picture className={classes.imgWrapper}>
        <source
          media="(min-width: 600px)"
          sizes="1266px"
          srcSet={`${imageUrl('confluence-mock.png')} 1266w`}
        />
        <source
          media="(max-width: 599px)"
          sizes="714px"
          srcSet={`${imageUrl('confluence-mock-mobile.png')} 714w`}
        />
        <img
          className={classes.img}
          src={imageUrl('confluence-mock-mobile.png')}
          alt="Confluence documentation written by Eave."
        />
      </picture>
    </section>
  );
};

export default DocumentationBanner;
