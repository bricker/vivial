import React from 'react';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/styles';
import { IconButton, Drawer } from '@material-ui/core';

import { HEADER } from '../../constants.js';
import HamburgerIcon from '../Icons/HamburgerIcon.js';
import CloseIcon from '../Icons/CloseIcon.js';
import Button from '../Button/index.js';
import EaveLogo from '../EaveLogo/index.js';

class Header extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      drawerIsOpen: false,
    };
    this.handleOpenDrawer = this.handleOpenDrawer.bind(this);
    this.handleCloseDrawer = this.handleCloseDrawer.bind(this);
  }

  handleOpenDrawer() {
    this.setState({ drawerIsOpen: true });
  }

  handleCloseDrawer() {
    this.setState({ drawerIsOpen: false });
  }

  render() {
    const { classes, simpleHeader } = this.props;
    const { drawerIsOpen } = this.state;

    return (
      <header className={classes.outterContainer}>
        <div className={classes.innerContainer}>
          <div className={classes.logoContainer}>
            <EaveLogo />
          </div>
          {!simpleHeader && (
            <>
              <div className={classes.ctaContainer}>
                <button>
                  Log In
                </button>
                <Button to="/early">
                  Get Early Access
                </Button>
              </div>
              <IconButton
                classes={{ root: classes.menuIconBtn }}
                onClick={this.handleOpenDrawer}
              >
                <HamburgerIcon />
              </IconButton>
              <Drawer open={drawerIsOpen} anchor="right" transitionDuration={600}>
                <div className={classes.mobileMenu}>
                  <div className={classes.innerContainer}>
                    <div className={classes.logoContainer}>
                      <EaveLogo />
                    </div>
                    <IconButton
                      classes={{ root: classes.menuIconBtn }}
                      onClick={this.handleCloseDrawer}
                    >
                      <CloseIcon />
                    </IconButton>
                  </div>
                  <nav className={classes.mobileNav}>
                    <Link className={classes.mobileNavItem} to="/early">
                      Get Early Access
                    </Link>
                  </nav>
                </div>
              </Drawer>
            </>
          )}
        </div>
      </header>
    );
  }
}

const styles = (theme) => ({
  outterContainer: {
    position: 'absolute',
    top: '0',
    width: '100%',
    zIndex: 100,
  },
  innerContainer: {
    height: HEADER.mobile.height,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0px 16px',
    [theme.breakpoints.up('md')]: {
      height: HEADER.desktop.height,
      padding: '0px 46px',
    },
  },
  logoContainer: {
    paddingLeft: 10,
    [theme.breakpoints.up('md')]: {
      paddingLeft: 0,
    },
  },
  menuIconBtn: {
    padding: 0,
    [theme.breakpoints.up('md')]: {
      display: 'none',
    },
  },
  mobileMenu: {
    width: '100vw',
    height: '100vh',
    backgroundColor: theme.palette.background.main,
  },
  mobileNav: {
    padding: '30px 26px',
  },
  mobileNavItem: {
    color: theme.palette.primary.main,
    textDecoration: 'none',
    fontFamily: theme.typography.fontFamily.main,
    fontSize: 32,
    lineHeight: '37.5px',
    fontWeight: 400,
  },
  ctaContainer: {
    display: 'none',
    [theme.breakpoints.up('md')]: {
      display: 'block',
      fontSize: 32,
    },
  },
});

export default withStyles(styles)(Header);
