import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import AnswerSelector from '../components/selector/answer_selector';


const QuestionPage7 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();
  const pageIdx = 6;

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q7: option,
    });
    navigate('/question8');
  };

  return (
    <AnswerSelector
      idx={pageIdx}
      handleButtonClick={handleButtonClick}
    />
  );
};

export default QuestionPage7;