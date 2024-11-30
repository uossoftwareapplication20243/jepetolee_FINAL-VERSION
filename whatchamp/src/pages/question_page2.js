import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import AnswerSelector from '../components/selector/answer_selector';

const QuestionPage2 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();
  const pageIdx = 1;

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q2: option,
    });
    navigate('/question3');
  };

  return (
    <AnswerSelector
      idx={pageIdx}
      handleButtonClick={handleButtonClick}
    />
  );
};

export default QuestionPage2;