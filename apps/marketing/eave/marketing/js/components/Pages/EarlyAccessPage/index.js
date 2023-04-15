import React from 'react';
import * as EmailValidator from 'email-validator';
import { withCookies } from 'react-cookie';
import { withStyles } from '@material-ui/styles';
import { Checkbox, TextField } from '@material-ui/core';

import { HEADER, INTEGRATION_LOGOS } from '../../../constants.js';
import LockIcon from '../../Icons/LockIcon.js';
import Button from '../../Button/index.js';
import Affiliates from '../../Affiliates/index.js';
import Copy from '../../Copy/index.js';
import Page from '../Page/index.js';
import withTitle from '../../hoc/withTitle.js';
import { getTrackingInfo, saveCookie, cookiePrefix } from '../../../cookies.js';

const copy = {
  title: 'Get Free Early Access',
  subtitle: 'Eave is currently in development. Submit your email below for exclusive early access.  Note there are a limited number of seats for early access - availability granted on a first come first serve basis.',
  submittedTitle: 'Thanks!',
  submittedSubtitle: "You've been successfully added to the waitlist for early access to Eave. We'll email you with updates and instructions when ready. For inquiries, contact info@eave.fyi",
  cta: 'Submit',
  secure: 'Secure email form',
  integrationsSelectionPrompt: 'What integrations would you be interested in? Click all that apply.',
  freeFormPrompt: 'What interests you about Eave? Are there other integrations you’d like to see that aren’t mentioned above? We’d love to know to better tailor your experience.',
};

class EarlyAccessPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      emailError: false,
      emailHelperText: '',
      emailColor: 'primary',
      emailSubmitted: false,
    };
    this.handleEmailChange = this.handleEmailChange.bind(this);
    this.handleEmailSubmit = this.handleEmailSubmit.bind(this);

    this.shuffledLogos = Object.entries(INTEGRATION_LOGOS)
      .map((value) => ({ value, sort: Math.random() }))
      .sort((a, b) => a.sort - b.sort)
      .map(({ value }) => value);
  }

  handleEmailChange(e) {
    this.setState({
      email: e.target.value,
      emailError: false,
      emailHelperText: '',
      emailColor: 'primary',
    });
  }

  handleEmailSubmit(e) {
    e.preventDefault();
    const { email } = this.state;
    const emailIsValid = EmailValidator.validate(email);
    if (!emailIsValid) {
      this.setState({
        emailError: true,
        emailColor: 'primary',
        emailHelperText: 'Invalid email address.',
      });
      return;
    }
    const { cookies } = this.props;

    const selectedIntegrations = Array.from(e.target.elements.integrations)
      .filter((c) => c.checked)
      .map((c) => c.value)
      .sort(); // normalize

    const visitorId = cookies.get('visitor_id');
    const trackingInfo = getTrackingInfo();
    const variant = cookies.get('_gaexp');
    const freeFormText = e.target.elements.freeFormInput.value;
    const integrationsPresentationOrder = this.shuffledLogos.map(([name]) => name);

    fetch('/access_request', {
      body: JSON.stringify({
        email,
        visitor_id: visitorId,
        opaque_input: JSON.stringify({
          selected_integrations: selectedIntegrations,
          free_form_text: freeFormText,
          tracking_info: trackingInfo,
          experiment_variant: variant,
        }),
      }),
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(() => {
      this.setState({
        emailSubmitted: true,
      });
    }).catch(() => {
      this.setState({
        emailColor: 'primary',
        emailError: true,
        emailHelperText: 'Error: contact info@eave.fyi.',
      });
    }).finally(() => {
      const cookieName = `${cookiePrefix}ear`;
      if (cookies.get(cookieName)) return;

      window.dataLayer?.push({
        event: 'early_access_form_submission',
        email,
        integrations_presentation_order: integrationsPresentationOrder,
        selected_integrations: selectedIntegrations,
        free_form_text: freeFormText,
        transaction_id: visitorId,
      });

      saveCookie(cookieName, true);
    });
  }

  render() {
    const { classes } = this.props;
    const {
      email,
      emailColor,
      emailError,
      emailHelperText,
      emailSubmitted,
    } = this.state;
    const title = emailSubmitted ? copy.submittedTitle : copy.title;
    const subtitle = emailSubmitted ? copy.submittedSubtitle : copy.subtitle;

    return (
      <Page>
        <main className={classes.main}>
          <section className={classes.section}>
            <Copy className={classes.title} variant="h1">
              {title}
            </Copy>
            <Copy className={classes.subtitle} variant="p">
              {subtitle}
            </Copy>
            {!emailSubmitted && (
              <>
                <form onSubmit={this.handleEmailSubmit}>
                  <div className={[classes.formInputContainer, classes.formSection].join(' ')}>
                    <TextField
                      classes={{ root: classes.emailTextField }}
                      label="Email Address"
                      variant="outlined"
                      color={emailColor}
                      onChange={this.handleEmailChange}
                      value={email}
                      error={emailError}
                      helperText={emailHelperText}
                      FormHelperTextProps={{
                        classes: { root: classes.emailHelperText },
                      }}
                      InputProps={{
                        classes: { root: classes.emailInput },
                      }}
                      InputLabelProps={{
                        classes: { root: classes.emailInputLabel },
                      }}
                    />
                    <div className={classes.secureHelperText}>
                      <LockIcon className={classes.lockIcon} /> {copy.secure}
                    </div>
                  </div>

                  <div className={classes.formSection}>
                    <Copy className={classes.subtitle}>
                      {copy.integrationsSelectionPrompt}
                    </Copy>

                    <div className={[classes.formInputContainer, classes.checkboxesContainer].join(' ')}>
                      {
                        this.shuffledLogos.map(([name, { alt, src }]) => {
                          const icon = (
                            <img
                              className={classes.checkboxImg}
                              alt={alt}
                              src={src}
                            />
                          );

                          const iconChecked = (
                            <img
                              className={[classes.checkboxImg, classes.checkboxImgChecked].join(' ')}
                              alt={alt}
                              src={src}
                            />
                          );

                          return (
                            <Checkbox
                              key={name}
                              value={name}
                              name="integrations"
                              color="primary"
                              classes={{ root: classes.checkbox, checked: classes.checkboxChecked }}
                              icon={icon}
                              checkedIcon={iconChecked}
                            />
                          );
                        })
                      }
                    </div>
                  </div>

                  <div className={classes.formSection}>
                    <Copy className={classes.subtitle}>
                      {copy.freeFormPrompt}
                    </Copy>

                    <div className={classes.formInputContainer}>
                      <TextField
                        name="freeFormInput"
                        classes={{ root: classes.textareaInput }}
                        multiline
                        minRows={4}
                        placeholder="I'm interested in..."
                        variant="outlined"
                        color="primary"
                        InputProps={{
                          classes: { root: classes.emailInput },
                        }}
                      />
                    </div>
                  </div>

                  <div className={classes.cta}>
                    <Button type="submit" lg>
                      {copy.cta}
                    </Button>
                  </div>
                </form>
                <Affiliates />
              </>
            )}
          </section>
        </main>
      </Page>
    );
  }
}

const styles = (theme) => ({
  section: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: `calc(${HEADER.mobile.heightPx} + 54px) 40px 0`,
    [theme.breakpoints.up('md')]: {
      padding: '164px',
    },
  },
  title: {
    marginBottom: 26,
    [theme.breakpoints.up('sm')]: {
      maxWidth: 850,
    },
  },
  subtitle: {
    marginBottom: 32,
    [theme.breakpoints.up('sm')]: {
      maxWidth: 840,
    },
  },
  cta: {
    marginBottom: 46,
  },
  formSection: {
    marginBottom: 42,
  },
  checkboxesContainer: {
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    width: '100%',
    gap: 12,
    justifyContent: 'flex-start',
  },
  checkbox: {
    width: 102,
    height: 45,
    padding: 14,
    borderRadius: 10,
    border: `1px solid ${theme.typography.color.main}`,
  },
  checkboxChecked: {
    boxShadow: `inset 0px 0px 0 2000px ${theme.palette.background.dark}`,
  },
  checkboxImg: {
    maxWidth: '100%',
    maxHeight: 45,
  },
  checkboxImgChecked: {
    opacity: '40%',
  },
  formInputContainer: {
    [theme.breakpoints.up('sm')]: {
      maxWidth: 600,
    },
  },
  textareaInput: {
    width: '100%',
  },
  emailTextField: {
    width: '100%',
  },
  emailInput: {
    borderRadius: 5,
    color: theme.typography.color.main,
  },
  emailInputLabel: {
    color: theme.typography.color.main,
  },
  emailHelperText: {
    margin: 0,
    padding: '2px 14px',
  },
  secureHelperText: {
    marginTop: 5,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: 12,
    color: theme.typography.color.main,
    [theme.breakpoints.up('sm')]: {
      fontSize: 14,
      lineHeight: '16px',
      justifyContent: 'left',
      marginTop: 10,
    },
  },
  lockIcon: {
    marginRight: 4,
  },
});

export default withCookies(withStyles(styles)(withTitle(EarlyAccessPage)));
