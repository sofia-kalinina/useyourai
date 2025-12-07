
import React, { useState } from 'react';
import axios from 'axios';
import Message from './Message';
import './Chat.css';

const Chat = () => {
  // Declare API_URL first
  const API_URL = window.ENV?.API_URL;

  const [messages, setMessages] = useState([
    { text: 'Welcome to useyourai! Ask for some exercises to get started.', sender: 'system' },
  ]);
  const [input, setInput] = useState('');

  // Then check if it exists
  if (!API_URL) {
    return (
      <div className="chat-container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'red',
        padding: '20px',
        textAlign: 'center'
      }}>
        <div>
          <h2>Configuration Error</h2>
          <p>API_URL is not configured. Please ensure config.js is loaded correctly.</p>
        </div>
      </div>
    );
  }

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { text: input, sender: 'user' };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput('');

      try {
        const response = await axios.post(`${API_URL}/test`, {
          prompt: input,
        });

        const systemMessage = { text: response.data.reply, sender: 'system' };
        setMessages((prevMessages) => [...prevMessages, systemMessage]);
      } catch (error) {
        console.error('Error fetching response:', error);
        const errorMessage = { text: 'Sorry, something went wrong. Please try again.', sender: 'system' };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      }
    }
  };

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your request..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Chat;
