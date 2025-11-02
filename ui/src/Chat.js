
import React, { useState } from 'react';
import axios from 'axios';
import Message from './Message';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([
    { text: 'Welcome to useyourai! Ask for some exercises to get started.', sender: 'system' },
  ]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { text: input, sender: 'user' };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput('');

      try {
        const response = await axios.post('https://k70r21jrb5.execute-api.eu-central-1.amazonaws.com/dev/test', {
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
