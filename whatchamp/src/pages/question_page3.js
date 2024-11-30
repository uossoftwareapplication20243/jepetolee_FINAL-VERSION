import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import AnswerSelector from '../components/selector/answer_selector';

const QuestionPage3 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();
  const pageIdx = 2;

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q3: option,
    });
    navigate('/question4');
  };

  return (
    <AnswerSelector
      idx={pageIdx}
      handleButtonClick={handleButtonClick}
    />
  );
};

export default QuestionPage3;