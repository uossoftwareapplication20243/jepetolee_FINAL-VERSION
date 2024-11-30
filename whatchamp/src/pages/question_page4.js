import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import AnswerSelector from '../components/selector/answer_selector';



const QuestionPage4 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();
  const pageIdx = 3;

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q4: option,
    });
    navigate('/question5');
  };

  return (
    <AnswerSelector
    idx={pageIdx}
    handleButtonClick={handleButtonClick}
  />
  );
};

export default QuestionPage4;