import React from 'react';
import Header from './Header';
import './Privacy.css';

const Privacy = () => (
  <div className="privacy-page">
    <Header />
    <main className="privacy-main">
      <h1>Privacy Policy</h1>
      <p className="privacy-meta">Effective date: 26 April 2026 &nbsp;·&nbsp; Last updated: 26 April 2026</p>

      <h2>1. Who is responsible for your data</h2>
      <p>
        useyourai ("<strong>we</strong>", "<strong>us</strong>") is the data controller for personal data collected
        through <strong>useyourai.eu</strong>. For any privacy-related questions or requests, contact us at{' '}
        <a href="mailto:privacy@useyourai.eu">privacy@useyourai.eu</a>.
      </p>

      <h2>2. What data we collect and why</h2>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Purpose</th>
            <th>Legal basis</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Email address</strong></td>
            <td>Create and identify your account; send confirmation and password-reset codes</td>
            <td>Contract</td>
          </tr>
          <tr>
            <td><strong>Exercise prompts</strong> (free text, ≤ 500 characters)</td>
            <td>Generate language exercises via AI</td>
            <td>Contract</td>
          </tr>
          <tr>
            <td><strong>Exercise answers</strong> (free text, ≤ 300 characters)</td>
            <td>Evaluate answers and generate feedback via AI</td>
            <td>Contract</td>
          </tr>
          <tr>
            <td><strong>Session metadata</strong> (topic, language, level, feedback preference)</td>
            <td>Personalise exercises to your chosen settings</td>
            <td>Contract</td>
          </tr>
          <tr>
            <td><strong>User identifier</strong> (a random UUID assigned at sign-up)</td>
            <td>Link sessions to your account; enforce access control</td>
            <td>Legitimate interest</td>
          </tr>
        </tbody>
      </table>
      <p>
        We do <strong>not</strong> collect your name, phone number, or payment details.
        We do <strong>not</strong> use tracking or advertising cookies.
        We do <strong>not</strong> embed third-party analytics scripts.
      </p>

      <h2>3. How long we keep your data</h2>
      <ul>
        <li><strong>Exercise prompts, answers, and session data</strong> — automatically deleted after <strong>24 hours</strong> via a database TTL mechanism.</li>
        <li><strong>Account data (email address)</strong> — retained until you request account deletion. Email <a href="mailto:privacy@useyourai.eu">privacy@useyourai.eu</a> to delete your account.</li>
      </ul>

      <h2>4. Who processes your data</h2>
      <p>
        We use <strong>Amazon Web Services (AWS)</strong> as our cloud infrastructure provider, covered by
        AWS's standard <a href="https://aws.amazon.com/compliance/gdpr-center/" target="_blank" rel="noopener noreferrer">Data Processing Addendum</a>.
      </p>
      <table>
        <thead>
          <tr>
            <th>Service</th>
            <th>Region</th>
            <th>What it handles</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Amazon Cognito</td>
            <td>eu-central-1 (Frankfurt)</td>
            <td>Authentication — stores your email and hashed password</td>
          </tr>
          <tr>
            <td>Amazon DynamoDB</td>
            <td>eu-central-1 (Frankfurt)</td>
            <td>Session storage — prompts, answers, metadata (deleted after 24 h)</td>
          </tr>
          <tr>
            <td>AWS Lambda &amp; API Gateway</td>
            <td>eu-central-1 (Frankfurt)</td>
            <td>Application logic — in-transit only, no persistent storage</td>
          </tr>
          <tr>
            <td>Amazon S3 &amp; CloudFront</td>
            <td>eu-central-1 / global edge</td>
            <td>Hosts the website front end (static files only; no user data)</td>
          </tr>
          <tr>
            <td>Amazon Bedrock (Claude Sonnet)</td>
            <td>eu-central-1 (Frankfurt)</td>
            <td>AI model — receives your prompts and answers to generate exercises and feedback</td>
          </tr>
        </tbody>
      </table>
      <div className="privacy-note">
        <strong>AI and your data:</strong> We use Claude via Amazon Bedrock. AWS's policy is that customer inputs
        and outputs are <strong>not used to train or improve foundation models</strong>. Your prompts and answers
        are processed transiently and not retained beyond the request.
        See the <a href="https://aws.amazon.com/bedrock/faqs/" target="_blank" rel="noopener noreferrer">AWS Bedrock FAQ</a>.
      </div>
      <p>We do not share your data with any other third parties.</p>

      <h2>5. Browser storage</h2>
      <p>
        When you sign in, your session tokens are stored in your browser's <strong>localStorage</strong>.
        The access token expires after <strong>1 hour</strong>; the refresh token after <strong>30 days</strong>.
        Clearing your browser's site data removes them immediately.
      </p>
      <p>
        No tracking or advertising cookies are used. No cookie consent banner is shown because the only
        browser storage we use is strictly necessary to provide the service you signed in to use.
      </p>

      <h2>6. Your rights</h2>
      <p>Under GDPR you have the right to:</p>
      <ul>
        <li><strong>Access</strong> — request a copy of the data we hold about you</li>
        <li><strong>Rectification</strong> — ask us to correct inaccurate data</li>
        <li><strong>Erasure</strong> — ask us to delete your account and all associated data</li>
        <li><strong>Portability</strong> — receive your data in a machine-readable format</li>
        <li><strong>Objection</strong> — object to processing based on legitimate interest</li>
        <li><strong>Restriction</strong> — ask us to limit processing while a dispute is resolved</li>
      </ul>
      <p>
        Email <a href="mailto:privacy@useyourai.eu">privacy@useyourai.eu</a> to exercise any of these rights.
        We will respond within <strong>30 days</strong>.
      </p>
      <p>
        You may also lodge a complaint with your national data protection authority. In Germany:{' '}
        <a href="https://www.bfdi.bund.de" target="_blank" rel="noopener noreferrer">Bundesbeauftragte für den Datenschutz (BfDI)</a>.
      </p>

      <h2>7. Changes to this policy</h2>
      <p>
        If we make material changes, we will update the effective date above. Continued use of the service
        after a change constitutes acceptance of the revised policy.
      </p>

      <div className="privacy-page-footer">
        useyourai &nbsp;·&nbsp; <a href="mailto:privacy@useyourai.eu">privacy@useyourai.eu</a>
      </div>
    </main>
  </div>
);

export default Privacy;
