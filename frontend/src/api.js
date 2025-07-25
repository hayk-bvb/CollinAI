import axios from 'axios';

console.log("Hello World");
const api = axios.create({
  // TODO: Add a env variable of the baseURL here instead of defining it literally
  baseURL: 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sendMessage = async (message) => {
  console.log(api.baseURL);
  console.log("Sending to: ", api.defaults.baseURL + '/api/chat');
  const response = await api.post('/api/chat', { message });
  console.log(response.data);
  return response.data; // e.g. { reply: "...", id: 123 }
};