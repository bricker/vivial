import React from "react";
import ExternalLink from "../../Links/ExternalLink";
import LegalPage from "../LegalPage";

const PrivacyPage = () => {
  return (
    <LegalPage title="Privacy">
      Vivial, operated by Eave Technologies, Inc., ("we", "us", or "our") is committed to protecting the privacy of our
      customers and users of our products and services ("you" or "your"). This Privacy Policy explains how we collect,
      use, and disclose information that we obtain from you when you use our products and services.
      <br />
      <br />
      <b>Information We Collect</b>
      <br />
      We may collect information from you when you use our products and services, including your name, email address,
      phone number, and other contact information. We may also collect information about your device, such as IP
      address, operating system, and browser type.
      <br />
      <br />
      We may also collect information about your usage of our products and services, such as the pages you visit, the
      features you use, and the content you view.
      <br />
      <br />
      <b>How We Use Your Information</b>
      <br />
      We use personal information to provide and improve our product and services, communicate with our users, and
      personalize their experience. Specifically, we may use your information to:
      <br />
      <ul>
        <li>Process payments</li>
        <li>Respond to customer inquiries and support requests</li>
        <li>Analyze usage trends and improve our services</li>
        <li>Send promotional emails and other marketing communications</li>
        <li>Comply with legal obligations and protect our rights</li>
      </ul>
      <b>Information Sharing and Disclosure</b>
      <br />
      We do not sell or rent personal information to third parties. However, we may share your information with trusted
      third-party service providers who assist us in delivering our services, such as payment processors and email
      marketing platforms. We may also disclose personal information if required by law or to protect our legal rights.
      <br />
      <br />
      <b>Data Security</b>
      <br />
      We take reasonable measures to protect personal information from unauthorized access, disclosure, and misuse. This
      includes using encryption and other security technologies to protect sensitive data, as well as limiting access to
      personal information to authorized personnel only. However, no security measures are perfect or impenetrable, and
      we cannot guarantee the security of your information.
      <br />
      <br />
      <b>Your Rights and Choices</b>
      <br />
      You have the right to access, correct, or delete your personal information at any time. You may also opt-out of
      receiving marketing communications from us by following the instructions in our emails. Please note that we may
      still send you transactional or service-related messages even if you opt-out of marketing communications.
      <br />
      <br />
      <b>Changes to this Privacy Policy</b>
      <br />
      We may update this privacy policy from time to time to reflect changes in our practices or legal requirements. We
      will notify you of any changes by posting the updated Privacy Policy on our website.
      <br />
      <br />
      <b>Contact Us</b>
      <br />
      If you have any questions or concerns about this privacy policy or our data practices, please contact us at{" "}
      <ExternalLink to="mailto:info@vivialapp.com">info@vivialapp.com</ExternalLink>.
    </LegalPage>
  );
};

export default PrivacyPage;
