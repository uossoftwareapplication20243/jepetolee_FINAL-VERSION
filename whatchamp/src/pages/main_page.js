import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, TextField, Button, Grid } from '@mui/material';
import QuestionProvider from '../context/questionContext';
import { useQuestionContext } from '../context/questionContext.js';
import { server_url } from '../const/url.js';
import { active_color, inactive_color } from '../const/color.js';

function MainPage() {
  const [showLineSelection, setShowLineSelection] = useState(false);
  const navigate = useNavigate();
  const { setQuestionMap, questionMap, setLine, username, tag, setUsername, setTag } = useQuestionContext();

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowLineSelection(true);
  };


  const lines = [
    "탑", "정글", "미드", "원딜", "서폿", "상관없음"
  ];
  const handleLineSelection = async (line_index) => {
    setLine(line_index);
    setQuestionMap({
      ...questionMap,
      line: lines[line_index]
    });
  
    try {
      console.log("서버로 통신");
      const response = await fetch(
        server_url + "/api/starter",
        {
          method: "POST",
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username, tag: tag })
        }
      );
  
      if (response.ok) {
        const data = await response.json();
        console.log("서버 통신 성공");
  
        if (data["record-based"]) {
          console.log("CF 결과페이지로 이동");
          navigate('/result');
        } else {
          console.log("Content Based 질문 페이지로 이동");
          navigate('/question1');
        }
      } else {
        console.error("Request failed with status:", response.status);
      }
    } catch (error) {
      console.error("Error during fetch:", error);
    }
  };

  return (
    <QuestionProvider>
      <Box sx={{ maxWidth: 600, margin: 'auto', textAlign: 'center', mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          왓챔?
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          플레이어에 맞는 리그오브레전드 챔피언 추천
        </Typography>
        {!showLineSelection ? (
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, my: 4 }}>
              <TextField
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                variant="outlined"
                size="small"
                placeholder="사용자명"
                sx={{ flexGrow: 1 }}
              />
              <TextField
                value={tag}
                onChange={(e) => setTag(e.target.value)}
                variant="outlined"
                size="small"
                sx={{ width: '160px' }}
              />
              <Button type="submit" variant="contained" color="primary">
                조회
              </Button>
            </Box>
          </form>
        ) : (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            minHeight="60vh"
            sx={{ backgroundColor: '#f5f5f5', p: 3, mt: 4 }}
          >
            <Typography variant="h4" mb={4} gutterBottom sx={{ fontWeight: 'bold' }}> 
              라인을 선택하세요
            </Typography>
            <Grid container spacing={2} sx={{ maxWidth: 600, mb: 4 }}>
              {lines.map((line, index) => (
                <Grid item xs={4} key={index}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => handleLineSelection(index)}
                    sx={{
                      height: 100,
                      backgroundColor: inactive_color,
                      '&:hover': {
                        backgroundColor: active_color,
                      }
                    }}
                  >
                    <Typography
                      align="center"
                      sx={{ fontSize: '18px', fontWeight: 'bold' }}
                    >
                      {line}
                    </Typography>
                  </Button>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Box>
    </QuestionProvider>
  );
}

export default MainPage;
