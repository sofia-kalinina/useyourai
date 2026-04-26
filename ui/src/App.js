import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Chat from './Chat';
import Auth from './Auth';
import Header from './Header';
import Privacy from './Privacy';
import { refreshSession, signOut } from './cognito';
import './App.css';

function MainApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    refreshSession()
      .then(() => setIsAuthenticated(true))
      .catch(() => setIsAuthenticated(false))
      .finally(() => setAuthChecked(true));
  }, []);

  const handleAuthenticated = () => setIsAuthenticated(true);

  const handleSignOut = () => {
    signOut();
    setIsAuthenticated(false);
  };

  if (!authChecked) return null;

  return (
    <div className="App">
      <Header onSignOut={isAuthenticated ? handleSignOut : undefined} />
      {isAuthenticated
        ? <Chat onAuthError={handleSignOut} />
        : <Auth onAuthenticated={handleAuthenticated} />
      }
      <footer className="App-footer">
        <a href="/privacy">Privacy Policy</a>
      </footer>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/*" element={<MainApp />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
