import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import AnswerSelector from '../components/selector/answer_selector';

const QuestionPage5 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();
  const pageIdx = 4;

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q5: option,
    });
    navigate('/question6');
  };

  return (
    <AnswerSelector
      idx={pageIdx}
      handleButtonClick={handleButtonClick}
    />
  );
};

export default QuestionPage5;