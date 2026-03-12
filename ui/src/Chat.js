
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './Message';
import './Chat.css';

const Chat = () => {
  const API_URL = window.ENV?.API_URL;

  const [messages, setMessages] = useState([
    { text: 'Welcome to useyourai! Ask for some exercises to get started.', sender: 'system' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (!API_URL) {
    return (
      <div className="chat-container config-error">
        <h2>Configuration Error</h2>
        <p>API_URL is not configured. Please ensure config.js is loaded correctly.</p>
      </div>
    );
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/test`, { prompt: input });
      setMessages(prev => [...prev, { text: response.data.reply, sender: 'system' }]);
    } catch (error) {
      console.error('Error fetching response:', error);
      setMessages(prev => [...prev, { text: 'Sorry, something went wrong. Please try again.', sender: 'system' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        {isLoading && (
          <div className="message system">
            <div className="typing-bubble">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask for exercises, e.g. 'Give me 5 German adjective exercises'"
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()} aria-label="Send">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default Chat;
