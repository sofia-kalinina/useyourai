
import React from 'react';
import Chat from './Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1 className="App-brand">
          useyour
          <svg className="brand-bubble" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15,0 H85 C93,0 100,7 100,15 V60 C100,68 93,75 85,75 H30 L10,98 L22,75 H15 C7,75 0,68 0,60 V15 C0,7 7,0 15,0 Z" fill="#61DAFB"/>
            <text x="50%" y="38%" dominantBaseline="middle" textAnchor="middle" fontFamily="Arial, sans-serif" fontSize="36" fill="#282c34" fontWeight="bold">ai</text>
          </svg>
        </h1>
        <p className="App-tagline">AI-powered language practice</p>
      </header>
      <Chat />
    </div>
  );
}

export default App;
