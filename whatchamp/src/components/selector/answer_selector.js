import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { active_color, inactive_color } from '../../const/color';
import { questionList } from '../../const/question_list';

const AnswerSelector = ({
  idx,
  handleButtonClick
}) => {
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
        {questionList[idx].title}
      </Typography>
      <Box mb={4} mt={4}>
        {questionList[idx].option.map((option, index) => (
          <Button
            key={index}
            variant="contained"
            onClick={() => handleButtonClick(option)}
            sx={{
              m: 1,
              width: '200px',
              height: '100px',
              backgroundColor: inactive_color,
              '&:hover': {
                backgroundColor: active_color,
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
        {questionList[idx].idx}/8
      </Typography>
    </Box>
  );
};

export default AnswerSelector;