// App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './pages/main_page';
import ResultPage from './pages/result_page';
import NewResultPage from './pages/new_result_page';
import QuestionPage1 from './pages/question_page1';
import QuestionPage2 from './pages/question_page2';
import QuestionPage3 from './pages/question_page3';
import QuestionPage4 from './pages/question_page4';
import QuestionPage5 from './pages/question_page5';
import QuestionPage6 from './pages/question_page6';
import QuestionPage7 from './pages/question_page7';
import QuestionPage8 from './pages/question_page8';


import { createTheme, ThemeProvider } from '@mui/material';
import QuestionProvider  from './context/questionContext';

export const theme = createTheme({
  typography: {
    fontFamily: 'Pretendard Variable',
  },
  palette: {
    primary: {
      main: '#444DF2',
    },
  },
});


function App() {
  return (
    <ThemeProvider theme={theme}>
      <QuestionProvider>
        <Router>
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/result" element={<ResultPage />} />
            <Route path="/new_result" element={<NewResultPage />} />
            <Route path="/question1" element={<QuestionPage1 />} />
            <Route path="/question2" element={<QuestionPage2 />} />
            <Route path="/question3" element={<QuestionPage3 />} />
            <Route path="/question4" element={<QuestionPage4 />} />
            <Route path="/question5" element={<QuestionPage5 />} />
            <Route path="/question6" element={<QuestionPage6 />} />
            <Route path="/question7" element={<QuestionPage7 />} />
            <Route path="/question8" element={<QuestionPage8 />} />          

          </Routes>
        </Router>
      </QuestionProvider>
    </ThemeProvider>
  );
};
export default App;