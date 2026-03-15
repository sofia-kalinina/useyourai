
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './Message';
import './Chat.css';

const Chat = () => {
  const API_URL = window.ENV?.API_URL;

  const [messages, setMessages] = useState([
    { text: 'Welcome to useyourai! Ask for a set of exercises on any language topic — for example, "Give me 10 German accusative case exercises".', sender: 'system' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentExerciseId, setCurrentExerciseId] = useState(null);
  const [level, setLevel] = useState('A2');
  const [feedbackMode, setFeedbackMode] = useState('at_end');
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

  const addMessage = (text, sender) =>
    setMessages((prev) => [...prev, { text, sender }]);

  const handleNewSession = async (prompt) => {
    try {
      const response = await axios.post(`${API_URL}/session`, {
        prompt,
        level,
        feedback_mode: feedbackMode,
      });
      const { session_id, exercise } = response.data;
      setSessionId(session_id);
      setCurrentExerciseId(exercise.id);
      addMessage(exercise.question, 'system');
    } catch (error) {
      console.error('Error creating session:', error);
      addMessage('Sorry, something went wrong. Please try again.', 'system');
    }
  };

  const handleSubmitAnswer = async (answer) => {
    try {
      const response = await axios.post(`${API_URL}/session/${sessionId}/answer`, {
        exercise_id: currentExerciseId,
        answer,
      });
      const { is_correct, feedback, next_exercise, mistakes } = response.data;

      addMessage(is_correct ? 'Correct!' : 'Incorrect.', 'system');

      if (feedback) {
        addMessage(feedback, 'system');
      }

      if (next_exercise) {
        setCurrentExerciseId(next_exercise.id);
        addMessage(next_exercise.question, 'system');
      } else {
        const mistakeCount = mistakes ? mistakes.length : 0;
        addMessage(
          mistakeCount > 0
            ? `Session complete! You had ${mistakeCount} mistake(s). Start a new session to continue practising.`
            : 'Session complete! Great job — no mistakes!',
          'system'
        );
        setSessionId(null);
        setCurrentExerciseId(null);
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
      addMessage('Sorry, something went wrong. Please try again.', 'system');
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    addMessage(userText, 'user');
    setInput('');
    setIsLoading(true);

    try {
      if (sessionId) {
        await handleSubmitAnswer(userText);
      } else {
        await handleNewSession(userText);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.map((message, index) => {
          const isWelcome = index === 0 && !sessionId;
          if (isWelcome) {
            return (
              <div key={index} className="welcome-row">
                <Message message={message} />
                <div className="session-config">
                  <div className="pill-group">
                    {['A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map((l) => (
                      <button
                        key={l}
                        className={`pill${level === l ? ' pill--active' : ''}`}
                        onClick={() => setLevel(l)}
                        disabled={isLoading}
                      >
                        {l}
                      </button>
                    ))}
                  </div>
                  <div className="pill-group">
                    <button
                      className={`pill${feedbackMode === 'after_each' ? ' pill--active' : ''}`}
                      onClick={() => setFeedbackMode('after_each')}
                      disabled={isLoading}
                    >
                      After each
                    </button>
                    <button
                      className={`pill${feedbackMode === 'at_end' ? ' pill--active' : ''}`}
                      onClick={() => setFeedbackMode('at_end')}
                      disabled={isLoading}
                    >
                      At the end
                    </button>
                  </div>
                </div>
              </div>
            );
          }
          return <Message key={index} message={message} />;
        })}
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
          placeholder={sessionId ? 'Type your answer...' : "Ask for exercises, e.g. 'Give me 5 German adjective exercises'"}
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
