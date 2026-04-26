import React, { useState } from 'react';
import { signUp, confirmRegistration, signIn, resendConfirmationCode, forgotPassword, confirmForgotPassword } from './cognito';
import './Auth.css';

const Auth = ({ onAuthenticated }) => {
  const [view, setView] = useState('signin'); // 'signin' | 'signup' | 'confirm' | 'forgot' | 'reset'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const clearError = () => setError('');

  const handleSignUp = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    clearError();
    try {
      await signUp(email, password);
      setView('confirm');
    } catch (err) {
      setError(err.message || 'Sign-up failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    clearError();
    try {
      await confirmRegistration(email, code);
      setView('signin');
    } catch (err) {
      setError(err.message || 'Confirmation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    clearError();
    try {
      await signIn(email, password);
      onAuthenticated();
    } catch (err) {
      setError(err.message || 'Sign-in failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setIsLoading(true);
    clearError();
    try {
      await resendConfirmationCode(email);
    } catch (err) {
      setError(err.message || 'Failed to resend code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    clearError();
    try {
      await forgotPassword(email);
      setView('reset');
    } catch (err) {
      setError(err.message || 'Failed to send reset code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    clearError();
    try {
      await confirmForgotPassword(email, code, password);
      setCode('');
      setPassword('');
      setView('signin');
    } catch (err) {
      setError(err.message || 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  if (view === 'signup') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Create account</h2>
          <p className="auth-subtitle">Start practising in seconds</p>
          {error && <p className="auth-error">{error}</p>}
          <form onSubmit={handleSignUp}>
            <div className="auth-field">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
            <div className="auth-field">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>
            <button className="auth-btn" type="submit" disabled={isLoading}>
              {isLoading ? 'Creating account…' : 'Create account'}
            </button>
          </form>
          <div className="auth-switch">
            Already have an account?{' '}
            <button onClick={() => { clearError(); setView('signin'); }}>Sign in</button>
          </div>
          <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.78rem', color: '#9ca3af' }}>
            By creating an account you agree to our{' '}
            <a href="/privacy" style={{ color: '#61DAFB', textDecoration: 'none' }}>Privacy Policy</a>
          </p>
        </div>
      </div>
    );
  }

  if (view === 'confirm') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Check your email</h2>
          <p className="auth-subtitle">Enter the code we sent to {email}</p>
          {error && <p className="auth-error">{error}</p>}
          <form onSubmit={handleConfirm}>
            <div className="auth-field">
              <label>Confirmation code</label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                autoComplete="one-time-code"
                inputMode="numeric"
              />
            </div>
            <button className="auth-btn" type="submit" disabled={isLoading}>
              {isLoading ? 'Confirming…' : 'Confirm'}
            </button>
          </form>
          <div className="auth-switch">
            Didn't receive a code?{' '}
            <button onClick={handleResendCode} disabled={isLoading}>Resend</button>
          </div>
        </div>
      </div>
    );
  }

  if (view === 'forgot') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Reset password</h2>
          <p className="auth-subtitle">Enter your email and we'll send a reset code</p>
          {error && <p className="auth-error">{error}</p>}
          <form onSubmit={handleForgotPassword}>
            <div className="auth-field">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
            <button className="auth-btn" type="submit" disabled={isLoading}>
              {isLoading ? 'Sending…' : 'Send reset code'}
            </button>
          </form>
          <div className="auth-switch">
            <button onClick={() => { clearError(); setView('signin'); }}>Back to sign in</button>
          </div>
        </div>
      </div>
    );
  }

  if (view === 'reset') {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Set new password</h2>
          <p className="auth-subtitle">Enter the code we sent to {email}</p>
          {error && <p className="auth-error">{error}</p>}
          <form onSubmit={handleResetPassword}>
            <div className="auth-field">
              <label>Reset code</label>
              <input
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                autoComplete="one-time-code"
                inputMode="numeric"
              />
            </div>
            <div className="auth-field">
              <label>New password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>
            <button className="auth-btn" type="submit" disabled={isLoading}>
              {isLoading ? 'Resetting…' : 'Set new password'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // default: signin
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Welcome back</h2>
        <p className="auth-subtitle">Sign in to continue practising</p>
        {error && <p className="auth-error">{error}</p>}
        <form onSubmit={handleSignIn}>
          <div className="auth-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="auth-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          <button className="auth-btn" type="submit" disabled={isLoading}>
            {isLoading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <div className="auth-switch">
          No account yet?{' '}
          <button onClick={() => { clearError(); setView('signup'); }}>Create one</button>
        </div>
        <div className="auth-switch">
          <button onClick={() => { clearError(); setView('forgot'); }}>Forgot password?</button>
        </div>
      </div>
    </div>
  );
};

export default Auth;
