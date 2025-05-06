import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Quiz.css';

function Quiz() {
  const location = useLocation();
  const navigate = useNavigate();
  const { module, submodule } = location.state || {};
  const [questions, setQuestions] = useState({});
  const [selectedOptions, setSelectedOptions] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);

  useEffect(() => {
    const fetchQuizData = async () => {
      try {
        const response = await axios.get('/quiz', {
          params: { module, submodule }
        });
        setQuestions(response.data.content);
        console.log(questions)
      } catch (error) {
        console.error('Error fetching quiz:', error);
      }
    };

    if (module && submodule) {
      fetchQuizData();
    }
  }, [module, submodule]);

  const handleOptionChange = (qKey, optionKey) => {
    setSelectedOptions(prev => ({ ...prev, [qKey]: optionKey }));
  };

  const handleShowAnswers = () => {
    const allAnswered = Object.keys(questions).length === Object.keys(selectedOptions).length;
    if (!allAnswered) {
      alert('Please answer all questions before checking answers.');
      return;
    }
    setShowAnswers(true);
  };

  const handleGoBack = () => {
    navigate('/');
  };

  return (
    <div className="modern-quiz">
      <div className="quiz-container">
        <h2 className="quiz-title">Quiz</h2>
        {Object.entries(questions).map(([qKey, qData]) => (
          <div key={qKey} className="quiz-question question-box">
            <p><strong>{qKey}. {qData.question}</strong></p>
            {Object.entries(qData.options).map(([optKey, optText]) => (
              <label key={optKey} style={{ display: 'block', marginLeft: '1em' }}>
                <input
                  type="radio"
                  name={`question-${qKey}`}
                  value={optKey}
                  checked={selectedOptions[qKey] === optKey}
                  onChange={() => handleOptionChange(qKey, optKey)}
                />
                {optText}
              </label>
            ))}
            {showAnswers && (
              <p className="answer-result" style={{ marginLeft: '1em', color: selectedOptions[qKey] === qData.answer ? 'green' : 'red' }}>
                {selectedOptions[qKey] === qData.answer ? '✅ Correct' : `❌ Correct Answer: ${qData.options[qData.answer]}`}
              </p>
            )}
          </div>
        ))}

        <button onClick={handleShowAnswers} className="quiz-button" style={{ marginTop: '1.5em', marginRight: '1em' }}>
          Show Answers
        </button>
        <button onClick={handleGoBack} className="quiz-button go-back" style={{ marginTop: '1.5em' }}>
          Go Back
        </button>
      </div>
    </div>
  );
}

export default Quiz;
