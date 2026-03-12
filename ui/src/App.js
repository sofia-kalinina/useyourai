
import React from 'react';
import Chat from './Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="App-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#6366f1"/>
            <text x="50%" y="55%" dominantBaseline="middle" textAnchor="middle" fontFamily="Arial, sans-serif" fontSize="14" fill="white" fontWeight="bold">AI</text>
          </svg>
        </div>
        <h1>useyour<span>ai</span></h1>
        <p className="App-tagline">AI-powered language practice</p>
      </header>
      <Chat />
    </div>
  );
}

export default App;
