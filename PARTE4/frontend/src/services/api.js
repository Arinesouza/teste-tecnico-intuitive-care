import axios from 'axios';

const isLocalhost = window.location.hostname === 'localhost';

const api = axios.create({
  baseURL: isLocalhost ? 'http://localhost:8000/api' : '/api',
});

export default api;