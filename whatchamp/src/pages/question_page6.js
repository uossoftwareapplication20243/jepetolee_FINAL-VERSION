import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import AnswerSelector from '../components/selector/answer_selector';


const QuestionPage6 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();
  const pageIdx = 5;

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q6: option,
    });
    navigate('/question7');
  };

  return (
    <AnswerSelector
      idx={pageIdx}
      handleButtonClick={handleButtonClick}
    />
  );
};

export default QuestionPage6;