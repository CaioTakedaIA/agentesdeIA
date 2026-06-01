import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/upload', formData);
  return data;
};

export const runPipeline = async () => {
  const { data } = await api.post('/pipeline/run');
  return data;
};

export const askQuestion = async (question) => {
  const { data } = await api.post('/ask', { question });
  return data;
};

export const getEventSource = () => {
  return new EventSource('/api/stream');
};
