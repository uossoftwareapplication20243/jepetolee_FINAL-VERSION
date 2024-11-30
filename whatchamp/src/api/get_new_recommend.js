import { server_url } from '../const/url';

export const getNewRecommend = async (questionMap, username, tag) => {
    //TODO URL 수정해야하지 않나
    const url = server_url + `/api/answers/${username}${tag}`;
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(questionMap),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      return await response.json();
    } catch (error) {
      console.error('Error sending question map:', error);
      throw error; // Rethrow to handle in the component
    }
  };