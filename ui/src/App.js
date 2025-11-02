
import React from 'react';
import Chat from './Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>useyour</h1>
        <div className="App-logo">
          <svg width="50" height="50" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M50 0C22.3858 0 0 22.3858 0 50C0 62.5833 4.625 73.75 12.5 82.5L10 100L30 92.5C38.75 97.375 49.9167 100 62.5 100C87.6142 100 100 77.6142 100 50C100 22.3858 77.6142 0 50 0Z" fill="#61DAFB"/>
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="51" fill="#282c34" font-weight="bold">AI</text>
          </svg>
        </div>
      </header>
      <Chat />
    </div>
  );
}

export default App;
