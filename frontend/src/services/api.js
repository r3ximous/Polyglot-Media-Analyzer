import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// File upload service
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/media/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Get processing status
export const getProcessingStatus = async (fileId) => {
  const response = await api.get(`/media/status/${fileId}`);
  return response.data;
};

// Get transcription
export const getTranscription = async (fileId) => {
  const response = await api.get(`/media/transcription/${fileId}`);
  return response.data;
};

// Get translation
export const translateContent = async (fileId, translationData) => {
  const response = await api.post(`/media/translate/${fileId}`, translationData);
  return response.data;
};

// Get summary
export const getSummary = async (fileId) => {
  const response = await api.get(`/media/summary/${fileId}`);
  return response.data;
};

// Get sentiment analysis
export const getSentimentAnalysis = async (fileId) => {
  const response = await api.get(`/media/sentiment/${fileId}`);
  return response.data;
};

// Get object detection
export const getObjectDetection = async (fileId) => {
  const response = await api.get(`/media/objects/${fileId}`);
  return response.data;
};

// Create highlight reel
export const createHighlightReel = async (fileId, segments) => {
  const response = await api.post(`/media/highlight/${fileId}`, { segments });
  return response.data;
};

// Search content
export const searchContent = async (query, filters = {}, size = 10) => {
  const params = new URLSearchParams();
  params.append('q', query);
  params.append('size', size);
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.append(key, value);
    }
  });
  
  const response = await api.get(`/search/search?${params}`);
  return response.data;
};

// Get analytics overview
export const getAnalyticsOverview = async () => {
  const response = await api.get('/search/analytics/overview');
  return response.data;
};

export default api;