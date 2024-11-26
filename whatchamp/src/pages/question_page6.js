import React from 'react';
import { Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';

const QuestionPage6 = () => {
  const navigate = useNavigate();
  const { questionMap, setQuestionMap } = useQuestionContext();

  const intro = "심리싸움 좋아하십니까"
  const options = [
    "네! 심리싸움 이기면\n너무 재밌죠",
    "아뇨. 저한테만\n집중하고 싶어요"
  ];

  const handleButtonClick = (option) => {
    setQuestionMap({
      ...questionMap,
      q6: option,
    });
    navigate('/question7');
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
      sx={{ backgroundColor: '#f5f5f5' }}
    >
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
        {intro}
      </Typography>
      <Box mb={4} mt={4}>
        {options.map((option, index) => (
          <Button
            key={index}
            variant="contained"
            onClick={() => handleButtonClick(option)}
            sx={{
              m: 1,
              width: '200px',
              height: '100px',
              backgroundColor: 'rgba(68, 77, 242, 0.5)', // 60% opacity
              '&:hover': {
                backgroundColor: 'rgba(68, 77, 242, 1)', // 100% opacity
              },
            }}
          >
            <Typography
              align="center"
              sx={{ fontSize: '18px', fontWeight: 'bold', whiteSpace: 'pre-line' }}
            >
              {option}
            </Typography>
          </Button>
        ))}
      </Box>
      <Typography variant="body1" sx={{ opacity: 0.7 }}>
        6/8
      </Typography>
    </Box>
  );
};

export default QuestionPage6;