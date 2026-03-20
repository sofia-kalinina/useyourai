
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './Message';
import translations from './translations';
import './Chat.css';

const getOrCreateUserId = () => {
  let userId = localStorage.getItem('user_id');
  if (!userId) {
    userId = crypto.randomUUID();
    localStorage.setItem('user_id', userId);
  }
  return userId;
};

const Chat = () => {
  const API_URL = window.ENV?.API_URL;
  const userId = getOrCreateUserId();

  const [lang, setLang] = useState('en');
  const tr = translations[lang];

  const [messages, setMessages] = useState([
    { text: translations.en.welcome, sender: 'system' },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentExerciseId, setCurrentExerciseId] = useState(null);
  const [answersSubmitted, setAnswersSubmitted] = useState(0);
  const [level, setLevel] = useState('A2');
  const [feedbackMode, setFeedbackMode] = useState('end');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.blur();
    }
  }, [isLoading]);

  // Update the welcome message text when language changes
  useEffect(() => {
    setMessages((prev) => [
      { text: tr.welcome, sender: 'system' },
      ...prev.slice(1),
    ]);
  }, [lang]); // eslint-disable-line react-hooks/exhaustive-deps

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
        lang,
        user_id: userId,
      });
      const { session_id, exercise } = response.data;
      setSessionId(session_id);
      setAnswersSubmitted(0);
      setCurrentExerciseId(exercise.id);
      addMessage(exercise.question, 'system');
    } catch (error) {
      console.error('Error creating session:', error);
      addMessage(tr.error, 'system');
    }
  };

  const handleSubmitAnswer = async (answer) => {
    try {
      const response = await axios.post(`${API_URL}/session/${sessionId}/answer`, {
        exercise_id: currentExerciseId,
        answer,
      });
      const { is_correct, feedback, next_exercise, mistakes } = response.data;

      if (feedbackMode === 'each') {
        addMessage(is_correct ? tr.correct : tr.incorrect, 'system');
      }

      if (next_exercise) {
        if (feedback) addMessage(feedback, 'system');
        setAnswersSubmitted(prev => prev + 1);
        setCurrentExerciseId(next_exercise.id);
        addMessage(next_exercise.question, 'system');
      } else {
        const total = answersSubmitted + 1;
        const mistakeCount = mistakes ? mistakes.length : 0;
        const correct = total - mistakeCount;
        addMessage(tr.sessionComplete(correct, total), 'system');
        if (feedback) addMessage(feedback, 'system');
        addMessage(tr.startNew, 'system');
        setSessionId(null);
        setCurrentExerciseId(null);
        setAnswersSubmitted(0);
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
      addMessage(tr.error, 'system');
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
                      className={`pill${feedbackMode === 'each' ? ' pill--active' : ''}`}
                      onClick={() => setFeedbackMode('each')}
                      disabled={isLoading}
                    >
                      {tr.afterEach}
                    </button>
                    <button
                      className={`pill${feedbackMode === 'end' ? ' pill--active' : ''}`}
                      onClick={() => setFeedbackMode('end')}
                      disabled={isLoading}
                    >
                      {tr.atTheEnd}
                    </button>
                  </div>
                  <div className="pill-group">
                    <button
                      className={`pill${lang === 'en' ? ' pill--active' : ''}`}
                      onClick={() => setLang('en')}
                    >
                      EN
                    </button>
                    <button
                      className={`pill${lang === 'uk' ? ' pill--active' : ''}`}
                      onClick={() => setLang('uk')}
                    >
                      UK
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
          placeholder={sessionId ? tr.placeholderAnswer : tr.placeholderPrompt}
          disabled={isLoading}
          ref={inputRef}
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
