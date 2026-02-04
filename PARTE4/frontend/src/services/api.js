import axios from "axios";

export const api = axios.create({
// No seu service de API do Frontend
  baseURL: window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : '/api'});
