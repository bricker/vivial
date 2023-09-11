import React from 'react';
import { Link } from 'react-router-dom';
import classNames from 'classnames';
import { makeStyles } from '@material-ui/styles';
import { imageUrl } from '../../util/asset-helpers';

const makeClasses = makeStyles((theme) => ({
  logoContainer: {
    display: 'inline-block',
    width: 88,
    height: 47,
  },
  logo: {
    width: '100%',
  }
}));

const EaveLogo = ({ className }) => {
  const classes = makeClasses();
  return (
    <Link className={classes.logoContainer} to="/">
      <img className={classes.logo} src={imageUrl('eave-logo-beta.png')} />
    </Link>
  );
};

export default EaveLogo;
