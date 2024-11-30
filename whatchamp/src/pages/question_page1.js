import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import MultiSelector from '../components/selector/multi_selector';

const QuestionPage1 = () => {
  const [selectedJobs, setSelectedJobs] = useState([]);
  const navigate = useNavigate();
  const {questionMap, setQuestionMap} = useQuestionContext()
  const pageIdx = 0;

  const handleJobToggle = (job) => {
    setSelectedJobs(prev => 
      prev.includes(job) ? prev.filter(j => j !== job) : [...prev, job]
    );
  };

  const handleNext = () => {
    setQuestionMap({
      ...questionMap,
      q1: selectedJobs,
    })
    navigate('/question2');
  };

  return (
    <MultiSelector
      idx = {pageIdx}
      handleNext={handleNext}
      handleJobToggle={handleJobToggle}
      selectedJobs = {selectedJobs}
    />
  );
};

export default QuestionPage1;