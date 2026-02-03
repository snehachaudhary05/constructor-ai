/**
 * API service for backend communication.
 */

import axios from 'axios';

// API base URL - use environment variable or default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Authentication APIs
export const authAPI = {
  getLoginURL: () => `${API_BASE_URL}/auth/login`,

  getSessionInfo: async (sessionId) => {
    const response = await api.get(`/auth/session/${sessionId}`);
    return response.data;
  },

  logout: async (sessionId) => {
    const response = await api.post('/auth/logout', { session_id: sessionId });
    return response.data;
  },
};

// Chatbot APIs
export const chatbotAPI = {
  sendMessage: async (sessionId, message) => {
    const response = await api.post('/chatbot/message', {
      session_id: sessionId,
      message: message,
    });
    return response.data;
  },

  getWelcomeMessage: async (sessionId) => {
    const response = await api.get(`/chatbot/welcome/${sessionId}`);
    return response.data;
  },
};

// Email APIs
export const emailAPI = {
  generateReply: async (sessionId, emailId) => {
    const response = await api.post('/email/generate-reply', null, {
      params: { session_id: sessionId, email_id: emailId },
    });
    return response.data;
  },

  sendReply: async (sessionId, emailId, replyText, originalSubject) => {
    const response = await api.post('/email/send-reply', {
      session_id: sessionId,
      email_id: emailId,
      reply_text: replyText,
      original_subject: originalSubject,
    });
    return response.data;
  },

  deleteEmail: async (sessionId, emailId) => {
    const response = await api.post('/email/delete', {
      session_id: sessionId,
      email_id: emailId,
    });
    return response.data;
  },

  getEmailDetails: async (sessionId, emailId) => {
    const response = await api.get(`/email/details/${emailId}`, {
      params: { session_id: sessionId },
    });
    return response.data;
  },
};

export default api;
