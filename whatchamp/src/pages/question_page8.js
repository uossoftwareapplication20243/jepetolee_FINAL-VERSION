import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import MultiOptionsSelector from '../components/selector/multi_options_selector';

const QuestionPage8 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap, username, tag } = useQuestionContext();
  const pageIdx = 7;

  const handleButtonClick = (option) => {
    // Update questionMap with the answer for q8
    setQuestionMap({
      ...questionMap,
      q8: option,
    });
    navigate('/new_result');
  };

  return (
    <MultiOptionsSelector
      idx = {pageIdx}
      handleButtonClick={handleButtonClick}
    />
  );
};

export default QuestionPage8;
