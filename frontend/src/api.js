import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sendMessage = async (message) => {
  const response = await api.post('/chat', { message });
  return response.data; // e.g. { reply: "...", id: 123 }
};