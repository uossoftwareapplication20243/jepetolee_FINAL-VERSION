import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, CircularProgress } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { theme } from '../App';
import { cNameMap } from '../const/championsName';
import { positions } from '../const/positions';
import { Link } from 'react-router-dom';
import { useQuestionContext } from '../context/questionContext';
import { server_url } from '../const/url';

function get_images(champion_en) {
  return `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${champion_en}_0.jpg`;
}

function NewResultPage() {
  const location = useLocation();
  const { questionMap, line, username, tag } = useQuestionContext();
  const [championList, setChampionList] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state
  const idx = line;

  useEffect(() => {
    // Initial static data for demonstration
    setChampionList([]);
  }, []);

  useEffect(() => {

    if (questionMap.q8) {
      const sendData = async () => {
        try {
          const data = await sendQuestionMap(questionMap, username, tag);
          console.log(data);
          navigate('/new_result');
        } catch (error) {
          console.error('Error sending data:', error);
        }
      };

      sendData();
    }
  }, [questionMap, username, tag, navigate]);

  return (
    <Box
  sx={{
    maxWidth: 1400,
    margin: 'auto',
    textAlign: 'center',
    mt: 10,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: loading ? 'center' : 'flex-start', // Adjust alignment
    minHeight: '80vh', // Ensure space for spinner or content
  }}
>
  {loading ? (
    <CircularProgress color="secondary" />
  ) : (
    <Box sx={{ width: '100%' }}>
      <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          왓챔?
        </Typography>
      </Link>
      <Typography variant="subtitle1" gutterBottom>
        {username} {tag}
      </Typography>
      <Paper
        elevation={3}
        sx={{
          backgroundColor: theme.palette.primary.main,
          color: 'white',
          p: 3,
          mt: 3,
        }}
      >
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
          {positions[idx]?.en || 'Position'}
        </Typography>
        <Grid container spacing={5} justifyContent="center">
          {championList.map((champion, index) => (
            <Grid item key={index}>
              <Box
                component="img"
                mt={3}
                sx={{
                  width: 600,
                  height: 350,
                  backgroundColor: index === 2 ? '#6b1b54' : '#1e3a5f',
                  borderRadius: 2,
                  mb: 1,
                }}
                src={get_images(cNameMap[champion].en)}
                alt={champion}
              />
              <Typography variant="h5">{champion}</Typography>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  )}
</Box>
  );
}

export default NewResultPage;