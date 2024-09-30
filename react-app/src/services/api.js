import axios from 'axios';

// Create an axios instance with the base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
});

// Request interceptor to log the request details
api.interceptors.request.use(
  (config) => {
    // Log the request details
    console.log('Starting API Request', {
      method: config.method.toUpperCase(),
      url: `${config.baseURL}${config.url}`,
      headers: config.headers,
      data: config.data,
    });

    return config;
  },
  (error) => {
    // Log the error before the request is sent
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to log the response details
api.interceptors.response.use(
  (response) => {
    // Log the response details
    console.log('Response:', {
      status: response.status,
      statusText: response.statusText,
      url: response.config.url,
      data: response.data,
    });

    return response;
  },
  (error) => {
    // Log the error details
    console.error('API call failed:', {
      message: error.message,
      url: error.config?.url,
      method: error.config?.method,
      headers: error.config?.headers,
      data: error.config?.data,
      response: error.response,
    });

    return Promise.reject(error); // Ensure the promise is rejected
  }
);

export default api;