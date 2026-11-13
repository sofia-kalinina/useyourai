import React from 'react';
import './Message.css';

const MistakeList = ({ mistakes, tr }) => {
  return (
    <div className="message system">
      <div className="mistake-list">
        <div className="mistake-list__title">{tr.mistakesTitle}</div>
        <ol>
          {mistakes.map((mistake) => (
            <li key={mistake.exercise_id}>
              <div>{mistake.question}</div>
              <div className="mistake-list__wrong">{tr.yourAnswer}: {mistake.user_answer}</div>
              <div className="mistake-list__right">{tr.correctAnswer}: {mistake.expected_answer}</div>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
};

export default MistakeList;
