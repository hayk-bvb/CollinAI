import axios from 'axios';

export const api = axios.create({
  // TODO: Add a env variable of the baseURL here instead of defining it literally
  baseURL: 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sendMessage = async (message, sessionID) => {
  const response = await api.post('/api/chat', { message, sessionID });
  console.log(response.data);
  return response.data; // e.g. { reply: "...", id: 123 }
};