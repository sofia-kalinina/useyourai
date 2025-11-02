
import React from 'react';
import './Message.css';

const Message = ({ message }) => {
  return (
    <div className={`message ${message.sender}`}>
      <p>{message.text}</p>
    </div>
  );
};

export default Message;
